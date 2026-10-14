# ============================================================
#  SIM SPINNER — сервер с ботом, рефералами и рассылкой
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import time
import random
import threading
import requests

app = Flask(__name__)
CORS(app)

# ТОКЕН БОТА — ПОСЛЕ ТЕСТА СМЕНИ В @BotFather (/revoke → /token)
BOT_TOKEN = "8688292241:AAEpB6R9ndFLFCjUOs_vC0gmAJZwg_TUUMw"
BOT_USERNAME = "Sim_moner_zyza_ymer_bot"
START_BALANCE = 100000
REF_START_BONUS = 50000
REF_MYTH_PERCENT = 0.20
DAILY_REWARDS = [10000, 15000, 20000, 25000, 30000, 40000, 50000]

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
            "daily_claims": [],
            "level": 1,
            "xp": 0,
            "referrer": None,
            "ref_earnings": 0,
            "total_spins": 0,
            "last_seen": int(time.time()),
        }
    else:
        if username: PLAYERS[user_id]["username"] = username.lstrip("@").lower()
        if first_name: PLAYERS[user_id]["first_name"] = first_name
        if photo: PLAYERS[user_id]["photo"] = photo
        PLAYERS[user_id]["last_seen"] = int(time.time())
    return PLAYERS[user_id]


def find_player_by_username(username):
    if not username: return None, None
    clean = username.lstrip("@").lower()
    for uid, data in PLAYERS.items():
        if data.get("username") == clean:
            return uid, data
    return None, None


def send_tg(chat_id, text, with_button=False):
    if not BOT_TOKEN: return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        if with_button:
            payload["reply_markup"] = {
                "inline_keyboard": [[
                    {"text": "🎰 Открыть игру", "url": f"https://t.me/{BOT_USERNAME}/app"}
                ]]
            }
        requests.post(url, json=payload, timeout=5)
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

    xp_gain = 1 if mode == "normal" else (5 if mode == "lucky" else 15)
    old_level = player["level"]
    player["xp"] += xp_gain
    new_level = 1 + player["xp"] // 100
    if new_level > old_level:
        player["level"] = new_level
        if new_level % 10 == 0:
            reward = 10000 * (new_level // 10)
            player["balance"] += reward
            send_tg(user_id,
                f"🎉 <b>Новый уровень {new_level}!</b>\n\n"
                f"Ты получил приз: <b>+{reward:,} ₽</b>\n"
                f"Продолжай крутить! 💪".replace(",", " "))

    if rarity == "МИФ" and player.get("referrer"):
        bonus = int(price * REF_MYTH_PERCENT)
        ref = PLAYERS.get(player["referrer"])
        if ref:
            ref["balance"] += bonus
            ref["ref_earnings"] += bonus
            send_tg(player["referrer"],
                f"💎 <b>Твой друг выбил МИФ!</b>\n\n"
                f"@{player['username']} сорвал джекпот.\n"
                f"Тебе начислено: <b>+{bonus:,} ₽</b> (20%)".replace(",", " "))

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

    send_tg(to_id,
        f"💰 <b>Вам перевели деньги!</b>\n\n"
        f"От: @{sender['username'] or 'игрок'}\n"
        f"Сумма: <b>+{amount:,} ₽</b>".replace(",", " "))
    send_tg(from_id,
        f"✅ <b>Перевод отправлен</b>\n\n"
        f"Кому: @{receiver['username'] or 'игрок'}\n"
        f"Сумма: <b>-{amount:,} ₽</b>".replace(",", " "))

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


# ============================================================
#  ЕЖЕДНЕВНЫЕ НАГРАДЫ
# ============================================================
@app.route("/api/daily/status")
def daily_status():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    now = int(time.time())
    one_day = 24 * 60 * 60
    claims = set(ts // one_day for ts in player.get("daily_claims", []))
    today = now // one_day

    days = []
    for i in range(6, -1, -1):
        day_ts = today - i
        day_index = (6 - i)
        days.append({
            "day": day_index + 1,
            "reward": DAILY_REWARDS[day_index],
            "claimed": day_ts in claims,
            "today": day_ts == today,
            "can_claim": day_ts == today and day_ts not in claims,
        })
    return jsonify({"days": days, "streak": player.get("daily_streak", 0)})


@app.route("/api/daily/claim", methods=["POST"])
def daily_claim():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)

    now = int(time.time())
    one_day = 24 * 60 * 60
    today = now // one_day
    claims = set(ts // one_day for ts in player.get("daily_claims", []))
    if today in claims:
        return jsonify({"error": "Сегодня уже забрал"}), 400

    streak = 0
    for i in range(7):
        if (today - i) in claims:
            streak += 1
        else:
            break

    reward = DAILY_REWARDS[min(streak, 6)]
    player["balance"] += reward
    player["daily_claims"].append(now)
    player["daily_streak"] = streak + 1
    player["last_daily"] = now

    send_tg(user_id, f"🎁 Ежедневная награда: +{reward:,} ₽ (день {min(streak+1,7)})".replace(",", " "))

    return jsonify({"status": "ok", "reward": reward, "balance": player["balance"], "streak": player["daily_streak"]})


# ============================================================
#  РЕФЕРАЛЫ
# ============================================================
@app.route("/api/ref/register", methods=["POST"])
def ref_register():
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
    referrer["ref_earnings"] += REF_START_BONUS

    send_tg(referrer_id,
        f"🎉 <b>По твоей ссылке зашёл друг!</b>\n\n"
        f"Ты получил бонус: <b>+{REF_START_BONUS:,} ₽</b>\n"
        f"С каждого его МИФА будешь получать 20%.".replace(",", " "))

    return jsonify({"status": "ok", "referrer": referrer_id, "bonus": REF_START_BONUS})


@app.route("/api/ref/info")
def ref_info():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    refs = [uid for uid, p in PLAYERS.items() if p.get("referrer") == str(user_id)]
    return jsonify({
        "ref_earnings": player["ref_earnings"],
        "ref_count": len(refs),
        "ref_link": f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}",
    })


# ============================================================
#  WEBHOOK
# ============================================================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        user = msg.get("from", {})

        if text.startswith("/start"):
            # Реферальный параметр
            parts = text.split()
            if len(parts) > 1 and parts[1].startswith("ref_"):
                referrer_id = parts[1][4:]
                get_or_create_player(chat_id, user.get("username"), user.get("first_name"))
                player = PLAYERS[str(chat_id)]
                if not player["referrer"] and referrer_id != str(chat_id):
                    player["referrer"] = referrer_id
                    referrer = PLAYERS.get(referrer_id)
                    if referrer:
                        referrer["balance"] += REF_START_BONUS
                        referrer["ref_earnings"] += REF_START_BONUS
                        send_tg(referrer_id,
                            f"🎉 <b>По твоей ссылке зашёл друг!</b>\n\n"
                            f"Ты получил: <b>+{REF_START_BONUS:,} ₽</b>".replace(",", " "))

            welcome = (
                "🎰 <b>Добро пожаловать в «Крути номер»!</b>\n\n"
                "Это игра, где ты крутишь SIM-карты и выбиваешь красивые номера.\n\n"
                "💰 <b>Как играть:</b>\n"
                "• Выбирай страну (Африка дешевле, Дубай дороже)\n"
                "• Крути — 150, 5000 или 20000 ₽\n"
                "• Редкие номера уходят в «Мои номера» — продавай!\n"
                "• Улучшай номера на колесе фортуны (×2 или сгорание)\n\n"
                "🎁 <b>Бонусы:</b>\n"
                "• +50 000 ₽ за каждого друга по твоей ссылке\n"
                "• +20% от каждого МИФА друга\n"
                "• Ежедневный бонус (растёт каждый день)\n"
                "• Приз на каждом 10 уровне\n\n"
                "Нажми кнопку ниже, чтобы начать! 👇"
            )
            send_tg(chat_id, welcome, with_button=True)

    return jsonify({"ok": True})


@app.route("/api/set_webhook")
def set_webhook():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "нужен ?url=https://..."}), 400
    full_url = f"{url}/webhook/{BOT_TOKEN}"
    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", json={"url": full_url})
    return jsonify(r.json())


