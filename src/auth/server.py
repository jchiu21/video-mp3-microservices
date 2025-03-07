"""
Flask-based authentication service using JWT.

This API provides authentication functionality using both Basic Authentication 
(for login) and Bearer Authentication (JWT for subsequent requests). 

Endpoints:
- `/login` (POST): Authenticates a user with Basic Auth (username & password), 
  verifies credentials from a MySQL database, and returns a JWT.
- `/validate` (POST): Validates the provided JWT from the Authorization header.

Configuration:
- Uses environment variables for MySQL credentials and JWT secret.
- Runs on port 5000.

Dependencies:
- Flask, Flask-MySQLdb, PyJWT, and OS environment variables.
"""

import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

@server.route("/login", methods=["POST"])
def login():
    # parse the Basic Authorization header (username:password) from the request
    auth = request.authorization  
    if not auth:
        return "missing credentials", 401
    
    # query db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user where email=%s", (auth.username,)
    )
    
    if res > 0:
        user_row = cur.fetchone() # retrieve the user
        email = user_row[0]
        password = user_row[1]
        
        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401
    

def createJWT(username, secret, authz):
    return jwt.encode(
        # Payload
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) # expires in 24hrs
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": authz
        },
        secret,
        algorithm="HS256"
    )
    
    
@server.route("/validate", methods=["POST"])
def validate():
    # Extract Bearer token from auth header
    encoded_jwt = request.headers["Authorization"]
    
    if not encoded_jwt:
        return "missing credentials", 401
    
    # The auth header will be in format "Bearer <JWT>"
    encoded_jwt = encoded_jwt.split(" ")[1]
    
    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithm=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200

    
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)  # listen on all docker container IP addresses