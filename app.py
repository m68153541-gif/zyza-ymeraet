# ============================================================
#  SIM SPINNER — сервер
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os, time, random, threading, requests

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8688292241:AAEpB6R9ndFLFCjUOs_vC0gmAJZwg_TUUMw"
BOT_USERNAME = "Sim_moner_zyza_ymer_bot"
START_BALANCE = 50000
REF_START_BONUS = 25000
REF_MYTH_PERCENT = 0.05          # было 0.20 → теперь 5%
DAILY_REWARDS = [3000, 5000, 7000, 10000, 13000, 17000, 22000]
MAX_LEVEL = 1000                 # было 100 → теперь 1000

PLAYERS = {}

ACHIEVEMENTS = {
    "first_spin":   {"name": "Первый шаг",       "desc": "Сделай первую прокрутку",       "reward": 1000},
    "ten_spins":    {"name": "Разогрев",         "desc": "Сделай 10 прокруток",            "reward": 3000},
    "hundred_spins":{"name": "Крутила",          "desc": "Сделай 100 прокруток",           "reward": 15000},
    "thousand_spins":{"name":"Легенда круток",   "desc": "Сделай 1000 прокруток",          "reward": 150000},
    "first_rare":   {"name": "Первое РЕДКОЕ",   "desc": "Выбей РЕДКИЙ номер",            "reward": 3000},
    "first_epic":   {"name": "Эпичный",          "desc": "Выбей ЭПИК",                     "reward": 15000},
    "first_legend": {"name": "Легенда",          "desc": "Выбей ЛЕГЕНДУ",                  "reward": 60000},
    "first_myth":   {"name": "Мифический",       "desc": "Выбей МИФ",                      "reward": 300000},
    "millionaire":  {"name": "Миллионер",        "desc": "Имей 1 000 000 ₽",             "reward": 30000},
    "ten_millions": {"name": "Десять лямов",     "desc": "Имей 10 000 000 ₽",             "reward": 150000},
    "hundred_millions":{"name":"Сто миллионов",  "desc": "Имей 100 000 000 ₽",            "reward": 600000},
    "first_referral":{"name":"Первый друг",     "desc": "Пригласи первого друга",        "reward": 10000},
    "ten_referrals":{"name": "Наставник",        "desc": "Пригласи 10 друзей",             "reward": 150000},
    "first_daily":  {"name": "Ежедневный",       "desc": "Забери первую ежедневку",        "reward": 2000},
    "week_streak":  {"name": "Неделя подряд",    "desc": "Заходи 7 дней подряд",           "reward": 30000},
    "first_transfer":{"name":"Первый перевод",  "desc": "Переведи деньги другу",          "reward": 3000},
    "level_10":     {"name": "Десятка",          "desc": "Достигни 10 уровня",             "reward": 5000},
    "level_100":    {"name": "Сотка",            "desc": "Достигни 100 уровня",            "reward": 100000},
    "level_500":    {"name": "Пятисотка",        "desc": "Достигни 500 уровня",            "reward": 500000},
    "level_1000":   {"name": "ПОБЕДИТЕЛЬ",      "desc": "Достигни 1000 уровня — победа!", "reward": 3000000},
}

QUEST_POOL = [
    {"id":"q_spin_10",    "text":"Сделай 10 прокруток",       "target":10,  "reward":5000, "type":"spins"},
    {"id":"q_spin_50",    "text":"Сделай 50 прокруток",       "target":50,  "reward":18000, "type":"spins"},
    {"id":"q_spin_100",   "text":"Сделай 100 прокруток",      "target":100, "reward":40000, "type":"spins"},
    {"id":"q_rare",       "text":"Выбей РЕДКОЕ",              "target":1,   "reward":8000, "type":"rare"},
    {"id":"q_epic",       "text":"Выбей ЭПИК",                "target":1,   "reward":25000, "type":"epic"},
    {"id":"q_legend",     "text":"Выбей ЛЕГЕНДУ",             "target":1,   "reward":80000, "type":"legend"},
    {"id":"q_earn_500k",  "text":"Заработай 500 000 ₽",       "target":500000,"reward":25000,"type":"earned"},
    {"id":"q_earn_2m",    "text":"Заработай 2 000 000 ₽",     "target":2000000,"reward":80000,"type":"earned"},
    {"id":"q_sell_5",     "text":"Продай 5 номеров",          "target":5,   "reward":10000, "type":"sold"},
    {"id":"q_upgrade_1",  "text":"Улучши номер (×2)",         "target":1,   "reward":15000, "type":"upgraded"},
]


