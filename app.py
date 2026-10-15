# ============================================================
#  SIM SPINNER — сервер v0.0.6
# ============================================================

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os, time, random, threading, requests, string

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8688292241:AAEpB6R9ndFLFCjUOs_vC0gmAJZwg_TUUMw"
BOT_USERNAME = "Sim_moner_zyza_ymer_bot"
START_BALANCE = 50000
REF_START_BONUS = 25000
REF_MYTH_PERCENT = 0.05
DAILY_REWARDS = [3000, 5000, 7000, 10000, 13000, 17000, 22000]
MAX_LEVEL = 1000

# Секретное слово для выдачи одноразовых доступов
SECRET_WORD = "дианаматвей"

PLAYERS = {}
ADMINS = {}          # {user_id: {"login": "...", "password": "..."}}  — постоянные
ONE_TIME = {}        # {user_id: {"login": "...", "password": "...", "used": False}}
LOGS = []            # список логов для админа
SEASON_START = int(time.time())
GOLDEN_UNTIL = 0     # timestamp конца золотого часа (глобально)

# ============================================================
#  ДОСТИЖЕНИЯ
# ============================================================
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
    "level_1000":   {"name": "ПОБЕДИТЕЛЬ",      "desc": "Достигни 1000 уровня",           "reward": 3000000},
    "kaboom":       {"name": "БУМ!",             "desc": "Выбей пасхалку 420420420",       "reward": 1000000},
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


def add_log(uid, text):
    """Записать лог для админа."""
    LOGS.append({"ts": int(time.time()), "uid": str(uid), "text": text})
    if len(LOGS) > 500:
        LOGS[:] = LOGS[-500:]


def today_key(): return int(time.time()) // 86400


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
            "banned": False,
            "ban_reason": "",
            "best_number": None,
            "history": [],           # последние 20 прокруток
            "spent_countries": {},   # {country_id: count}
            "spent_operators": {},   # {operator: count}
            "daily_balance": [],     # [{ts, balance}] для графика
            "x2_until": 0,           # персональный x2 (выдал админ)
            "season_notified": False,
        }
    else:
        if username: PLAYERS[user_id]["username"] = username.lstrip("@").lower()
        if first_name: PLAYERS[user_id]["first_name"] = first_name
        if photo: PLAYERS[user_id]["photo"] = photo
        PLAYERS[user_id]["last_seen"] = int(time.time())
    p = PLAYERS[user_id]
    ensure_quests(p)
    # Снимок баланса для графика (раз в сутки)
    today = today_key()
    if not p["daily_balance"] or p["daily_balance"][-1].get("day") != today:
        p["daily_balance"].append({"day": today, "balance": p["balance"]})
        if len(p["daily_balance"]) > 14:
            p["daily_balance"] = p["daily_balance"][-14:]
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


def is_golden_hour():
    return int(time.time()) < GOLDEN_UNTIL


# ============================================================
#  БАЗОВЫЕ РУЧКИ
# ============================================================
@app.route("/")
def index(): return send_file("index.html")


@app.route("/api/ping")
def ping(): return jsonify({"status": "ok", "golden": is_golden_hour(), "golden_until": GOLDEN_UNTIL})


@app.route("/api/debug")
def debug():
    try:
        info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo", timeout=5).json()
    except Exception as e: info = {"error": str(e)}
    return jsonify({"webhook": info, "players": len(PLAYERS), "golden": is_golden_hour()})


@app.route("/api/balance")
def balance():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id, request.args.get("username"),
                                  request.args.get("first_name"), request.args.get("photo"))
    if player.get("banned"):
        return jsonify({"banned": True, "reason": player.get("ban_reason", "")}), 403
    return jsonify({
        "balance": player["balance"], "username": player["username"],
        "first_name": player["first_name"], "level": player["level"],
        "xp": player["xp"], "ref_earnings": player["ref_earnings"],
        "league": player_league(player["balance"]),
        "prestiges": player["prestiges"], "wins": player["wins"],
        "golden": is_golden_hour(), "golden_until": GOLDEN_UNTIL,
        "x2_until": player.get("x2_until", 0),
    })


