from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>원재료 계산기 - 만원요리 최씨남매</h1>
    <p>앱이 정상적으로 실행중입니다.</p>
    <p><a href="/health">Health Check</a></p>
    '''

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'App is running'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)