def today_key():
    return int(time.time()) // 86400


def ensure_quests(player):
    tk = today_key()
    if player.get("quests_date") != tk:
        picked = random.sample(QUEST_POOL, 4)
        player["quests"] = []
        for q in picked:
            player["quests"].append({
                "id": q["id"], "text": q["text"], "target": q["target"],
                "reward": q["reward"], "type": q["type"],
                "progress": 0, "claimed": False,
            })
        player["quests_date"] = tk


def add_quest_progress(player, qtype, amount=1):
    ensure_quests(player)
    for q in player["quests"]:
        if q["type"] == qtype and not q["claimed"]:
            q["progress"] = min(q["progress"] + amount, q["target"])


def unlock_achievement(player, aid):
    if aid not in ACHIEVEMENTS: return None
    if aid in player.get("achievements", []): return None
    player.setdefault("achievements", []).append(aid)
    player["balance"] += ACHIEVEMENTS[aid]["reward"]
    return {"id": aid, **ACHIEVEMENTS[aid]}


def player_league(balance):
    if balance < 1_000_000: return "bronze"
    if balance < 10_000_000: return "silver"
    return "gold"


def get_or_create_player(user_id, username=None, first_name=None, photo=None):
    user_id = str(user_id)
    if user_id not in PLAYERS:
        PLAYERS[user_id] = {
            "balance": START_BALANCE,
            "username": (username or "").lstrip("@").lower(),
            "first_name": first_name or "Игрок",
            "photo": photo or "",
            "daily_streak": 0,
            "daily_claims": [],
            "level": 1, "xp": 0,
            "referrer": None,
            "ref_earnings": 0,
            "total_spins": 0,
            "referral_count": 0,
            "last_seen": int(time.time()),
            "achievements": [],
            "quests": [],
            "quests_date": 0,
            "wins": 0,
            "prestiges": 0,
        }
    else:
        if username: PLAYERS[user_id]["username"] = username.lstrip("@").lower()
        if first_name: PLAYERS[user_id]["first_name"] = first_name
        if photo: PLAYERS[user_id]["photo"] = photo
        PLAYERS[user_id]["last_seen"] = int(time.time())
    p = PLAYERS[user_id]
    ensure_quests(p)
    return p


def find_player_by_username(username):
    if not username: return None, None
    clean = username.lstrip("@").lower()
    for uid, data in PLAYERS.items():
        if data.get("username") == clean:
            return uid, data
    return None, None


def send_tg(chat_id, text, with_button=False):
    if not BOT_TOKEN: return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        if with_button:
            payload["reply_markup"] = {"inline_keyboard": [[
                {"text": "🎰 Открыть игру", "url": f"https://t.me/{BOT_USERNAME}/app"}
            ]]}
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("TG error:", e)
        return False


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"})


@app.route("/api/debug")
def debug():
    try:
        info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo", timeout=5).json()
    except Exception as e: info = {"error": str(e)}
    return jsonify({"webhook": info, "players": len(PLAYERS)})


@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id, request.args.get("username"),
                                  request.args.get("first_name"), request.args.get("photo"))
    return jsonify({
        "balance": player["balance"], "username": player["username"],
        "first_name": player["first_name"], "level": player["level"],
        "xp": player["xp"], "ref_earnings": player["ref_earnings"],
        "league": player_league(player["balance"]),
        "prestiges": player["prestiges"],
        "wins": player["wins"],
    })


@app.route("/api/achievements")
def achievements():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    all_list = []
    for aid, data in ACHIEVEMENTS.items():
        all_list.append({
            "id": aid, "name": data["name"], "desc": data["desc"],
            "reward": data["reward"], "unlocked": aid in player["achievements"],
        })
    return jsonify({"achievements": all_list})


@app.route("/api/quests")
def quests():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    ensure_quests(player)
    return jsonify({"quests": player["quests"], "date": player["quests_date"]})


