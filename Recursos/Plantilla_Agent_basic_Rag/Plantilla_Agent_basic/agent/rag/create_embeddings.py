# create_embeddings.py
# rag/create_embeddings.py
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pymongo import MongoClient

def create_and_save_embeddings(libro_path: str, db_uri: str):
    """
    Carga un archivo PDF, lo divide en chunks, crea embeddings y los guarda
    en una colección de MongoDB.
    """
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not google_api_key:
        print("Error: La variable de entorno 'GOOGLE_API_KEY' no está configurada.")
        return

    print("--- 1. Cargando el libro ---")
    try:
        loader = PyPDFLoader(libro_path)
        docs = loader.load()
    except Exception as e:
        print(f"Error al cargar el libro: {e}")
        return

    print("--- 2. Dividiendo el libro en chunks ---")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Total de chunks creados: {len(chunks)}")
    
    print("--- 3. Creando los embeddings ---")
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=google_api_key
    )
    
    documents_to_insert = []
    for chunk in chunks:
        embedding = embedding_model.embed_query(chunk.page_content)
        documents_to_insert.append({
            "content": chunk.page_content,
            "embedding": embedding
        })

    print("--- 4. Conectando a MongoDB Atlas y guardando los embeddings ---")
    try:
        client = MongoClient(db_uri)
        db = client["Criker"]
        collection = db["my_embeddings"]
        
        collection.delete_many({})
        collection.insert_many(documents_to_insert)
        
        print(f"Embeddings guardados en la colección 'my_embeddings' con éxito.")
        
    except Exception as e:
        print(f"Error al conectar con MongoDB o al guardar los datos: {e}")

if __name__ == "__main__":
    load_dotenv()
    mongodb_uri = os.getenv("MONGO_URI")
    libro_pdf_path = "data/mi_libro.pdf"

    if not mongodb_uri:
        print("Error: La variable de entorno 'MONGO_URI' no está configurada.")
    elif not os.path.exists(libro_pdf_path):
        print(f"\nError: El archivo '{libro_pdf_path}' no se encuentra.")
    else:
        create_and_save_embeddings(libro_pdf_path, mongodb_uri)