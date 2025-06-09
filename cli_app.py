import uuid
import subprocess
import sys # For python executable path
from rag_module import load_llm, setup_rag_chain, ask_question_with_rag, COLLECTION_NAME, EMBEDDING_MODEL_NAME, DB_DIR
from knowledge_base import get_or_create_collection as kb_get_or_create_collection, \
                           add_document as kb_add_document, client as kb_client

# --- Global Variables ---
# Path to the model. This might be updated after fine-tuning.
# For now, it's the same as in rag_module.py, but a more robust solution
# would use a config file or environment variable.
CURRENT_MODEL_PATH_FOR_RAG = None # Will be set after LLM is loaded by rag_module's functions

# Initialize components for RAG
# We need to load the LLM and set up the RAG chain once when the CLI app starts.
print("Initialisation du LLM et de la chaîne RAG...")
llm = load_llm()
# Note: The collection for RAG is implicitly handled by Chroma vector store in setup_rag_chain
rag_chain = setup_rag_chain(llm, COLLECTION_NAME, EMBEDDING_MODEL_NAME)
print("Initialisation terminée.")

# Get the ChromaDB collection for adding documents (using knowledge_base functions)
# This uses the client from knowledge_base.py
try:
    knowledge_collection = kb_get_or_create_collection(COLLECTION_NAME)
except Exception as e:
    print(f"Erreur lors de l'initialisation de la collection ChromaDB via knowledge_base: {e}")
    print("Veuillez vérifier la configuration de ChromaDB.")
    exit()

def display_menu():
    """Displays the main menu."""
    print("\n--- Interface CLI RAG ---")
    print("Choisissez une option:")
    print("1. Poser une question")
    print("2. Ajouter une connaissance (ChromaDB)")
    print("3. Fournir des données pour l'apprentissage (fichier learning_data.txt)")
    print("4. Mettre à jour le modèle avec les nouvelles données (fine-tuning)")
    print("5. Quitter")

def handle_trigger_fine_tuning():
    """Handles triggering the fine-tuning script."""
    print("\nLancement du script de fine-tuning (fine_tune_model.py)...")
    print("Cela peut prendre beaucoup de temps, surtout sur CPU.")
    print("Surveillez la console pour la sortie du script de fine-tuning.")
    try:
        # Ensure using the same Python interpreter that runs cli_app.py
        process_result = subprocess.run([sys.executable, "fine_tune_model.py"], capture_output=False, text=False, check=False)
        if process_result.returncode == 0:
            print("Le script de fine-tuning semble s'être terminé avec succès.")
            print("IMPORTANT: Pour utiliser le modèle fine-tuné, vous devez MANUELLEMENT")
            print(f"mettre à jour le chemin du modèle dans 'rag_module.py' vers './tinyllama_finetuned'")
            print("et redémarrer cette application CLI.")
        else:
            print("ERREUR: Le script de fine-tuning s'est terminé avec un code d'erreur.")
            print(f"Code de retour: {process_result.returncode}")
            # stderr_output = process_result.stderr.decode('utf-8', errors='replace') if process_result.stderr else "Aucune sortie d'erreur capturée."
            # print(f"Erreur:\n{stderr_output}")
            print("Veuillez vérifier la sortie de la console pour plus de détails sur l'erreur.")

    except FileNotFoundError:
        print("ERREUR: Le script 'fine_tune_model.py' est introuvable. Assurez-vous qu'il est dans le même répertoire.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors du lancement du fine-tuning: {e}")

def handle_provide_learning_data():
    """Handles providing data for learning."""
    learning_text = input("Veuillez saisir le texte à apprendre (une phrase ou un petit paragraphe): ")
    if not learning_text.strip():
        print("Le texte ne peut pas être vide.")
        return
    try:
        with open("learning_data.txt", "a", encoding="utf-8") as f:
            f.write(learning_text + "\n")
        print("Données d'apprentissage ajoutées à learning_data.txt")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans learning_data.txt: {e}")