@app.route("/api/achievements")
def achievements():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    all_list = []
    for aid, data in ACHIEVEMENTS.items():
        all_list.append({"id": aid, "name": data["name"], "desc": data["desc"],
                         "reward": data["reward"], "unlocked": aid in player["achievements"]})
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
    user_id = data.get("user_id"); qid = data.get("quest_id")
    if not user_id or not qid: return jsonify({"error": "bad request"}), 400
    player = get_or_create_player(user_id)
    for q in player["quests"]:
        if q["id"] == qid:
            if q["claimed"]: return jsonify({"error": "Уже получено"}), 400
            if q["progress"] < q["target"]: return jsonify({"error": "Не выполнено"}), 400
            q["claimed"] = True
            player["balance"] += q["reward"]
            add_log(user_id, f"Забрал задание {qid} +{q['reward']}")
            return jsonify({"status":"ok","reward":q["reward"],"balance":player["balance"]})
    return jsonify({"error": "Задание не найдено"}), 404


# ============================================================
#  СТАТИСТИКА
# ============================================================
@app.route("/api/stats")
def stats():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    # Любимая страна и оператор
    fav_country = max(player.get("spent_countries", {}).items(), key=lambda x: x[1], default=("—", 0))
    fav_op = max(player.get("spent_operators", {}).items(), key=lambda x: x[1], default=("—", 0))
    avg_check = (player["stats"]["earned"] / player["stats"]["sold"]) if player["stats"].get("sold") else 0
    return jsonify({
        "spins": player["total_spins"],
        "sold": player["stats"].get("sold", 0),
        "earned": player["stats"].get("earned", 0),
        "best_price": player["stats"].get("best_price", 0),
        "favorite_country": fav_country[0],
        "favorite_operator": fav_op[0],
        "avg_check": int(avg_check),
        "best_number": player.get("best_number"),
        "history": player.get("history", [])[-20:],
        "daily_balance": player.get("daily_balance", [])[-7:],
    })


