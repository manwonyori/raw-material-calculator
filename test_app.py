from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>원재료 계산기 작동 중!</h1>'

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)