from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to PackPal Minimal API",
        "version": "1.0.0",
        "status": "Running"
    })

@app.route('/api/hello')
def hello():
    return jsonify({
        "message": "Hello from PackPal API!"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 