from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # чтобы GitHub Pages мог обращаться к серверу

# Заглушка на будущее
@app.route('/api/balance', methods=['GET'])
def get_balance():
    # Тут будет логика получения баланса игрока
    return jsonify({"balance": 100000})

@app.route('/api/transfer', methods=['POST'])
def transfer():
    # Тут будет логика передачи денег
    data = request.json
    return jsonify({"status": "ok", "to": data.get("to"), "amount": data.get("amount")})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
