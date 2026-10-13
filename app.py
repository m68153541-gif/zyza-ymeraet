# ============================================================
#  SIM SPINNER — серверная часть
#  Запуск локально:  python app.py
#  Railway/Render:   gunicorn app:app
# ============================================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)  # разрешает запросы с GitHub Pages


# ============================================================
#  ХРАНИЛИЩЕ ИГРОКОВ (в памяти, потом заменим на БД)
#  Ключ — ID игрока (Telegram user_id или сгенерированный)
# ============================================================
PLAYERS = {
    # пример:
    # "123456789": {"balance": 100000, "nick": "player1"}
}

START_BALANCE = 100000


def get_or_create_player(user_id):
    """Возвращает игрока, если нет — создаёт с начальным балансом."""
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "nick": "player_" + user_id[-4:],
        }
    return PLAYERS[user_id]


# ============================================================
#  API
# ============================================================

@app.route("/")
def index():
    return "SIM Spinner server is running"


@app.route("/api/ping")
def ping():
    """Проверка, что сервер жив."""
    return jsonify({"status": "ok"})


@app.route("/api/balance")
def balance():
    """Получить баланс игрока."""
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
    """
    Серверная прокрутка.
    Списывает стоимость, генерирует номер, начисляет или сохраняет.
    """
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

    # --- тут будет логика генерации номера ---
    # Пока заглушка
    price = random.randint(50, 50000)
    player["balance"] += price

    return jsonify({
        "balance": player["balance"],
        "result": {
            "number": "".join(random.choices(string.digits, k=9)),
            "price": price,
        }
    })


@app.route("/api/transfer", methods=["POST"])
def transfer():
    """
    Перевод денег другому игроку.
    Тело запроса: { "from": "user_id_1", "to": "user_id_2", "amount": 500 }
    """
    data = request.get_json(force=True) or {}
    from_id = data.get("from")
    to_id = data.get("to")
    amount = data.get("amount")

    if not from_id or not to_id or not amount:
        return jsonify({"error": "нужны from, to, amount"}), 400

    amount = int(amount)
    if amount <= 0:
        return jsonify({"error": "сумма должна быть больше 0"}), 400

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
#  ЗАПУСК
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
