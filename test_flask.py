from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['POST'])
def test():
    try:
        data = request.json
        message = data.get('message', 'No message')
        return jsonify({'status': 'ok', 'received': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Test server starting on http://localhost:5001")
    app.run(debug=False, port=5001, use_reloader=False)
