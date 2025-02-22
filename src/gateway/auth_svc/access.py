import os, requests

# Forward authentication request to auth service
def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    
    # Header for basic auth
    basicAuth = (auth.username, auth.password)
    
    # Send post request to Auth Service's login endpoint with basic auth 
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", 
        auth=basicAuth
    )
    
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)