def handle_ask_question():
    """Handles the ask question functionality."""
    question = input("Veuillez saisir votre question: ")
    if not question.strip():
        print("La question ne peut pas être vide.")
        return

    print("\nTraitement de votre question...")
    answer_details = ask_question_with_rag(rag_chain, question) # rag_chain is already initialized

    print(f"\nQuestion: {question}")
    print(f"Réponse: {answer_details['result']}")
    print("Documents sources récupérés:")
    if answer_details['source_documents']:
        for doc in answer_details['source_documents']:
            doc_id = "N/A"
            if hasattr(doc, 'metadata') and doc.metadata and 'id' in doc.metadata:
                doc_id = doc.metadata['id']
            elif hasattr(doc, 'metadata') and doc.metadata and 'source' in doc.metadata: # Fallback for some cases
                 doc_id = doc.metadata['source']

            # Chroma from_documents might store ID in metadata differently or not at all without explicit setup
            # The ID might not be directly available as 'id' if not explicitly set during Chroma vector store creation in LangChain
            # For documents added via knowledge_base.py, the ID is there, but retrieval might not always pass it as 'id'.
            # This is more of a LangChain/Chroma integration detail for metadata propagation.

            print(f"  - {doc.page_content} (ID: {doc_id})") # Attempt to get ID
    else:
        print("  - Aucun document source n'a été récupéré.")

def handle_add_knowledge():
    """Handles the add knowledge functionality."""
    document_text = input("Veuillez saisir le texte de la nouvelle connaissance: ")
    if not document_text.strip():
        print("Le texte de la connaissance ne peut pas être vide.")
        return

    document_id = input("Veuillez saisir un ID unique pour ce document (ou appuyez sur Entrée pour un UUID généré): ")
    if not document_id.strip():
        document_id = str(uuid.uuid4())
        print(f"ID généré: {document_id}")

    try:
        # Use the collection obtained from knowledge_base.py's functions
        kb_add_document(knowledge_collection, document_text, document_id)
        # Note: RAG chain's retriever might need to be updated or re-initialized
        # if new documents are added frequently and need to be immediately available.
        # For this simple CLI, we assume the vector store might pick it up,
        # or a restart might be needed for immediate reflection in complex LangChain setups.
        # Chroma (if used directly by LangChain retriever) should see new docs in the same collection.
        print(f"'{document_text}' (ID: {document_id}) ajouté à la base de connaissances.")
        print("Il peut être nécessaire de redémarrer l'application pour que les nouvelles connaissances soient immédiatement prises en compte par le RAG dans certains scénarios complexes.")
    except Exception as e:
        print(f"Erreur lors de l'ajout du document: {e}")


def main_loop():
    """Main loop for the CLI application."""
    while True:
        display_menu()
        choice = input("Votre choix: ")

        if choice == '1':
            handle_ask_question()
        elif choice == '2':
            handle_add_knowledge()
        elif choice == '3':
            handle_provide_learning_data()
        elif choice == '4':
            handle_trigger_fine_tuning()
        elif choice == '5':
            print("Merci d'avoir utilisé l'application. Au revoir!")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    # Set the global CURRENT_MODEL_PATH_FOR_RAG, though it's not dynamically used yet for reloading.
    # This is more of a placeholder for future dynamic loading.
    # The actual model path is hardcoded in rag_module.py for now.
    CURRENT_MODEL_PATH_FOR_RAG = rag_module.MODEL_NAME # or the fine-tuned path if implemented dynamically
    # Ensure the default documents from knowledge_base.py are present if the collection was just created.
    # This is a bit redundant if rag_module.py already did this, but ensures they exist for the CLI.
    # For simplicity, we rely on the fact that knowledge_base.py's add_document (via rag_module)
    # or direct calls would populate it. Here, we just ensure the collection exists.
    # The `add_documents_if_not_exist` from `rag_module.py` could be called here if needed,
    # but `knowledge_collection` from `kb_get_or_create_collection` should point to the same one.

    # Let's ensure some base documents are there if the collection is empty.
    # This is a simplified check.
    if knowledge_collection.count() == 0:
        print("La collection est vide. Ajout des documents initiaux de knowledge_base.py...")
        from knowledge_base import add_document as kb_add_doc_direct # avoid conflict
        documents_to_add = {
            "doc1": "Le ciel est bleu.",
            "doc2": "L'herbe est verte.",
            "doc3": "Paris est la capitale de la France.",
            "doc4": "Les pommes sont généralement rouges ou vertes.",
            "doc5": "Le soleil brille pendant la journée."
        }
        for doc_id, text in documents_to_add.items():
            try:
                # Check if doc_id exists before adding
                if not knowledge_collection.get(ids=[doc_id])['ids']:
                     kb_add_doc_direct(knowledge_collection, text, doc_id)
            except Exception as e:
                print(f"Skipping initial doc add for {doc_id} due to: {e}") # Might already exist from another run

    main_loop()
