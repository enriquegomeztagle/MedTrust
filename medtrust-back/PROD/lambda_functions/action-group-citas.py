import json
import logging
import random
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Evento recibido: %s", json.dumps(event, indent=2, ensure_ascii=False))

    function_name = event.get("function", "unknown_function")

    if function_name == "consultarCita":
        return consultar_cita(event)
    elif function_name == "generarCita":
        return generar_cita(event)
    else:
        return {
            "statusCode": 400,
            "body": "Error: Función desconocida '%s'." % function_name,
        }


def consultar_cita(event):
    try:
        numeroCita = next(
            param["value"]
            for param in event.get("parameters", [])
            if param["name"] == "numeroCita"
        )
        logger.info("Número de cita recibido: %s", numeroCita)
    except StopIteration:
        return {
            "statusCode": 400,
            "body": 'Error: Parámetro "numeroCita" no encontrado en la solicitud.',
        }

    if numeroCita == "1234":
        dummy_info = {
            "numeroCita": 1234,
            "estadoCita": "Confirmada",
            "fechaCita": "2024-12-15",
            "horaCita": "09:30:00",
            "motivo": "Consulta general",
            "detalles": "Servicio estándar",
            "creadaEn": "2024-11-20 08:10:46",
        }
        logger.info(
            "Información dummy devuelta: %s",
            json.dumps(dummy_info, indent=2, ensure_ascii=False),
        )
    else:
        dummy_info = {
            "estadoCita": "No encontrada",
            "mensaje": "El número de cita proporcionado no corresponde a ninguna cita registrada.",
        }
        logger.info(
            "Información para cita no encontrada: %s",
            json.dumps(dummy_info, indent=2, ensure_ascii=False),
        )

    responseBody = {
        "TEXT": {
            "body": "Información de la cita: %s"
            % json.dumps(dummy_info, ensure_ascii=False)
        }
    }

    return construir_respuesta(event, responseBody)


def generar_cita(event):
    try:
        nombrePaciente = next(
            param["value"]
            for param in event.get("parameters", [])
            if param["name"] == "nombrePaciente"
        )
        telefono = next(
            param["value"]
            for param in event.get("parameters", [])
            if param["name"] == "telefono"
        )
        fechaCita = next(
            param["value"]
            for param in event.get("parameters", [])
            if param["name"] == "fechaCita"
        )
        horaCita = next(
            param["value"]
            for param in event.get("parameters", [])
            if param["name"] == "horaCita"
        )
        motivo = next(
            param["value"]
            for param in event.get("parameters", [])
            if param["name"] == "motivo"
        )

        logger.info(
            "Datos recibidos: nombrePaciente=%s, telefono=%s, fechaCita=%s, horaCita=%s, motivo=%s",
            nombrePaciente,
            telefono,
            fechaCita,
            horaCita,
            motivo,
        )

    except StopIteration:
        return {
            "statusCode": 400,
            "body": "Error: Faltan uno o más parámetros obligatorios.",
        }

    numeroCita = random.randint(1000, 9999)

    cita_info = {
        "numeroCita": numeroCita,
        "estadoCita": "Pendiente de aprobación",
        "nombrePaciente": nombrePaciente,
        "telefono": telefono,
        "fechaCita": fechaCita,
        "horaCita": horaCita,
        "motivo": motivo,
        "creadaEn": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    logger.info("Cita creada: %s", json.dumps(cita_info, indent=2, ensure_ascii=False))

    mensaje_adicional = "La cita ha sido creada exitosamente y está pendiente de aprobación por un médico."

    responseBody = {
        "TEXT": {
            "body": "Cita creada exitosamente: %s\n\n%s"
            % (json.dumps(cita_info, ensure_ascii=False), mensaje_adicional)
        }
    }

    return construir_respuesta(event, responseBody)


def construir_respuesta(event, responseBody):
    action_response = {
        "actionGroup": event.get("actionGroup", "unknown_actionGroup"),
        "function": event.get("function", "unknown_function"),
        "functionResponse": {"responseBody": responseBody},
    }

    dummy_function_response = {
        "response": action_response,
        "messageVersion": event.get("messageVersion", "1.0"),
    }

    logger.info(
        "Respuesta final: %s",
        json.dumps(dummy_function_response, indent=2, ensure_ascii=False),
    )

    return dummy_function_response
