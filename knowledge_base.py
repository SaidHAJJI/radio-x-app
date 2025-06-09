import chromadb
import os

# Ensure the directory for persistent storage exists
DB_DIR = "chroma_db_store"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Initialize a persistent ChromaDB client
client = chromadb.PersistentClient(path=DB_DIR)

def get_or_create_collection(collection_name: str = "llm_knowledge"):
    """
    Retrieves an existing collection or creates it if it doesn't exist.
    """
    try:
        collection = client.get_collection(name=collection_name)
        print(f"Collection '{collection_name}' retrieved.")
    except:
        collection = client.create_collection(name=collection_name)
        print(f"Collection '{collection_name}' created.")
    return collection

def add_document(collection, document_text: str, document_id: str):
    """
    Adds a document text to the specified collection with a unique ID.
    """
    collection.add(
        documents=[document_text],
        ids=[document_id]
    )
    print(f"Document ID '{document_id}' added to collection '{collection.name}'.")

def query_documents(collection, query_text: str, n_results: int = 2):
    """
    Queries the collection with a text and returns the n_results most similar documents.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results

if __name__ == "__main__":
    # Get or create the collection
    knowledge_collection = get_or_create_collection()

    # Add some example documents
    documents_to_add = {
        "doc1": "Le ciel est bleu.",
        "doc2": "L'herbe est verte.",
        "doc3": "Paris est la capitale de la France.",
        "doc4": "Les pommes sont généralement rouges ou vertes.",
        "doc5": "Le soleil brille pendant la journée."
    }

    # Check existing documents to avoid adding duplicates if script is run multiple times
    existing_ids = knowledge_collection.get(ids=list(documents_to_add.keys()))['ids']

    for doc_id, text in documents_to_add.items():
        if doc_id not in existing_ids:
            add_document(knowledge_collection, text, doc_id)
        else:
            print(f"Document ID '{doc_id}' already exists in collection '{knowledge_collection.name}'.")

    # Perform an example query
    query = "Quelle est la couleur du ciel ?"
    print(f"\nQuerying for: '{query}'")
    query_results = query_documents(knowledge_collection, query, n_results=2)

    print("\nQuery Results:")
    if query_results and query_results['documents']:
        for i, doc in enumerate(query_results['documents'][0]):
            print(f"Result {i+1}: {doc} (ID: {query_results['ids'][0][i]}, Distance: {query_results['distances'][0][i]})")
    else:
        print("No results found.")

    # Another example query
    query2 = "Capitale France"
    print(f"\nQuerying for: '{query2}'")
    query_results2 = query_documents(knowledge_collection, query2, n_results=1)

    print("\nQuery Results:")
    if query_results2 and query_results2['documents']:
        for i, doc in enumerate(query_results2['documents'][0]):
            print(f"Result {i+1}: {doc} (ID: {query_results2['ids'][0][i]}, Distance: {query_results2['distances'][0][i]})")
    else:
        print("No results found.")
