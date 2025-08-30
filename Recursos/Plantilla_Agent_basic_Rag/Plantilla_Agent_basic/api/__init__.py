# api/api.py
from fastapi import FastAPI, Request
from agent.main import process_message

app = FastAPI()

@app.post("/preguntas")
async def chat_endpoint(request: Request):
    """
    Endpoint que recibe una petición POST con un JSON que contenga el mensaje del usuario.
    Ejemplo de payload: { "message": "¿Cómo estás?" }
    """
    data = await request.json()
    user_message = data.get("message", "")
    response = process_message(user_message)
    return {"response": response}
