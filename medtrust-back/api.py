from fastapi import FastAPI, Request
import boto3
import json
import logging
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir los orígenes según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)


logging.basicConfig(level=logging.INFO)


# Configurar cliente de Amazon Bedrock
cliente = boto3.client('bedrock-runtime', region_name='us-east-1')

# Función para obtener la respuesta de Amazon Bedrock usando la API de Mensajes y devolver solo el texto
def obtener_respuesta_bedrock(entrada_usuario):
    """
    Envía el mensaje del usuario a Amazon Bedrock y obtiene la respuesta del asistente.

    :param entrada_usuario: El mensaje del usuario enviado al chatbot.
    :return: El texto de la respuesta generada por el asistente.
    """
    # Registrar el mensaje que se envió
    logging.info(f"Mensaje enviado: {entrada_usuario}")
    
    # Preparar el historial de mensajes para la API de Mensajes
    mensajes_api = [
        {"role": "user", "content": entrada_usuario},  # Mensaje del usuario
    ]
    
    # Preparar el payload con los parámetros requeridos
    carga_util = {
        "messages": mensajes_api,
        "max_tokens": 2000,
        "anthropic_version": "bedrock-2023-05-31",  
    }
    
    # Convertir el payload a JSON y codificarlo como bytes
    carga_bytes = json.dumps(carga_util).encode('utf-8')
    
    try:
        respuesta = cliente.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=carga_bytes,
            accept='application/json',
            contentType='application/json'
        )
        
        # Leer y decodificar la respuesta
        cuerpo_respuesta = respuesta['body'].read().decode('utf-8')
        logging.info(f"Respuesta completa de Bedrock: {cuerpo_respuesta}")  # Registrar la respuesta completa para depuración
        json_respuesta = json.loads(cuerpo_respuesta)  # Convertir la respuesta a JSON
        
        # Extraer el contenido de texto de la respuesta del asistente
        contenido_texto = ''.join([parte['text'] for parte in json_respuesta['content'] if parte.get('type') == 'text'])
        
        # Registrar la salida obtenida
        logging.info(f"Respuesta obtenida: {contenido_texto}")
        
        return contenido_texto
    except Exception as e:
        logging.error(f"Error al invocar a Bedrock: {e}")
        return "Lo siento, hubo un problema al obtener la respuesta."

# Ruta para manejar el envío de mensajes
@app.post("/enviar-mensaje")
async def enviar_mensaje(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("mensaje", "").strip()

    # Obtener la respuesta de Amazon Bedrock
    respuesta_bedrock = obtener_respuesta_bedrock(mensaje_usuario)

    # Devolver la respuesta
    return JSONResponse(content={"respuesta": respuesta_bedrock})
