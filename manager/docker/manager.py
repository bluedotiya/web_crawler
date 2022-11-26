import json
import jsonschema
import requests
import redis
from flask import Flask, request, Response

# Global Variables

# DNS Names
REDIS_DNS_NAME = "redis.redis.svc.cluster.local"
FEEDER_DNS_NAME ="feeder.feeder.svc.cluster.local"

# Flask Server Obj
app = Flask(__name__)

# Redis Server Obj
redis_obj = redis.Redis(host=REDIS_DNS_NAME, port=6379, db=0, password='a-very-complex-password-here')


@app.route('/url', methods=['POST'])
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
    
    # Send request to Feeder
    feeder_req_data = client_req
    feeder_response = requests.post('http://feeder.feeder.svc.cluster.local', json=feeder_req_data)

    # Check response from feeder
    if feeder_response.status_code != 200:
        return Response(feeder_response.text, status=feeder_response.status_code, mimetype='application/json') 

    # Create New Job Hashmap on Redis
    redis_obj.hset(client_req['url'], 'depth1', client_req['url'])

    # Send feeder response to redis
    for url in feeder_response.json()['urls']:
        inset_res = redis_obj.sadd('urls', url)
        # Check if insert operation was successful
        if inset_res != 1:
            return Response("{'Error':'reddis insert failed'}", status=500, mimetype='application/json')

    # Get inserted value, Normalize to JSON
    get_res = redis_obj.smembers(name='urls')
    normalized_output = json.loads(list(get_res))

    # Return ANS to Client
    return Response(normalized_output, status=200, mimetype='application/json')
    

