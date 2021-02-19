import base64
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddns_username = os.environ.get("DDNS_USERNAME")
ddns_password = os.environ.get("DDNS_PASSWORD")

def ddns_lambda(event, context):
    logger.debug(event)

    allow_access = False
    headers = event.get('headers')
    if headers:
        auth = headers.get("Authorization")
        if auth:
            allow_access = check_credentials(auth)

    if not allow_access:
        response = format_response(401, "Unauthorized")

    if allow_access:
        querystrings = event.get("queryStringParameters")
        if querystrings:
            logger.info(querystrings.get("hostname"))
            logger.info(querystrings.get("myip"))

        response = format_response(200, "Congrats! You're authorized.")

    return response


def check_credentials(authorization_header):
    try:
        base64_authentication_string = authorization_header.replace("Basic ", "")
        authentication_string = base64.b64decode(base64_authentication_string).decode("utf-8")
        provided_username, provided_password = tuple(authentication_string.split(":"))
        if provided_username == ddns_username and provided_password == ddns_password:
            logger.info(f"{provided_username} logged in.")
            return True
        else:
            logger.info(f"{provided_username} failed login.")

    except Exception as ex:
        logger.error(repr(ex))
        return False

    return False

def format_response(status, message):
    return {
        "statusCode": status,
        "body": json.dumps({"status": status, "message": message })
    }