# ============================================================
#  РАССЫЛКА КАЖДЫЙ ЧАС
# ============================================================
HOURLY_MESSAGES = [
    "🎰 <b>Как дела?</b>\nЗагляни в игру — может, сегодня твой день!\nЖми /start",
    "💎 <b>Не забыл про игру?</b>\nДрузья уже крутят номера. Ты с ними?\nЖми /start",
    "🎁 <b>Ежедневный бонус ждёт!</b>\nЗагляни в игру и забери приз.\nЖми /start",
    "🏆 <b>Хочешь в ТОП-3?</b>\nОбгони друзей по балансу!\nЖми /start",
    "💰 <b>Что-то давно не крутил.</b>\nЗаходи, пока удача на твоей стороне!\nЖми /start",
    "🔥 <b>Один оборот — и ты миллионер?</b>\nТолько в «Крути номер».\nЖми /start",
    "👥 <b>Приглашай друзей!</b>\nЗа каждого — 50 000 ₽ + 20% от его МИФов.\nЖми /start",
]

_last_hour_sent = [0]

def hourly_broadcaster():
    """Раз в час рассылает напоминание всем активным игрокам."""
    while True:
        try:
            now = int(time.time())
            current_hour = now // 3600
            if _last_hour_sent[0] != current_hour:
                _last_hour_sent[0] = current_hour
                msg = random.choice(HOURLY_MESSAGES)
                for uid, p in list(PLAYERS.items()):
                    # только тем, кто заходил за последние 3 дня
                    if now - p.get("last_seen", 0) < 3 * 24 * 3600:
                        send_tg(uid, msg)
        except Exception as e:
            print("Broadcast error:", e)
        time.sleep(600)  # проверяем каждые 10 минут


# Запуск фонового потока
_bg_thread = threading.Thread(target=hourly_broadcaster, daemon=True)
_bg_thread.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
