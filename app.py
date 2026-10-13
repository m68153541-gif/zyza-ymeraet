# ============================================================
#  SIM SPINNER — сервер
#  Локально: python app.py
#  Render:   gunicorn app:app
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

PLAYERS = {}
START_BALANCE = 100000


def get_or_create_player(user_id, username=None, first_name=None):
    """Возвращает игрока. Если нет — создаёт с 100 000 ₽."""
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "username": (username or "").lstrip("@").lower(),
            "first_name": first_name or "Игрок",
        }
    else:
        # Обновляем username, если игрок уже есть
        if username:
            PLAYERS[user_id]["username"] = username.lstrip("@").lower()
        if first_name:
            PLAYERS[user_id]["first_name"] = first_name
    return PLAYERS[user_id]


def find_player_by_username(username):
    """Ищет игрока по username (без @, регистр не важен)."""
    if not username:
        return None
    clean = username.lstrip("@").lower()
    for uid, data in PLAYERS.items():
        if data.get("username") == clean:
            return uid, data
    return None, None


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})


# ============================================================
#  Баланс игрока
#  GET /api/balance?user_id=123&username=xxx&first_name=Иван
# ============================================================
@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400
    username = request.args.get("username")
    first_name = request.args.get("first_name")
    player = get_or_create_player(user_id, username, first_name)
    return jsonify({
        "user_id": user_id,
        "balance": player["balance"],
        "username": player["username"],
        "first_name": player["first_name"],
    })


# ============================================================
#  Прокрутка
#  POST /api/spin { user_id, mode, price, rarity }
# ============================================================
@app.route("/api/spin", methods=["POST"])
def spin():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    mode = data.get("mode", "normal")
    price = int(data.get("price", 0))
    cost = int(data.get("cost", 0))

    if not user_id:
        return jsonify({"error": "no user_id"}), 400

    player = get_or_create_player(user_id)

    if player["balance"] < cost:
        return jsonify({"error": "Недостаточно средств", "balance": player["balance"]}), 400

    player["balance"] -= cost
    player["balance"] += price

    return jsonify({
        "balance": player["balance"],
        "delta": price - cost,
    })


# ============================================================
#  Перевод по username
#  POST /api/transfer { user_id, to_username, amount }
# ============================================================
@app.route("/api/transfer", methods=["POST"])
def transfer():
    data = request.get_json(force=True) or {}
    from_id = data.get("user_id")
    to_username = data.get("to_username", "").strip()
    amount = data.get("amount")

    if not from_id:
        return jsonify({"error": "нет отправителя"}), 400
    if not to_username:
        return jsonify({"error": "укажи username получателя"}), 400
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "сумма должна быть числом"}), 400
    if amount <= 0:
        return jsonify({"error": "сумма должна быть больше 0"}), 400

    sender = get_or_create_player(from_id)
    to_id, receiver = find_player_by_username(to_username)

    if not receiver:
        return jsonify({"error": "Игрок @" + to_username.lstrip("@") + " не найден"}), 404

    if to_id == str(from_id):
        return jsonify({"error": "нельзя перевести самому себе"}), 400

    if sender["balance"] < amount:
        return jsonify({"error": "Недостаточно средств"}), 400

    sender["balance"] -= amount
    receiver["balance"] += amount

    return jsonify({
        "status": "ok",
        "from_balance": sender["balance"],
        "to_username": receiver["username"],
        "to_first_name": receiver["first_name"],
        "amount": amount,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
