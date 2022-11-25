import json
import jsonschema
from flask import Flask, request, Response
import Rts
app = Flask(__name__)


@app.route('/api/data', methods=['POST'])
def index():

    # Check client request header is json
    if request.is_json == False:
        return Response("{'Error':'Only json data is allowed'}", status=400, mimetype='application/json')
    
    # Validate client request json scheme
    
    try:
        schema = {"type" : "object","properties" : {"url" : {"type" : "string"}}}
        jsonschema.validate(request.get_json(), schema)
    except jsonschema.exceptions.ValidationError:
        return Response("{'Error':'Bad Json scheme'}", status=400, mimetype='application/json')

    # Check if client request json key is vaild
    client_req = request.get_json()
    if list(client_req.keys())[0] != "url":
        return Response("{'Error':'url key was not found in json'}", status=400, mimetype='application/json')

    # Check if the desired request was successful
    request_obj = Rts.request(client_req['url'])
    if request_obj == ('', ''):
        return Response("{'Error':'Requested URL was not found'}", status=404, mimetype='application/json')

    request_html, request_time = request_obj
    extracted_urls = Rts.extract(request_html)
    extracted_urls['time'] = int(request_time.microseconds) / 1000
    client_answer = json.dumps(extracted_urls), "200"
    return client_answer
        