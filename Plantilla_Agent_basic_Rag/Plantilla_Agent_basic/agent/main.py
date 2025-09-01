# main.py
from dotenv import load_dotenv
import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from .rag.atlas_retriever import AtlasRetriever

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.memory.mongodb_memory import MongoMemory

# Asegúrate de que las variables de entorno se carguen correctamente
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Verifica si las variables se cargaron
if not GOOGLE_API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY no está configurada.")
if not MONGO_URI:
    raise ValueError("Error: MONGO_URI no está configurada.")

# Instanciamos el modelo de lenguaje de Google
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-thinking-exp-01-21",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2,
    top_p=0.9
)

# Instanciamos la memoria para la conversación
memory_db = MongoMemory(mongo_uri=MONGO_URI, db_name="Criker") # Puedes ajustar el nombre de la BD si lo deseas

# --- ¡CORRECCIÓN AQUÍ! ---
# Instanciamos el retriever UNA SOLA VEZ, conectándolo a MongoDB Atlas.
# Los nombres de la BD y la colección deben coincidir con los que usaste en create_embeddings.py
rag_retriever = AtlasRetriever(
    api_key=GOOGLE_API_KEY, 
    db_uri=MONGO_URI,
    db_name="Criker",        # <- ¡Tu base de datos!
    collection_name="my_embeddings"  # <- ¡Tu colección!
)

def load_prompt_base() -> str:
    prompt_file = os.path.join(
        os.path.dirname(__file__),
        "prompt_templates",
        "escenarioGeneral2.py"
    )
    with open(prompt_file, "r", encoding="utf-8") as file:
        return file.read()

def build_context(history) -> str:
    conversation_str = ""
    for entry in history:
        if entry["role"] == "user":
            conversation_str += f"Usuario: {entry['message']}\n"
        else:
            conversation_str += f"Agente: {entry['message']}\n"
    return conversation_str

def process_message(user_id: str, user_message: str) -> str:
    # 1. RAG: Buscar la información relevante en el libro
    retrieved_docs = rag_retriever.retrieve(user_message, k=3)
    context_libro = "\n\n".join(retrieved_docs)

    if not context_libro:
        context_libro = "No se ha encontrado información relevante en la base de conocimiento para esta consulta."
    
    # 2. Recuperar historial de conversación
    history = memory_db.get_conversation(user_id)
    context_historial = build_context(history)
    prompt_base = load_prompt_base()
    
    # 3. Construir el prompt final
    is_first_message = len(history) == 0
    final_prompt = (
        f"{prompt_base}\n\n"
        f"Contexto del libro:\n{context_libro}\n\n"
        f"{'Este es el primer mensaje del usuario.' if is_first_message else 'Esta es una conversación en curso.'}\n"
        f"Historial de conversación:\n{context_historial}"
        f"Usuario: {user_message}\n"
        "Agente:"
    )

    # Invocar al modelo
    response = llm.invoke(final_prompt)
    
    # Limpiar la respuesta de marcadores Markdown
    clean_response = response.content.strip('`').replace('```', '').strip()

    # Guardar conversación en memoria
    memory_db.save_message(user_id, "user", user_message)
    memory_db.save_message(user_id, "agent", clean_response) # <-- Mejor guardar la respuesta limpia

    return clean_response

def main_cli():
    print("¡Bienvenido al Agente IA!")
    print("Escribe 'salir' para terminar la conversación")

    # Restaurado a la lógica de pedir el ID de usuario
    user_id = input("Ingrese su ID de usuario: ")
    while True:
        user_input = input("\nTú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break

        answer = process_message(user_id, user_input)
        print(f"\nAgente: {answer}")

if __name__ == "__main__":
    main_cli()