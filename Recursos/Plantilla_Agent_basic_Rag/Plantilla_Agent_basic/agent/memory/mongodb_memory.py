# agent/memory/mongodb_memory.py
from pymongo import MongoClient
import datetime

"""
        1.-Clase para manejar la memoria de la conversación utilizando MongoDB.
        2.-Esta clase se conecta a una base de datos MongoDB y permite guardar y recuperar mensajes de conversación.
        3.-Los mensajes se guardan junto con la hora en que fueron guardados.
        4.-Los mensajes se pueden recuperar por el ID del usuario, ordenados por fecha.
        5.-la funcion 'init' declara la base de datos y la coleccion a utilizar, en este caso "conversations". Asegurate de agregar el nombre de tu base de datos siguiendo el prefijo de "agent_memory_" seguido del nombre de tu agente.
        6.-el nombre de la coleccion es "conversations" por defecto, pero puedes cambiarlo si lo deseas.
        
        """

class MongoMemory:
    def __init__(self, mongo_uri: str, db_name: str = "Criker", collection_name: str = "agent_memory"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_message(self, user_id: str, role: str, message: str):
        """Guarda el mensaje junto con la hora en que se guardó."""
        data = {
            "user_id": user_id,
            "role": role,  # 'user' o 'agent'
            "message": message,
            "timestamp": datetime.datetime.utcnow()
        }
        self.collection.insert_one(data)

    def get_conversation(self, user_id: str):
        """Recupera todo el historial de la conversación para el usuario dado, ordenado por fecha."""
        return list(self.collection.find({"user_id": user_id}).sort("timestamp", 1))
