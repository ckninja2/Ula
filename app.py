from flask import Flask
import urllib.request

app = Flask(__name__)

def get_google_time():
    request = urllib.request.Request("http://www.google.com", method="HEAD")
    with urllib.request.urlopen(request) as response:
        date_str = response.headers['Date']
    return date_str
    
@app.route('/')
def hello():
    return f"Hello, World! Welcome to Koyeb!\n{get_google_time()}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
