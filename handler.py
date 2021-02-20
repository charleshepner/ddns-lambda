import base64
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ddns_username = os.environ.get("DDNS_USERNAME")
ddns_password = os.environ.get("DDNS_PASSWORD")

def ddns_lambda(event, context):
    logger.debug(event)

    try:
        response = process_request(event)
    except Exception as e:
        logger.error(repr(e))
        response = format_response(500, "911")

    return response


def process_request(event):
    allow_access = False
    headers = event.get('headers')
    querystrings = event.get("queryStringParameters")

    if headers:
        useragent = headers.get("User-Agent")
        if not useragent or useragent == "Amazon CloudFront": 
            return format_response(400, "badagent")

        auth = headers.get("Authorization")
        if auth:
            allow_access = check_credentials(auth)

    if not allow_access:
        return format_response(403, "badauth")

    if allow_access and querystrings:
        logger.info(querystrings.get("hostname"))
        logger.info(querystrings.get("myip"))
        return format_response(200, "good")
    else:
        return format_response(500, "911")


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
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": message
    }

