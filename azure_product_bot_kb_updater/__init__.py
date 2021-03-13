import logging
import os, http.client, urllib.parse, json, time

import azure.functions as func
from ..com.QnA_brute_force import QnABruteForce


KB_SUBSCRIPTION_KEY = ''
KB_ID = ''

HOST = 'westus.api.cognitive.microsoft.com'
SERVICE = '/qnamaker/v4.0'
METHOD = '/knowledgebases/'


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    #### Function Code goes here #### ------------------------------------------------------------

    #    _load_env_vars()
    KB_SUBSCRIPTION_KEY = os.environ["KB_SUBSCRIPTION_KEY"]
    logging.info(f'Loaded KB Subscription Key: {KB_SUBSCRIPTION_KEY}')

    KB_ID = os.environ['KB_ID']
    logging.info(f'Loaded KB ID: {KB_ID}')

    qna = QnABruteForce()
    #req = {'qnaList':[]}
    req = {'qnaList': qna.qna()}

    path = SERVICE + METHOD + KB_ID
    content = json.dumps(req)
    # Replaces knowledge base
    logging.debug(pretty_print(content))
    result = replace_kb(path, content, KB_SUBSCRIPTION_KEY)
    # Print request response in JSON with presentable formatting.
    logging.info(pretty_print(result))

    #### End Function Code #### ------------------------------------------------------------------

    if name:
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )


def _load_env_vars():
    # Replace this with a valid subscription key.

    KB_SUBSCRIPTION_KEY = os.environ["KB_SUBSCRIPTION_KEY"]
    logging.info(f'Loaded KB Subscription Key: {KB_SUBSCRIPTION_KEY}')

    KB_ID = os.environ['KB_ID']
    logging.info(f'Loaded KB ID: {KB_ID}')

    # endpoint = 'https://azure-product-bot.cognitiveservices.azure.com/'


'''
Formats and indents JSON for display.
:param content: The JSON to format and indent.
:type: string
:return: Formatted and indented JSON.
:rtype: string
'''


def pretty_print(content):
    # Note: We convert content to and from an object so we can pretty-print it.
    return json.dumps(json.loads(content), indent=4)


'''
Sends a PUT HTTP request, to replace the knowledge base.
:param path: The URL path of your request.
:param content: The contents of your PUT request.
:type: string
:return: Status of PUT request in replacing the kb.
:rtype: HTTPResponse
'''


def replace_kb(path, content, subscriptionKey):
    logging.info ('Calling ' + HOST + path + '.')
    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-Type': 'application/json',
        'Content-Length': len(content)
    }
    conn = http.client.HTTPSConnection(HOST)
    conn.request("PUT", path, content, headers)
    response = conn.getresponse()

    if response.status == 204:
        return json.dumps({'result': 'Success.'})
    else:
        return response.read()
