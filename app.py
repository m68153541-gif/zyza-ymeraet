# ============================================================
#  SIM SPINNER — сервер + игра на одной ссылке
#  Локально:        python app.py  →  http://127.0.0.1:5000
#  Render:          gunicorn app:app
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import random
import string

app = Flask(__name__)
CORS(app)  # разрешает запросы с других доменов (на будущее)


# ============================================================
#  ХРАНИЛИЩЕ ИГРОКОВ (в памяти, потом заменим на БД)
#  Ключ — user_id (например, Telegram user_id)
# ============================================================
PLAYERS = {}
START_BALANCE = 100000


def get_or_create_player(user_id):
    """Возвращает игрока. Если его нет — создаёт с начальным балансом."""
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "nick": "player_" + user_id[-4:],
        }
    return PLAYERS[user_id]


# ============================================================
#  ГЛАВНАЯ — отдаём игру (index.html из корня проекта)
# ============================================================
@app.route("/")
def index():
    return send_file("index.html")


# ============================================================
#  API: проверка, что сервер жив
# ============================================================
@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})


# ============================================================
#  API: получить баланс игрока
#  GET /api/balance?user_id=123
# ============================================================
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


# ============================================================
#  API: прокрутка (пока заглушка, потом перенесём логику из HTML)
#  POST /api/spin  { "user_id": "123", "mode": "normal|lucky|super" }
# ============================================================
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
        return jsonify({
            "error": "Недостаточно средств",
            "balance": player["balance"],
        }), 400

    player["balance"] -= cost

    # ВРЕМЕННАЯ заглушка. Позже сюда перенесём beauty_score и generate_number
    price = random.randint(50, 50000)
    player["balance"] += price

    return jsonify({
        "balance": player["balance"],
        "result": {
            "number": "".join(random.choices(string.digits, k=9)),
            "price": price,
        },
    })


# ============================================================
#  API: перевод денег другому игроку
#  POST /api/transfer  { "from": "1", "to": "2", "amount": 500 }
# ============================================================
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

    return jsonify({
        "status": "ok",
        "from_balance": sender["balance"],
        "to_balance": receiver["balance"],
    })


# ============================================================
#  ЗАПУСК (локально)
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