# ============================================================
#  ПРОКРУТКА
# ============================================================
@app.route("/api/spin", methods=["POST"])
def spin():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    mode = data.get("mode", "normal")
    price = int(data.get("price", 0))
    cost = int(data.get("cost", 0))
    rarity = data.get("rarity", "")
    country_id = data.get("country_id", "")
    operator = data.get("operator", "")
    number = data.get("number", "")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    if player.get("banned"):
        return jsonify({"error": "Вы забанены", "reason": player.get("ban_reason","")}), 403
    if player["balance"] < cost:
        return jsonify({"error": "Недостаточно средств", "balance": player["balance"]}), 400

    # Золотой час / персональный x2
    mult = 1.0
    if is_golden_hour(): mult = 2.0
    if player.get("x2_until", 0) > int(time.time()): mult = max(mult, 2.0)
    final_price = int(price * mult)

    player["balance"] -= cost
    player["balance"] += final_price
    player["total_spins"] += 1
    if not player["stats"].get("sold"): player["stats"]["sold"] = 0
    if not player["stats"].get("earned"): player["stats"]["earned"] = 0
    if not player["stats"].get("best_price"): player["stats"]["best_price"] = 0
    if rarity not in ("ЭПИК","ЛЕГЕНДА","МИФ"):
        player["stats"]["sold"] += 1
        player["stats"]["earned"] += final_price
    if final_price > player["stats"]["best_price"]:
        player["stats"]["best_price"] = final_price

    # Статистика стран и операторов
    if country_id:
        player["spent_countries"][country_id] = player["spent_countries"].get(country_id, 0) + 1
    if operator:
        player["spent_operators"][operator] = player["spent_operators"].get(operator, 0) + 1

    # Лучший номер
    if number and (not player["best_number"] or final_price > player["best_number"].get("price", 0)):
        player["best_number"] = {"number": number, "price": final_price, "rarity": rarity,
                                 "country_id": country_id, "operator": operator}

    # История
    player["history"].append({
        "ts": int(time.time()), "number": number, "price": final_price,
        "rarity": rarity, "mode": mode, "country_id": country_id,
        "operator": operator, "sold": rarity not in ("ЭПИК","ЛЕГЕНДА","МИФ"),
        "x2": mult > 1,
    })
    if len(player["history"]) > 20:
        player["history"] = player["history"][-20:]

    # XP
    xp_gain = 1 if mode == "normal" else (5 if mode == "lucky" else 15)
    old_level = player["level"]
    player["xp"] += xp_gain
    new_level = min(MAX_LEVEL, 1 + player["xp"] // 100)
    new_achievements = []
    if new_level > old_level:
        player["level"] = new_level
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
            bonus = int(final_price * REF_MYTH_PERCENT)
            ref = PLAYERS.get(player["referrer"])
            if ref:
                ref["balance"] += bonus
                ref["ref_earnings"] += bonus
                send_tg(player["referrer"], f"💎 Друг выбил МИФ! +{bonus:,} ₽".replace(",", " "))

    if number == "420420420":
        a = unlock_achievement(player, "kaboom")
        if a: new_achievements.append(a)

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

    # Обновляем дневной снимок баланса
    today = today_key()
    if player["daily_balance"] and player["daily_balance"][-1].get("day") == today:
        player["daily_balance"][-1]["balance"] = player["balance"]

    return jsonify({
        "balance": player["balance"], "level": player["level"], "xp": player["xp"],
        "new_achievements": new_achievements,
        "final_price": final_price, "mult": mult,
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
    if sender.get("banned"): return jsonify({"error": "Вы забанены"}), 403
    to_id, receiver = find_player_by_username(to_username)
    if not receiver: return jsonify({"error": "Игрок не найден"}), 404
    if to_id == str(from_id): return jsonify({"error": "нельзя себе"}), 400
    if sender["balance"] < amount: return jsonify({"error": "Недостаточно"}), 400
    sender["balance"] -= amount
    receiver["balance"] += amount
    send_tg(to_id, f"💰 <b>Вам перевели {amount:,} ₽</b>\nОт: @{sender['username'] or 'игрок'}".replace(",", " "))
    send_tg(from_id, f"✅ <b>Перевод отправлен</b>\nКому: @{receiver['username'] or 'игрок'}\nСумма: {amount:,} ₽".replace(",", " "))
    add_log(from_id, f"Перевод @{receiver['username']} {amount}₽")
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
        days.append({"day": i + 1, "reward": DAILY_REWARDS[i],
                     "claimed": claimed, "today": can_claim, "can_claim": can_claim})
    return jsonify({"days": days, "streak": streak, "today_claimed": today in claims})


@app.route("/api/daily/claim", methods=["POST"])
def daily_claim():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    if player.get("banned"): return jsonify({"error": "Вы забанены"}), 403
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
    return jsonify({"ref_earnings": player["ref_earnings"],
                    "ref_count": len(refs),
                    "ref_link": f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"})


@app.route("/api/upgrade_used", methods=["POST"])
def upgrade_used():
    data = request.get_json(force=True) or {}
    user_id = data.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    player = get_or_create_player(user_id)
    add_quest_progress(player, "upgraded", 1)
    return jsonify({"ok": True})


# ============================================================
#  АДМИН-ПАНЕЛЬ
# ============================================================
def check_admin(login, password):
    """Проверяет, есть ли админ с такими данными. Возвращает user_id или None."""
    for uid, data in ADMINS.items():
        if data["login"] == login and data["password"] == password:
            return uid
    # Проверяем одноразовые (если не использованы)
    for uid, data in ONE_TIME.items():
        if data["login"] == login and data["password"] == password and not data["used"]:
            return uid
    return None


@app.route("/api/admin/access", methods=["POST"])
def admin_access():
    """Получить доступ в админ-панель через одноразовый логин/пароль или постоянный."""
    data = request.get_json(force=True) or {}
    login = data.get("login", "")
    password = data.get("password", "")
    user_id = data.get("user_id")
    action = data.get("action", "login")

    if action == "set_permanent":
        # Первый вход — сохраняем постоянный логин/пароль
        if not login or not password:
            return jsonify({"error": "логин и пароль обязательны"}), 400
        ADMINS[str(user_id)] = {"login": login, "password": password}
        add_log(user_id, f"Установил постоянный админ-логин: {login}")
        return jsonify({"status": "ok", "admin": True})

    # Обычный вход
    uid = check_admin(login, password)
    if not uid:
        return jsonify({"error": "Неверный логин или пароль"}), 401
    # Если вход по одноразовому — помечаем использованным
    if uid in ONE_TIME and ONE_TIME[uid]["login"] == login:
        ONE_TIME[uid]["used"] = True
    add_log(uid, f"Вход в админку: {login}")
    return jsonify({"status": "ok", "admin": True, "admin_id": uid})


@app.route("/api/admin/players")
def admin_players():
    """Все игроки + онлайн статус."""
    now = int(time.time())
    result = []
    for uid, p in PLAYERS.items():
        online = (now - p.get("last_seen", 0)) < 300  # 5 минут — считаем онлайн
        result.append({
            "user_id": uid, "username": p.get("username", ""),
            "first_name": p.get("first_name", ""),
            "balance": p["balance"], "level": p["level"],
            "banned": p.get("banned", False),
            "online": online,
            "photo": p.get("photo", ""),
        })
    # Сначала онлайн, потом по балансу
    result.sort(key=lambda x: (not x["online"], -x["balance"]))
    return jsonify({"players": result, "total": len(result)})


@app.route("/api/admin/player/<uid>")
def admin_player(uid):
    p = PLAYERS.get(str(uid))
    if not p: return jsonify({"error": "не найден"}), 404
    return jsonify({
        "user_id": uid, "username": p.get("username",""),
        "first_name": p.get("first_name",""),
        "balance": p["balance"], "level": p["level"],
        "xp": p["xp"], "banned": p.get("banned", False),
        "ban_reason": p.get("ban_reason",""),
        "total_spins": p["total_spins"],
        "photo": p.get("photo",""),
    })


@app.route("/api/admin/set_balance", methods=["POST"])
def admin_set_balance():
    data = request.get_json(force=True) or {}
    uid = data.get("user_id")
    amount = int(data.get("amount", 0))
    admin_id = data.get("admin_id")
    if not uid: return jsonify({"error": "no user_id"}), 400
    p = PLAYERS.get(str(uid))
    if not p: return jsonify({"error": "не найден"}), 404
    p["balance"] = amount
    add_log(admin_id, f"Установил баланс {uid}: {amount}")
    send_tg(uid, f"⚙️ Ваш баланс изменён админом: <b>{amount:,} ₽</b>".replace(",", " "))
    return jsonify({"status": "ok", "balance": amount})


@app.route("/api/admin/set_username", methods=["POST"])
def admin_set_username():
    data = request.get_json(force=True) or {}
    uid = data.get("user_id"); username = data.get("username","").strip()
    admin_id = data.get("admin_id")
    p = PLAYERS.get(str(uid))
    if not p: return jsonify({"error": "не найден"}), 404
    p["username"] = username.lstrip("@").lower()
    add_log(admin_id, f"Сменил username {uid}: {username}")
    return jsonify({"status": "ok", "username": p["username"]})


@app.route("/api/admin/ban", methods=["POST"])
def admin_ban():
    data = request.get_json(force=True) or {}
    uid = data.get("user_id"); reason = data.get("reason", "Нарушение правил")
    admin_id = data.get("admin_id")
    action = data.get("action", "ban")  # ban | unban
    p = PLAYERS.get(str(uid))
    if not p: return jsonify({"error": "не найден"}), 404
    if action == "ban":
        p["banned"] = True
        p["ban_reason"] = reason
        send_tg(uid, f"🚫 <b>Вы забанены</b>\nПричина: {reason}")
        add_log(admin_id, f"Забанил {uid}: {reason}")
    else:
        p["banned"] = False
        p["ban_reason"] = ""
        send_tg(uid, "✅ <b>Вы разбанены</b>")
        add_log(admin_id, f"Разбанил {uid}")
    return jsonify({"status": "ok", "banned": p["banned"]})


@app.route("/api/admin/x2_all", methods=["POST"])
def admin_x2_all():
    """Запустить x2 всем на 30 минут."""
    global GOLDEN_UNTIL
    data = request.get_json(force=True) or {}
    admin_id = data.get("admin_id")
    GOLDEN_UNTIL = int(time.time()) + 30 * 60
    for uid in PLAYERS.keys():
        send_tg(uid, "🔥 <b>ЗОЛОТОЙ ЧАС!</b>\n\n30 минут ×2 к цене всех номеров!\nЗаходи скорее! 🎰")
    add_log(admin_id, "Запустил глобальный x2 на 30 минут")
    return jsonify({"status": "ok", "until": GOLDEN_UNTIL})


@app.route("/api/admin/season_reset", methods=["POST"])
def admin_season_reset():
    """Полное обнуление сезона."""
    global PLAYERS, SEASON_START
    data = request.get_json(force=True) or {}
    admin_id = data.get("admin_id")
    # Сбрасываем всех игроков
    for uid, p in PLAYERS.items():
        p["balance"] = START_BALANCE
        p["level"] = 1
        p["xp"] = 0
        p["achievements"] = []
        p["quests"] = []
        p["quests_date"] = 0
        p["daily_claims"] = []
        p["daily_streak"] = 0
        p["best_number"] = None
        p["history"] = []
        p["stats"] = {"sold": 0, "earned": 0, "best_price": 0}
        p["total_spins"] = 0
        p["spent_countries"] = {}
        p["spent_operators"] = {}
        p["daily_balance"] = []
        p["season_notified"] = False
        # Уведомляем
        send_tg(uid, "🎬 <b>СЕЗОН ЗАВЕРШЁН!</b>\n\nВсе данные обнулены. Новый сезон начался!\nЗаходи и начинай сначала 🎰")
    SEASON_START = int(time.time())
    add_log(admin_id, "Обнулил сезон для всех игроков")
    return jsonify({"status": "ok", "season_start": SEASON_START})


@app.route("/api/admin/logs")
def admin_logs():
    return jsonify({"logs": LOGS[-100:][::-1]})


@app.route("/api/admin/give_bonus", methods=["POST"])
def admin_give_bonus():
    """Начислить всем бонус."""
    data = request.get_json(force=True) or {}
    amount = int(data.get("amount", 0))
    admin_id = data.get("admin_id")
    if amount <= 0: return jsonify({"error": "сумма должна быть > 0"}), 400
    count = 0
    for uid, p in PLAYERS.items():
        p["balance"] += amount
        send_tg(uid, f"🎁 <b>Бонус от админа!</b>\n+{amount:,} ₽".replace(",", " "))
        count += 1
    add_log(admin_id, f"Выдал всем бонус +{amount}")
    return jsonify({"status": "ok", "count": count})


@app.route("/api/admin/check_season")
def check_season():
    """Фронт запрашивает — не было ли сброса сезона, пока игрок не заходил."""
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "no user_id"}), 400
    p = PLAYERS.get(str(user_id))
    if not p: return jsonify({"season_reset": False})
    if not p.get("season_notified") and p.get("balance") == START_BALANCE and p.get("level") == 1 and not p.get("achievements"):
        # Проверяем, был ли сброс (например, by reset)
        pass
    return jsonify({"season_reset": False, "season_start": SEASON_START})


# ============================================================
#  WEBHOOK (бот)
# ============================================================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    if "message" in data:
        msg = data["message"]; chat_id = msg["chat"]["id"]
        text = msg.get("text","").strip(); user = msg.get("from", {})
        username = user.get("username", "")
        fname = user.get("first_name", "Игрок")

        # /adm — начало выдачи админ-доступа
        if text == "/adm":
            send_tg(chat_id, "🔑 <b>Секретное слово?</b>\n\nВведите секретное слово одним сообщением.")
            # Запоминаем, что ждём слово
            p = get_or_create_player(chat_id, username, fname)
            p["awaiting_secret"] = True
            return jsonify({"ok": True})

        # Если ждём секретное слово
        p = PLAYERS.get(str(chat_id))
        if p and p.get("awaiting_secret"):
            p["awaiting_secret"] = False
            if text.lower() == SECRET_WORD:
                # Генерируем одноразовый логин/пароль
                login = "".join(random.choices(string.digits, k=6))
                password = "".join(random.choices(string.digits, k=6))
                ONE_TIME[str(chat_id)] = {"login": login, "password": password, "used": False}
                send_tg(chat_id,
                    f"🔓 <b>Доступ в админ-панель</b>\n\n"
                    f"Логин: <code>{login}</code>\n"
                    f"Пароль: <code>{password}</code>\n\n"
                    f"Введите их в игре во вкладке Настройки → Разработчик → Вход в админ-панель.\n"
                    f"⚠️ Они одноразовые. Если уже ввели — устанавливайте постоянный логин/пароль."
                )
            else:
                send_tg(chat_id, "❌ Неверное секретное слово.")
            return jsonify({"ok": True})

        # /start
        if text.startswith("/start"):
            get_or_create_player(chat_id, username, fname)
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
                "• Смотри статистику и график баланса\n"
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


# ============================================================
#  РАССЫЛКА + ЗОЛОТОЙ ЧАС
# ============================================================
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
_last_golden_day = [0]
def broadcaster():
    global GOLDEN_UNTIL
    while True:
        try:
            now = int(time.time())
            cur = now // 3600
            # Ежечасовая рассылка
            if _last_hour[0] != cur:
                _last_hour[0] = cur
                msg = random.choice(HOURLY_MSGS)
                for uid, p in list(PLAYERS.items()):
                    if now - p.get("last_seen", 0) < 3 * 86400:
                        send_tg(uid, msg)
            # Золотой час раз в сутки — автоматически в 19:00
            today = now // 86400
            if _last_golden_day[0] != today and time.localtime().tm_hour == 19:
                _last_golden_day[0] = today
                GOLDEN_UNTIL = now + 30 * 60
                for uid in PLAYERS.keys():
                    send_tg(uid, "🔥 <b>ЗОЛОТОЙ ЧАС!</b>\n\n30 минут ×2 к цене всех номеров!\nЗаходи скорее! 🎰")
        except Exception as e:
            print("Broadcast err:", e)
        time.sleep(600)
threading.Thread(target=broadcaster, daemon=True).start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
