import os
from urllib.request import urlopen
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

import http.client
from env import *

app = Flask(__name__)
setup_db(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')

    return response


def get_management_api_access_token():
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)

    management_payload = f"grant_type=client_credentials&client_id={M_TO_M_CLIENT_ID}&client_secret={M_TO_M_CLIENT_SECRET}&audience=https://{AUTH0_DOMAIN}/api/v2/"

    headers = { 
        'content-type': "application/x-www-form-urlencoded"
    }

    conn.request("POST", "/oauth/token", management_payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")
    jsonDic = json.loads(decoded_data)
    access_token = ''
    if 'access_token' in jsonDic:
        access_token = jsonDic['access_token']

    return access_token

def get_users_data():
    access_token = get_management_api_access_token()

    if not access_token:
        abort(401)
    
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)

    headers = { 
        'Authorization': f"Bearer {access_token}"
    }

    conn.request("GET", "/api/v2/users", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")
    jsonDic = json.loads(decoded_data)

    if not jsonDic:
        abort(401)
    
    return jsonDic

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    formated_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formated_drinks
    }), 200



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_datail(payload):
    drinks = Drink.query.all()
    formated_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formated_drinks
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(payload):
    data = request.get_json()
    title = data['title']
    recipe = data['recipe']
    if not title or not recipe:
        abort(422)

    drink = Drink(title=title, recipe=json.dumps(recipe))
    try:
        drink.insert()
    except:
        abort(422)

    
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, id):
    data = request.get_json()

    try:
        drink = Drink.query.get(id)
    except:
        abort(404)

    if 'title' in data:
        drink.title = data['title']
        
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])

    try:
        drink.update()
    except:
        abort(422)
    
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    
    try:
        drink = Drink.query.get(id)
    except:
        abort(404)

    try:
        drink.delete()
    except:
        abort(422)
    
    return jsonify({
        "success": True,
        "drinks": id
    }), 200

## Users management 
@app.route('/users')
@requires_auth('read:users')
def get_users(payload):
    body = []
    users = get_users_data()

    if not users:
        abort(401)

    for user in users:
        body.append({
            'email': user['email'],
            'nickname': user['nickname'],
            'user_id': user['user_id'],
        })

    return jsonify(body)








## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
# there is no other error codes

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "item was not found"
                    }), 404

@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized Access"
                    }), 401

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, 
        "error": error.error['code'],
        "message": error.error['description']
    }), error.status_code

print('===========================================================================')