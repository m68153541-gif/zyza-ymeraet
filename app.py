# ============================================================
#  SIM SPINNER — сервер с рефералами и ботом
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import time
import random
import requests

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8688292241:AAEpB6R9ndFLFCjUOs_vC0gmAJZwg_TUUMw")
START_BALANCE = 100000
DAILY_BASE = 10000
DAILY_STEP = 5000
REF_START_BONUS = 50000          # за переход друга по ссылке
REF_MYTH_PERCENT = 0.20          # 20% от мифа друга

PLAYERS = {}


def get_or_create_player(user_id, username=None, first_name=None, photo=None):
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "username": (username or "").lstrip("@").lower(),
            "first_name": first_name or "Игрок",
            "photo": photo or "",
            "last_daily": 0,
            "daily_streak": 0,
            "level": 1,
            "xp": 0,
            "referrer": None,           # кто пригласил
            "ref_earnings": 0,          # сколько заработал на рефералах
            "total_spins": 0,
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


def send_telegram_message(chat_id, text):
    """Отправка сообщения через Telegram Bot API."""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=5)
    except Exception as e:
        print("Bot error:", e)


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})


@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
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
        "level": player["level"],
        "xp": player["xp"],
        "ref_earnings": player["ref_earnings"],
    })


@app.route("/api/spin", methods=["POST"])
def spin():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    mode = data.get("mode", "normal")
    price = int(data.get("price", 0))
    cost = int(data.get("cost", 0))
    rarity = data.get("rarity", "")

    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)

    if player["balance"] < cost:
        return jsonify({"error": "Недостаточно средств", "balance": player["balance"]}), 400

    player["balance"] -= cost
    player["balance"] += price
    player["total_spins"] += 1

    # XP и уровень
    xp_gain = 1 if mode == "normal" else (5 if mode == "lucky" else 15)
    player["xp"] += xp_gain
    new_level = 1 + player["xp"] // 100
    if new_level > player["level"]:
        player["level"] = new_level
        # Уведомление о новом уровне
        send_telegram_message(user_id, f"🎉 Новый уровень: {new_level}! Стоимость прокруток выросла.")

    # Реферальный бонус за мифик
    if rarity == "МИФ" and player.get("referrer"):
        bonus = int(price * REF_MYTH_PERCENT)
        referrer = PLAYERS.get(player["referrer"])
        if referrer:
            referrer["balance"] += bonus
            referrer["ref_earnings"] += bonus
            send_telegram_message(
                player["referrer"],
                f"💎 Твой реферал выбил МИФ! Начислено {bonus:,} ₽".replace(",", " ")
            )

    return jsonify({
        "balance": player["balance"],
        "delta": price - cost,
        "level": player["level"],
        "xp": player["xp"],
    })


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

    send_telegram_message(to_id, f"💰 Вам перевели {amount:,} ₽ от @{sender['username']}".replace(",", " "))

    return jsonify({
        "status": "ok",
        "from_balance": sender["balance"],
        "to_username": receiver["username"],
        "to_first_name": receiver["first_name"],
        "amount": amount,
    })


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


@app.route("/api/daily")
def daily():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    now = int(time.time())
    one_day = 24 * 60 * 60
    elapsed = now - player["last_daily"]

    if player["last_daily"] == 0:
        pass
    elif elapsed < one_day:
        return jsonify({"available": False, "next_in": one_day - elapsed, "streak": player["daily_streak"]})

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


# ============================================================
#  РЕФЕРАЛЫ
# ============================================================
@app.route("/api/ref/register", methods=["POST"])
def ref_register():
    """Регистрация реферала. Вызывается при /start с параметром."""
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    referrer_id = data.get("referrer_id")

    if not user_id or not referrer_id:
        return jsonify({"error": "нужны user_id и referrer_id"}), 400

    player = get_or_create_player(user_id)
    if player["referrer"]:
        return jsonify({"error": "уже есть реферер"}), 400

    referrer = PLAYERS.get(str(referrer_id))
    if not referrer:
        return jsonify({"error": "реферер не найден"}), 404

    player["referrer"] = str(referrer_id)
    referrer["balance"] += REF_START_BONUS

    send_telegram_message(referrer_id, f"🎉 По твоей ссылке зашёл друг! +{REF_START_BONUS:,} ₽".replace(",", " "))

    return jsonify({
        "status": "ok",
        "referrer": referrer_id,
        "bonus": REF_START_BONUS,
    })


@app.route("/api/ref/info")
def ref_info():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)

    # Считаем рефералов
    refs = [uid for uid, p in PLAYERS.items() if p.get("referrer") == str(user_id)]

    return jsonify({
        "ref_earnings": player["ref_earnings"],
        "ref_count": len(refs),
        "ref_link": f"https://t.me/YOUR_BOT?start={user_id}",
    })


# ============================================================
#  BOT WEBHOOK (для /start с реферальной ссылкой)
# ============================================================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Telegram будет присылать сюда все обновления."""
    data = request.get_json(force=True)
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        user = msg.get("from", {})

        # /start с реферальной ссылкой
        if text.startswith("/start"):
            parts = text.split()
            if len(parts) > 1:
                referrer_id = parts[1]
                # Регистрируем реферала
                get_or_create_player(
                    chat_id,
                    user.get("username"),
                    user.get("first_name"),
                )
                player = PLAYERS[str(chat_id)]
                if not player["referrer"] and referrer_id != str(chat_id):
                    player["referrer"] = referrer_id
                    referrer = PLAYERS.get(referrer_id)
                    if referrer:
                        referrer["balance"] += REF_START_BONUS
                        send_telegram_message(referrer_id, f"🎉 По твоей ссылке зашёл друг! +{REF_START_BONUS:,} ₽".replace(",", " "))

            # Приветственное сообщение
            welcome = (
                "🎰 <b>Добро пожаловать в «Крути номер»!</b>\n\n"
                "Это игра, где ты крутишь SIM-карты и выбиваешь красивые номера.\n"
                "💰 Продавай их и богатей!\n"
                "🏆 Соревнуйся с друзьями в топе.\n"
                "💸 Переводи деньги друзьям.\n"
                "🎡 Улучшай номера на колесе удачи.\n\n"
                "🎁 <b>Бонусы за друга:</b>\n"
                "• +50 000 ₽ за каждого, кто зайдёт по твоей ссылке\n"
                "• +20% от каждого МИФА, который он выбьет\n\n"
                "Нажми кнопку внизу, чтобы начать! 👇"
            )
            send_telegram_message(chat_id, welcome)

    return jsonify({"ok": True})


@app.route("/api/set_webhook")
def set_webhook():
    """Вызови один раз, чтобы установить webhook."""
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "нужен ?url=https://..."}), 400
    full_url = f"{url}/webhook/{BOT_TOKEN}"
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": full_url}
    )
    return jsonify(r.json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
