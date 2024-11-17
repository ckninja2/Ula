from flask import Flask, request
import urllib.request

app = Flask(__name__)

def get_google_time():
    request = urllib.request.Request("http://www.google.com", method="HEAD")
    with urllib.request.urlopen(request) as response:
        date_str = response.headers['Date']
    return date_str
    
@app.route('/')
def hello():
    requester_ip = request.remote_addr
    return f"Hello, World! Welcome to Koyeb!<br>{get_google_time()}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
