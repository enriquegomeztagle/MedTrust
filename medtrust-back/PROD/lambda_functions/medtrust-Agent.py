import os
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BEDROCK_REGION = os.getenv("BEDROCK_REGION")
client = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)


def lambda_handler(event, context):
    logger.info("Evento recibido: %s", json.dumps(event, indent=2, ensure_ascii=False))

    try:
        if isinstance(event["body"], str):
            body = json.loads(event["body"])
        else:
            body = event["body"]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Error al procesar el cuerpo de la solicitud: %s", str(e))
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps({"error": "Invalid request body."}, ensure_ascii=False),
        }

    logger.info(
        "Cuerpo de la solicitud procesado: %s", json.dumps(body, ensure_ascii=False)
    )

    provided_token = body.get("token", "")
    valid_token = os.getenv("VALID_TOKEN")

    if provided_token != valid_token:
        logger.warning("Token inválido proporcionado: %s", provided_token)
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(
                {"error": "Unauthorized: Invalid or missing token."}, ensure_ascii=False
            ),
        }

    AGENT_ID = os.getenv("AGENT_ID")
    AGENT_ALIAS_ID = os.getenv("AGENT_ALIAS_ID")
    SESSION_ID = os.getenv("SESSION_ID")
    task = body.get("question", "")

    if not task:
        logger.warning("No se encontró 'question' en el cuerpo de la solicitud.")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(
                {"error": "No 'question' found in the request body."},
                ensure_ascii=False,
            ),
        }

    try:
        logger.info("Invocando al agente Bedrock con task: %s", task)
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=SESSION_ID,
            inputText=task,
            enableTrace=True,
            endSession=False,
        )

        logger.info("Respuesta del agente Bedrock: %s", response)

        final_response = None
        if "completion" in response:
            completion_stream = response["completion"]
            final_response = ""
            for event in completion_stream:
                if "chunk" in event and "bytes" in event["chunk"]:
                    final_response += event["chunk"]["bytes"].decode("utf-8")

        if final_response:
            logger.info("Respuesta final procesada: %s", final_response)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json; charset=utf-8"},
                "body": json.dumps({"response": final_response}, ensure_ascii=False),
            }

        logger.warning("No se encontró respuesta final en el flujo de eventos.")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(
                {"response": "No final response found in the event stream."},
                ensure_ascii=False,
            ),
        }

    except boto3.exceptions.Boto3Error as e:
        logger.error("Error al invocar al agente Bedrock: %s", str(e))
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "body": json.dumps(
                {"error": f"Error invoking agent: {str(e)}"}, ensure_ascii=False
            ),
        }
