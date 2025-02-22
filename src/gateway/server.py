"""
API gateway service that acts as intermediary between clients and other microservices.
"""

import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

# Create connection between Flask and mongoDB
mongo = PyMongo(server)

# Create connection between Flask and gridFS
fs = gridfs.GridFS(mongo.db)

# Creates a synchronous connection to rabbitMQ with the hostname in kubernetes
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# Client facing login endpoint that proxies to auth service
@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    
    if not err:
        return token
    else:
        return err 
    

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    
    access = json.loads(access) # deserialize json string into python object
    
    # If admin claim is true, upload to mongoDB
    if access["admin"]:
        if len(request.files) > 1 or len(request.files) == 0:
            return "exactly 1 file required", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access) # return error if it exists
            
            if err: 
                return err
            
        return "success!", 200
    else:
        return "not authorized", 401
        
    
@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
