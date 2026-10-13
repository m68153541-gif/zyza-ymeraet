# ============================================================
#  SIM SPINNER — сервер + игра
#  Локально: python app.py
#  Render:   gunicorn app:app
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import random

app = Flask(__name__)
CORS(app)

PLAYERS = {}
START_BALANCE = 100000


def get_or_create_player(user_id):
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "nick": "player_" + user_id[-4:],
        }
    return PLAYERS[user_id]


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})


@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    return jsonify({
        "user_id": user_id,
        "balance": player["balance"],
        "nick": player["nick"],
    })


@app.route("/api/spin", methods=["POST"])
def spin():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    mode = data.get("mode", "normal")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    cost = {"normal": 150, "lucky": 5000, "super": 20000}.get(mode, 150)
    if player["balance"] < cost:
        return jsonify({"error": "Недостаточно средств", "balance": player["balance"]}), 400
    player["balance"] -= cost
    price = random.randint(50, 40000000)
    player["balance"] += price
    return jsonify({
        "balance": player["balance"],
        "result": {"number": "".join(random.choices("0123456789", k=9)), "price": price},
    })


@app.route("/api/transfer", methods=["POST"])
def transfer():
    data = request.get_json(force=True) or {}
    from_id = data.get("from")
    to_id = data.get("to")
    amount = data.get("amount")
    if not from_id or not to_id or not amount:
        return jsonify({"error": "нужны from, to, amount"}), 400
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "сумма должна быть числом"}), 400
    if amount <= 0:
        return jsonify({"error": "сумма должна быть больше 0"}), 400
    if str(from_id) == str(to_id):
        return jsonify({"error": "нельзя перевести самому себе"}), 400
    sender = get_or_create_player(from_id)
    receiver = get_or_create_player(to_id)
    if sender["balance"] < amount:
        return jsonify({"error": "Недостаточно средств"}), 400
    sender["balance"] -= amount
    receiver["balance"] += amount
    return jsonify({"status": "ok", "from_balance": sender["balance"], "to_balance": receiver["balance"]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
