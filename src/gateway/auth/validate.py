import os, requests

def token(request):
    # check if Authorization header exists
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)
    
    token = request.headers["Authorization"]
    
    # check if token is empty or None
    if not token:
        return None, ("missing credentials", 401)

    # send POST request to auth service's validate endpoint
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token}
    )
    
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)