@app.route("/api/quests/claim", methods=["POST"])
def quests_claim():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    qid = data.get("quest_id")
    if not user_id or not qid: return jsonify({"error": "bad request"}), 400
    player = get_or_create_player(user_id)
    for q in player["quests"]:
        if q["id"] == qid:
            if q["claimed"]: return jsonify({"error": "Уже получено"}), 400
            if q["progress"] < q["target"]: return jsonify({"error": "Не выполнено"}), 400
            q["claimed"] = True
            player["balance"] += q["reward"]
            return jsonify({"status":"ok","reward":q["reward"],"balance":player["balance"]})
    return jsonify({"error": "Задание не найдено"}), 404


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

    # XP и уровни — 100 XP на уровень, максимум 1000
    xp_gain = 1 if mode == "normal" else (5 if mode == "lucky" else 15)
    old_level = player["level"]
    player["xp"] += xp_gain
    new_level = min(MAX_LEVEL, 1 + player["xp"] // 100)
    new_achievements = []

    if new_level > old_level:
        player["level"] = new_level
        # Награда за каждые 25 уровней (было 10, снижаем частоту)
        if new_level % 25 == 0 and new_level < MAX_LEVEL:
            reward = 5000 * (new_level // 25)
            player["balance"] += reward
            send_tg(user_id, f"🎉 <b>Уровень {new_level}!</b>\nПриз: <b>+{reward:,} ₽</b>".replace(",", " "))
        if new_level == 10:
            a = unlock_achievement(player, "level_10")
            if a: new_achievements.append(a)
        if new_level == 100:
            a = unlock_achievement(player, "level_100")
            if a: new_achievements.append(a)
        if new_level == 500:
            a = unlock_achievement(player, "level_500")
            if a: new_achievements.append(a)
        if new_level == MAX_LEVEL and player["wins"] == 0:
            player["wins"] += 1
            a = unlock_achievement(player, "level_1000")
            if a: new_achievements.append(a)

    add_quest_progress(player, "spins", 1)
    if rarity in ("РЕДКОЕ","ЭПИК","ЛЕГЕНДА","МИФ"):
        add_quest_progress(player, "rare", 1)
    if rarity == "ЭПИК": add_quest_progress(player, "epic", 1)
    if rarity == "ЛЕГЕНДА": add_quest_progress(player, "legend", 1)
    if rarity == "МИФ": add_quest_progress(player, "epic", 1)

    if player["total_spins"] == 1:
        a = unlock_achievement(player, "first_spin")
        if a: new_achievements.append(a)
    if player["total_spins"] == 10:
        a = unlock_achievement(player, "ten_spins")
        if a: new_achievements.append(a)
    if player["total_spins"] == 100:
        a = unlock_achievement(player, "hundred_spins")
        if a: new_achievements.append(a)
    if player["total_spins"] == 1000:
        a = unlock_achievement(player, "thousand_spins")
        if a: new_achievements.append(a)
    if rarity == "РЕДКОЕ":
        a = unlock_achievement(player, "first_rare")
        if a: new_achievements.append(a)
    if rarity == "ЭПИК":
        a = unlock_achievement(player, "first_epic")
        if a: new_achievements.append(a)
    if rarity == "ЛЕГЕНДА":
        a = unlock_achievement(player, "first_legend")
        if a: new_achievements.append(a)
    if rarity == "МИФ":
        a = unlock_achievement(player, "first_myth")
        if a: new_achievements.append(a)
        if player.get("referrer"):
            bonus = int(price * REF_MYTH_PERCENT)   # 5%
            ref = PLAYERS.get(player["referrer"])
            if ref:
                ref["balance"] += bonus
                ref["ref_earnings"] += bonus
                send_tg(player["referrer"], f"💎 Друг выбил МИФ! +{bonus:,} ₽".replace(",", " "))

    if player["balance"] >= 1_000_000:
        a = unlock_achievement(player, "millionaire")
        if a: new_achievements.append(a)
    if player["balance"] >= 10_000_000:
        a = unlock_achievement(player, "ten_millions")
        if a: new_achievements.append(a)
    if player["balance"] >= 100_000_000:
        a = unlock_achievement(player, "hundred_millions")
        if a: new_achievements.append(a)

    for a in new_achievements:
        send_tg(user_id, f"🏆 <b>Достижение!</b>\n\n«{a['name']}»\n{a['desc']}\nНаграда: <b>+{a['reward']:,} ₽</b>".replace(",", " "))

    return jsonify({
        "balance": player["balance"], "level": player["level"], "xp": player["xp"],
        "new_achievements": new_achievements,
    })


@app.route("/api/transfer", methods=["POST"])
def transfer():
    data = request.get_json(force=True) or {}
    from_id = data.get("user_id")
    to_username = (data.get("to_username") or "").strip()
    amount = data.get("amount")
    if not from_id: return jsonify({"error": "нет отправителя"}), 400
    if not to_username: return jsonify({"error": "укажи username"}), 400
    try: amount = int(amount)
    except: return jsonify({"error": "сумма должна быть числом"}), 400
    if amount <= 0: return jsonify({"error": "сумма должна быть больше 0"}), 400
    sender = get_or_create_player(from_id)
    to_id, receiver = find_player_by_username(to_username)
    if not receiver: return jsonify({"error": "Игрок не найден"}), 404
    if to_id == str(from_id): return jsonify({"error": "нельзя себе"}), 400
    if sender["balance"] < amount: return jsonify({"error": "Недостаточно"}), 400
    sender["balance"] -= amount
    receiver["balance"] += amount
    send_tg(to_id, f"💰 <b>Вам перевели {amount:,} ₽</b>\nОт: @{sender['username'] or 'игрок'}".replace(",", " "))
    send_tg(from_id, f"✅ <b>Перевод отправлен</b>\nКому: @{receiver['username'] or 'игрок'}\nСумма: {amount:,} ₽".replace(",", " "))

    a = unlock_achievement(sender, "first_transfer")
    return jsonify({"status":"ok","from_balance":sender["balance"],
                    "to_username":receiver["username"],"amount":amount,
                    "new_achievement": a})


@app.route("/api/top")
def top():
    sp = sorted(PLAYERS.items(), key=lambda x: x[1]["balance"], reverse=True)
    return jsonify({"top": [
        {"user_id": uid, "balance": p["balance"], "username": p["username"],
         "first_name": p["first_name"], "photo": p["photo"],
         "league": player_league(p["balance"]), "level": p["level"]}
        for uid, p in sp[:10]
    ]})


@app.route("/api/daily/status")
def daily_status():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    now = int(time.time()); one_day = 86400; today = now // one_day
    claims = set(ts // one_day for ts in player.get("daily_claims", []))

    streak = 0
    if today in claims:
        for i in range(7):
            if (today - i) in claims: streak += 1
            else: break
    else:
        for i in range(1, 8):
            if (today - i) in claims: streak += 1
            else: break

    if streak >= 7: streak = 0

    days = []
    for i in range(7):
        claimed = i < streak
        can_claim = (i == streak) and (today not in claims) and (streak < 7)
        days.append({
            "day": i + 1, "reward": DAILY_REWARDS[i],
            "claimed": claimed, "today": can_claim, "can_claim": can_claim,
        })
    return jsonify({"days": days, "streak": streak, "today_claimed": today in claims})


@app.route("/api/daily/claim", methods=["POST"])
def daily_claim():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    now = int(time.time()); one_day = 86400; today = now // one_day
    claims = set(ts // one_day for ts in player.get("daily_claims", []))
    if today in claims: return jsonify({"error": "Сегодня уже забрал"}), 400

    streak = 0
    for i in range(1, 8):
        if (today - i) in claims: streak += 1
        else: break
    if streak >= 7:
        player["daily_claims"] = []
        streak = 0

    reward = DAILY_REWARDS[min(streak, 6)]
    player["balance"] += reward
    player["daily_claims"].append(now)
    player["daily_streak"] = streak + 1

    send_tg(user_id, f"🎁 Ежедневка: +{reward:,} ₽".replace(",", " "))

    a1 = unlock_achievement(player, "first_daily")
    a2 = None
    if player["daily_streak"] >= 7:
        a2 = unlock_achievement(player, "week_streak")

    return jsonify({"status":"ok","reward":reward,"balance":player["balance"],
                    "streak":player["daily_streak"],
                    "new_achievements":[x for x in (a1,a2) if x]})


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


@app.route("/api/upgrade_used", methods=["POST"])
def upgrade_used():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    add_quest_progress(player, "upgraded", 1)
    return jsonify({"ok": True})


@app.route("/api/prestige", methods=["POST"])
def prestige():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    if player["level"] < MAX_LEVEL:
        return jsonify({"error": f"Нужен {MAX_LEVEL} уровень"}), 400
    player["prestiges"] += 1
    player["level"] = 1
    player["xp"] = 0
    player["balance"] = START_BALANCE * (2 ** player["prestiges"])
    return jsonify({"status":"ok","prestiges":player["prestiges"],"balance":player["balance"]})


@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    if "message" in data:
        msg = data["message"]; chat_id = msg["chat"]["id"]
        text = msg.get("text",""); user = msg.get("from", {})
        if text.startswith("/start"):
            get_or_create_player(chat_id, user.get("username"), user.get("first_name"))
            player = PLAYERS[str(chat_id)]
            parts = text.split()
            if len(parts) > 1 and parts[1].startswith("ref_"):
                ref_id = parts[1][4:]
                if not player["referrer"] and ref_id != str(chat_id):
                    player["referrer"] = ref_id
                    ref = PLAYERS.get(ref_id)
                    if ref:
                        ref["balance"] += REF_START_BONUS
                        ref["ref_earnings"] += REF_START_BONUS
                        ref["referral_count"] = ref.get("referral_count", 0) + 1
                        send_tg(ref_id, f"🎉 <b>По твоей ссылке зашёл друг!</b>\n+{REF_START_BONUS:,} ₽".replace(",", " "))
                        a = unlock_achievement(ref, "first_referral")
                        if a:
                            send_tg(ref_id, f"🏆 «{a['name']}» +{a['reward']:,} ₽".replace(",", " "))
                        if ref.get("referral_count", 0) >= 10:
                            a = unlock_achievement(ref, "ten_referrals")
                            if a:
                                send_tg(ref_id, f"🏆 «{a['name']}» +{a['reward']:,} ₽".replace(",", " "))

            welcome = (
                "🎰 <b>Добро пожаловать в «Крути номер»!</b>\n\n"
                "Крути SIM-карты, выбивай редкие номера и богатей!\n\n"
                "💰 <b>Что делать:</b>\n"
                "• Выбирай страну\n"
                "• Крути в трёх режимах\n"
                "• Улучшай номера\n"
                "• Выполняй задания и достижения\n"
                "• Иди к 1000 уровню — это победа!\n\n"
                "🏆 <b>Бонусы:</b>\n"
                "• +25к за друга\n"
                "• +5% от его МИФов\n"
                "• Награды за достижения\n\n"
                "Жми кнопку 👇"
            )
            send_tg(chat_id, welcome, with_button=True)
    return jsonify({"ok": True})


@app.route("/api/set_webhook")
def set_webhook():
    url = request.args.get("url", "").rstrip("/")
    if not url: return jsonify({"error":"нужен ?url=https://..."}), 400
    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                      json={"url": f"{url}/webhook/{BOT_TOKEN}"}, timeout=10)
    return jsonify(r.json())


HOURLY_MSGS = [
    "🎰 Загляни в игру — может твой день! /start",
    "💎 Друзья крутят номера. Ты с ними? /start",
    "🎁 Ежедневка ждёт! /start",
    "🏆 Идёшь к 1000 уровню? Не сдавайся! /start",
    "💰 Что-то давно не крутил. Заходи! /start",
    "🔥 Один оборот — и ты миллионер? /start",
    "👥 Приглашай друзей: +25к за каждого! /start",
]
_last_hour = [0]
def broadcaster():
    while True:
        try:
            now = int(time.time()); cur = now // 3600
            if _last_hour[0] != cur:
                _last_hour[0] = cur
                msg = random.choice(HOURLY_MSGS)
                for uid, p in list(PLAYERS.items()):
                    if now - p.get("last_seen", 0) < 3 * 86400:
                        send_tg(uid, msg)
        except Exception as e:
            print("Broadcast err:", e)
        time.sleep(600)
threading.Thread(target=broadcaster, daemon=True).start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
