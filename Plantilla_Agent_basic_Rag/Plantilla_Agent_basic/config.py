# Este archivo contiene la configuración de la base de datos y las credenciales de la API de Google.
# Asegúrate de no compartir este archivo públicamente, ya que contiene información sensible.

#Asegurate de ejcutar python config.py para verificar que la conexión a la base de datos es correcta antes de ejecutar el resto del código.
import os
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://zidanypalomino2:iQFom1oiY0BnLxwD@cluster001.j8u97.mongodb.net/?retryWrites=true&w=majority&appName=Cluster001"
GOOGLE_API_KEY="AIzaSyDB1-PpJJRCdRBlO-tVN-sCU5HqcRgr5lU"

client = MongoClient(MONGO_URI)
try:
    client.admin.command('ping')
    print("✅ Conexión exitosa a MongoDB")
except Exception as e:
    print("❌ Error conectando a MongoDB:", e)