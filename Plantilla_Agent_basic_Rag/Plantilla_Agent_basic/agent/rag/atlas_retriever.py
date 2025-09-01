import os
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pymongo import MongoClient
from dotenv import load_dotenv

class AtlasRetriever:
    def __init__(self, api_key: str, db_uri: str, db_name: str, collection_name: str):
        """
        Inicializa el retriever conectándose a MongoDB y configurando el modelo de embeddings.
        """
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=api_key
        )
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        print("Conexión a MongoDB Atlas exitosa.")
        
    def retrieve(self, query: str, k: int = 3): # "k", número de documentos más relevantes a recuperar
        """
        Busca los 'k' documentos más relevantes para una consulta usando
        MongoDB Atlas Vector Search.
        """
        query_embedding = self.embedding_model.embed_query(query)
        
        
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_embedding,
                    "path": "embedding", 
                    "numCandidates": 10, # nro de chunks como posibles candidatos
                    "limit": k,
                    "index": "rag_vector_index" # index de la busqueda vectorial
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "content": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
        ]
        
        try:
            results = list(self.collection.aggregate(pipeline))
            retrieved_docs = [doc["content"] for doc in results]
            
            print("Analizando...")
            return retrieved_docs
        except Exception as e:
            print(f"Error al realizar la búsqueda en MongoDB: {e}")
            return []

# Probar conexión a mongo atlas
# if __name__ == "__main__":
#     load_dotenv()
#     google_api_key = os.getenv("GOOGLE_API_KEY")
#     mongodb_uri = os.getenv("MONGO_URI")

#     if not google_api_key or not mongodb_uri:
#         print("Asegúrate de que 'GOOGLE_API_KEY' y 'MONGO_URI' estén configuradas en tu archivo .env")
#     else:
#         retriever = AtlasRetriever(
#             google_api_key, 
#             mongodb_uri,
#             db_name="Criker",
#             collection_name="my_embeddings"
#         )
#         query = "ejemplo de consulta"
#         relevant_docs = retriever.retrieve(query)
        
#         if relevant_docs:
#             print("\nDocumentos más relevantes:")
#             for doc in relevant_docs:
#                 print("---")
#                 print(doc)