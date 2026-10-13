# ============================================================
#  SIM SPINNER — сервер
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

PLAYERS = {}
START_BALANCE = 100000
DAILY_BASE = 10000
DAILY_STEP = 5000


def get_or_create_player(user_id, username=None, first_name=None, photo=None):
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "username": (username or "").lstrip("@").lower(),
            "first_name": first_name or "Игрок",
            "photo": photo or "",
            "last_daily": 0,       # timestamp последнего получения
            "daily_streak": 0,     # сколько дней подряд
        }
    else:
        if username: PLAYERS[user_id]["username"] = username.lstrip("@").lower()
        if first_name: PLAYERS[user_id]["first_name"] = first_name
        if photo: PLAYERS[user_id]["photo"] = photo
    return PLAYERS[user_id]


def find_player_by_username(username):
    if not username: return None, None
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
#  Баланс + регистрация игрока
# ============================================================
@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(
        user_id,
        request.args.get("username"),
        request.args.get("first_name"),
        request.args.get("photo"),
    )
    return jsonify({
        "user_id": user_id,
        "balance": player["balance"],
        "username": player["username"],
        "first_name": player["first_name"],
    })


# ============================================================
#  Прокрутка
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
    return jsonify({"balance": player["balance"], "delta": price - cost})


# ============================================================
#  Перевод по username — моментальное зачисление
# ============================================================
@app.route("/api/transfer", methods=["POST"])
def transfer():
    data = request.get_json(force=True) or {}
    from_id = data.get("user_id")
    to_username = data.get("to_username", "").strip()
    amount = data.get("amount")

    if not from_id: return jsonify({"error": "нет отправителя"}), 400
    if not to_username: return jsonify({"error": "укажи username получателя"}), 400
    try: amount = int(amount)
    except: return jsonify({"error": "сумма должна быть числом"}), 400
    if amount <= 0: return jsonify({"error": "сумма должна быть больше 0"}), 400

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


# ============================================================
#  Топ-3 игроков по балансу
# ============================================================
@app.route("/api/top")
def top():
    sorted_players = sorted(PLAYERS.items(), key=lambda x: x[1]["balance"], reverse=True)
    top3 = []
    for uid, p in sorted_players[:3]:
        top3.append({
            "user_id": uid,
            "balance": p["balance"],
            "username": p["username"],
            "first_name": p["first_name"],
            "photo": p["photo"],
        })
    return jsonify({"top": top3})


# ============================================================
#  Ежедневный бонус
# ============================================================
@app.route("/api/daily")
def daily():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    now = int(time.time())
    one_day = 24 * 60 * 60
    elapsed = now - player["last_daily"]

    if player["last_daily"] == 0:
        # первый раз
        pass
    elif elapsed < one_day:
        return jsonify({
            "available": False,
            "next_in": one_day - elapsed,
            "streak": player["daily_streak"],
        })

    # обновляем streak: если прошло больше 2 дней — сбрасываем
    if player["last_daily"] > 0 and elapsed > one_day * 2:
        player["daily_streak"] = 0

    player["daily_streak"] += 1
    reward = DAILY_BASE + (player["daily_streak"] - 1) * DAILY_STEP
    player["balance"] += reward
    player["last_daily"] = now

    return jsonify({
        "available": True,
        "reward": reward,
        "streak": player["daily_streak"],
        "balance": player["balance"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
