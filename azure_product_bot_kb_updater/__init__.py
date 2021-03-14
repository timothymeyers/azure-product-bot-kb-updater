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

    path = SERVICE + METHOD + KB_ID

    #method = '/knowledgebases/{0}/{1}/qna/'.format(KB_ID, 'test');
    #path = SERVICE + method

    # Download the KB - no longer necessary?
    
    result = get_qna(path, KB_SUBSCRIPTION_KEY)
    result_json = json.loads(result)
    num_answers = len(result_json['qnaDocuments'])
    logging.info("download - " + str(num_answers))

    my_list = [i['id'] for i in result_json['qnaDocuments']]
    
    logging.debug (my_list)    
    

    ## Delete all QnA Brute Force data

    #req = {'delete': {'sources': ['QnA Brute Force']}}
    req = {'delete': {'ids': my_list}}
    content = json.dumps(req)
    operation, result = update_kb(path, content, KB_SUBSCRIPTION_KEY)

    '''
    Iteratively gets the operation state, updating the knowledge base.
    Once state is no longer "Running" or "NotStarted", the loop ends.
    '''
    done = False
    while False == done:
        path = SERVICE + operation
        # Gets the status of the operation.
        wait, status = check_status(path, KB_SUBSCRIPTION_KEY)
        # Print status checks in JSON with presentable formatting
        logging.info (pretty_print(status))

        wait = 30

        # Convert the JSON response into an object and get the value of the operationState field.
        state = json.loads(status)['operationState']
        # If the operation isn't finished, wait and query again.
        if state == 'Running' or state == 'NotStarted':
            logging.info ('Waiting ' + str(wait) + ' seconds...')
            time.sleep (int(wait))
        else:
            done = True # request has been processed, if successful, knowledge base is updated
    '''
    '''
    path = SERVICE + METHOD + KB_ID
    qna = QnABruteForce()
    req = {'qnaList': qna.qna()}

    content = json.dumps(req)
    
    # Replaces knowledge base
    logging.debug(pretty_print(content))
    result = replace_kb(path, content, KB_SUBSCRIPTION_KEY)
    logging.info("replace_db - " + pretty_print(result))

    result = publish_kb(path, '', KB_SUBSCRIPTION_KEY)
    logging.info("publish_db - " + pretty_print(result))

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
    return json.dumps(json.loads(content), indent=2)


'''
Sends a PUT HTTP request, to replace the knowledge base.
:param path: The URL path of your request.
:param content: The contents of your PUT request.
:type: string
:return: Status of PUT request in replacing the kb.
:rtype: HTTPResponse
'''


def replace_kb(path, content, subscriptionKey):
    logging.info('Calling [replace_kb] ' + HOST + path + '.')
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


'''
Sends a POST HTTP request.
:param path: The URL path of your request.
:param content: The contents of your POST request.
:type: string
:return: Status of POST request in publishing the kb.
:rtype: string
'''


def publish_kb(path, content, subscriptionKey):
    logging.info('Calling [publish_kb] ' + HOST + path + '.')
    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-Type': 'application/json',
        'Content-Length': len(content)
    }
    conn = http.client.HTTPSConnection(HOST)
    conn.request("POST", path, content, headers)
    response = conn.getresponse()

    if response.status == 204:
        return json.dumps({'result': 'Success.'})
    else:
        return response.read()


'''
Sends a GET HTTP request.
:param path: The URL path of your request.
:type: string
:return: The downloaded knowledge base.
:rtype: string
'''


def get_qna(path, subscriptionKey):
    path = path + '/test/qna/'
    logging.info ('Calling [get_qna] ' + HOST + path + '.')
    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
    }
    conn = http.client.HTTPSConnection(HOST)
    conn.request("GET", path, '', headers)
    response = conn.getresponse()
    return response.read()


def update_kb(path, content, subscriptionKey):
    logging.info ('Calling [update_kb] ' + HOST + path + '.')
    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-Type': 'application/json',
        'Content-Length': len(content)
    }
    conn = http.client.HTTPSConnection(HOST)
    conn.request("PATCH", path, content, headers)
    response = conn.getresponse()
    #return response.read()
    return response.getheader('Location'), response.read()

'''
Gets the status of the specified QnA Maker operation.
:param path: The URL of the request.
:type: string
:return: Header from retrying of the request (if retry is needed), response of the retry.
:rtype: string, string
'''
def check_status (path, subscriptionKey):
    logging.info ('Calling [check_status] ' + HOST + path + '.')
    headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}
    conn = http.client.HTTPSConnection(HOST)
    conn.request("GET", path, None, headers)
    response = conn.getresponse ()
    # If the operation is not finished, /operations returns an HTTP header named
    # 'Retry-After' with the number of seconds to wait before querying the operation again.
    return response.getheader('Retry-After'), response.read ()