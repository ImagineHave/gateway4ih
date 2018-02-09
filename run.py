from app import app
from facebook import GraphAPI
from flask import Flask, jsonify, request #, session
from app.models import User
import pymongo
import os

is_prod = os.environ.get('IS_HEROKU', None)

if is_prod:    
    uri  = os.environ.get('MONGODB_URI') #= 'mongodb://gateway:gateway4ih@ds227168.mlab.com:27168/userdb' 
    client = pymongo.MongoClient(uri)
    db = client.get_default_database()

if __name__ == "__main__":    
    app.run()

@app.route('/authoriseUser', methods=['POST'])
def signin():
    uid = request.args.get('uid','')
    print ("uid =", uid)    
        
    query = {'id': uid}
    
    user = db.users.find_one(query)
    print (user)    

    if not user:
        # Not an existing user so get info
        requestAccessToken = request.args.get('access_token','')
        print("token=", requestAccessToken)
        graph = GraphAPI(requestAccessToken)
        profile = graph.get_object('me')
        if 'link' not in profile:
            profile['link'] = ""

        # Create the user and insert it into the database
        user = User(id=str(profile['id']), name=profile['name'],
                        profile_url=profile['link'],
                        access_token=requestAccessToken)
        db.users.insert(user)
    elif user.access_token != requestAccessToken:
        # If an existing user, update the access token
        user.access_token = requestAccessToken

    response = jsonify({user})
    response.status_code = 200
    return response 
    
@app.route('/authorisedStatus', methods=['GET'])
def isAuthorised():
    
    db.users.insert({
        'id': '10',
        'profile_url': 'Debby Boone',
        'access_token': '12345'
    })
    query = {'id': request.args.get('uid','')}
    user = db.users.find_one(query)
    print (user)
    
    if not user:
        response = jsonify({"error":"User does not exist"})
        response.status_code = 401
        return response
    
    requestAccessToken = request.args.get('access_token','')
    
    if user['access_token'] != requestAccessToken:
        response = jsonify({"error":"Access token invalid"})
        response.status_code = 401
        return response
    
    response = jsonify({"authorisedStatus":"True"})
    response.status_code = 200
    return response
