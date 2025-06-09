import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline as hf_pipeline

from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Functions from knowledge_base.py (simplified for direct use here)
import chromadb
import os

DB_DIR = "chroma_db_store"
COLLECTION_NAME = "llm_knowledge"

def initialize_and_get_collection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    persistent_client = chromadb.PersistentClient(path=DB_DIR)
    try:
        collection = persistent_client.get_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' retrieved.")
    except:
        collection = persistent_client.create_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' created.")
    return collection

def add_documents_if_not_exist(collection):
    documents_to_add = {
        "doc1": "Le ciel est bleu.",
        "doc2": "L'herbe est verte.",
        "doc3": "Paris est la capitale de la France.",
        "doc4": "Les pommes sont généralement rouges ou vertes.",
        "doc5": "Le soleil brille pendant la journée."
    }
    existing_ids = collection.get(ids=list(documents_to_add.keys()))['ids']
    added_new = False
    for doc_id, text in documents_to_add.items():
        if doc_id not in existing_ids:
            collection.add(documents=[text], ids=[doc_id])
            print(f"Document ID '{doc_id}' added to collection '{collection.name}'.")
            added_new = True
    if not added_new and existing_ids:
        print("All documents already exist in the collection.")

# --- RAG Module specific code ---

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" # Chroma's default

def load_llm():
    print(f"Loading LLM: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16, # Using float16 for potentially lower memory
        device_map="auto" # Let accelerate handle device mapping
    )
    # Ensure pad_token_id is set if eos_token_id is used for padding
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    pipe = hf_pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=150, # Max tokens to generate
        #temperature=0.7,
        #top_k=50,
        #do_sample=True
    )
    return HuggingFacePipeline(pipeline=pipe)

def setup_rag_chain(llm, collection_name, embedding_model_name):
    print(f"Setting up RAG chain with embedding model: {embedding_model_name}")
    # Configure embeddings
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    # Configure vector store retriever from existing ChromaDB
    vector_store = Chroma(
        client=chromadb.PersistentClient(path=DB_DIR),
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 2}) # Retrieve top 2 documents

    # Define the prompt template
    template = """
    Utilisez les informations suivantes issues de la base de connaissances pour répondre à la question. Si vous ne connaissez pas la réponse ou que l'information n'est pas présente, dites simplement que vous ne savez pas. Ne faites pas d'hypothèses.

    Contexte: {context}

    Question: {question}

    Réponse utile:"""
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff", # Uses all retrieved text chunks in the context
        retriever=retriever,
        return_source_documents=True, # Optionally return source documents
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

def ask_question_with_rag(chain, question: str):
    print(f"\nProcessing RAG question: {question}")
    result = chain.invoke({"query": question}) # Using invoke and query for RetrievalQA
    return result

if __name__ == "__main__":
    # 1. Ensure ChromaDB has documents
    chroma_collection = initialize_and_get_collection()
    add_documents_if_not_exist(chroma_collection)

    # 2. Load LLM
    llm = load_llm()

    # 3. Setup RAG chain
    rag_chain = setup_rag_chain(llm, COLLECTION_NAME, EMBEDDING_MODEL_NAME)

    # 4. Ask questions
    questions = [
        "Quelle est la couleur du ciel ?",
        "Quelle est la capitale de la France ?",
        "Parle-moi des pommes.",
        "Quelle est la couleur de l'océan ?" # This info is not in KB
    ]

    for q in questions:
        answer_details = ask_question_with_rag(rag_chain, q)
        print(f"Question: {q}")
        print(f"Réponse: {answer_details['result']}")
        print("Documents sources récupérés:")
        for doc in answer_details['source_documents']:
            print(f"  - {doc.page_content} (ID: {doc.metadata.get('id', 'N/A') if hasattr(doc, 'metadata') and doc.metadata else 'N/A'})")
        print("-" * 30)

    print("\nRAG module execution finished.")
