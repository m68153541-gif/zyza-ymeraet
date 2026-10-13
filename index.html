# ============================================================
#  SIM SPINNER — «Крути номер»
#  Запуск:  python app.py
#  Открыть: http://127.0.0.1:5000
# ============================================================

from flask import Flask, render_template_string, jsonify, request
import random
from collections import Counter
import os

app = Flask(__name__)


# ============================================================
#  СТРАНЫ И ОПЕРАТОРЫ
# ============================================================
COUNTRIES = {
    "Африка": {"code": "+2", "flag": "🌍", "rarity": 0.20,
        "operators": {"MTN": 1.0, "Airtel": 1.1, "Safaricom": 1.3, "Vodacom": 1.2}},
    "Пакистан": {"code": "+92", "flag": "🇵🇰", "rarity": 0.30,
        "operators": {"Jazz": 1.0, "Zong": 1.2, "Ufone": 1.1, "Telenor": 1.3}},
    "Индия": {"code": "+91", "flag": "🇮🇳", "rarity": 0.45,
        "operators": {"Jio": 1.0, "Airtel": 1.2, "Vi": 1.1, "BSNL": 1.3}},
    "Казахстан": {"code": "+77", "flag": "🇰🇿", "rarity": 0.65,
        "operators": {"Beeline KZ": 1.0, "Activ": 1.2, "Tele2 KZ": 1.1, "Kcell": 1.3}},
    "Россия": {"code": "+7", "flag": "🇷🇺", "rarity": 0.90,
        "operators": {"Т2": 1.0, "МТС": 1.30, "МегаФон": 1.45, "Билайн": 1.60, "Yota": 1.50, "СберМобайл": 1.40}},
    "Германия": {"code": "+49", "flag": "🇩🇪", "rarity": 1.30,
        "operators": {"Telekom": 1.0, "Vodafone": 1.2, "O2": 1.1, "1&1": 1.3}},
    "Великобритания": {"code": "+44", "flag": "🇬🇧", "rarity": 1.40,
        "operators": {"EE": 1.0, "O2": 1.1, "Vodafone": 1.2, "Three": 1.3}},
    "США": {"code": "+1", "flag": "🇺🇸", "rarity": 1.70,
        "operators": {"Verizon": 1.0, "AT&T": 1.2, "T-Mobile": 1.15, "Sprint": 1.3}},
    "Япония": {"code": "+81", "flag": "🇯🇵", "rarity": 1.90,
        "operators": {"NTT Docomo": 1.0, "SoftBank": 1.2, "au": 1.15, "Rakuten": 1.3}},
    "ОАЭ": {"code": "+971", "flag": "🇦🇪", "rarity": 2.10,
        "operators": {"Etisalat": 1.0, "du": 1.2}},
    "Сингапур": {"code": "+65", "flag": "🇸🇬", "rarity": 2.20,
        "operators": {"Singtel": 1.0, "StarHub": 1.15, "M1": 1.25}},
    "Швейцария": {"code": "+41", "flag": "🇨🇭", "rarity": 2.30,
        "operators": {"Swisscom": 1.0, "Sunrise": 1.2, "Salt": 1.3}},
    "Люксембург": {"code": "+352", "flag": "🇱🇺", "rarity": 2.40,
        "operators": {"POST": 1.0, "Tango": 1.15, "Orange LU": 1.25}},
    "Монако": {"code": "+377", "flag": "🇲🇨", "rarity": 2.50,
        "operators": {"Monaco Telecom": 1.0, "Orange MC": 1.2}},
    "Катар": {"code": "+974", "flag": "🇶🇦", "rarity": 2.60,
        "operators": {"Ooredoo": 1.0, "Vodafone QA": 1.2}},
}


# ============================================================
#  ОЦЕНКА «КРАСОТЫ»
# ============================================================
def beauty_score(number):
    digits = list(number)
    score = 1.0

    repeats = 1
    max_repeat = 1
    for i in range(1, len(digits)):
        if digits[i] == digits[i-1]:
            repeats += 1
            max_repeat = max(max_repeat, repeats)
        else:
            repeats = 1
    if max_repeat >= 8: score += 6.5
    elif max_repeat >= 6: score += 4.0
    elif max_repeat >= 5: score += 2.4
    elif max_repeat >= 4: score += 1.2
    elif max_repeat == 3: score += 0.50
    elif max_repeat == 2: score += 0.18

    if len(set(digits)) == 1: score += 9.0
    if number == number[::-1]: score += 2.8
    if number in ("123456789", "987654321"): score += 7.5

    cnt = Counter(digits)
    most = cnt.most_common(1)[0][1]
    if most >= 6: score += 1.8
    elif most == 5: score += 0.9
    elif most == 4: score += 0.35
    elif most == 3: score += 0.10

    for m in ["777777","888888","999999","000000","123456","654321"]:
        if m in number: score += 3.5
    for m in ["7777","8888","9999","0000","777","888","999","000","111","222","555","666"]:
        if m in number: score += 1.0

    if number.startswith("007"): score += 0.7
    if number[0] == number[-1]: score += 0.20
    zeros = digits.count("0")
    if zeros >= 5: score += 1.4
    elif zeros >= 4: score += 0.65
    elif zeros >= 3: score += 0.22
    if number[:2] in ("77","88","99","00","11","22"): score += 0.25
    if len(set(digits)) >= 8: score -= 0.05

    return round(score, 2)


RARITIES = [
    (0.00, "МУСОР",     0.20, "r-trash",    "rar-trash"),
    (1.05, "ОБЫЧНОЕ",   0.60, "r-common",   "rar-common"),
    (1.35, "НЕОБЫЧНОЕ", 1.20, "r-uncommon", "rar-uncommon"),
    (1.80, "РЕДКОЕ",    2.50, "r-rare",     "rar-rare"),
    (2.60, "ЭПИК",      6.00, "r-epic",     "rar-epic"),
    (4.20, "ЛЕГЕНДА",  14.00, "r-legend",   "rar-legend"),
    (7.00, "МИФ",      30.00, "r-myth",     "rar-myth"),
]
KEEP_FROM = ("ЭПИК", "ЛЕГЕНДА", "МИФ")


def get_rarity(beauty):
    r = RARITIES[0]
    for item in RARITIES:
        if beauty >= item[0]: r = item
    return r[1], r[2], r[3], r[4]


def make_number(beauty, country, opmult):
    name, mult, cls, card = get_rarity(beauty)
    price = int(40 * country["rarity"] * opmult * beauty * mult)
    price = max(price, 5)
    return price, name, mult, cls, card


# ============================================================
#  ГЕНЕРАЦИЯ
# ============================================================
def generate_pattern(mode="normal"):
    if mode == "super":
        patterns = ["repeat_high","repeat_mid","sequence","zeros","magic","palindrome"]
        weights  = [1, 3, 2, 2, 5, 2]
    else:
        patterns = ["repeat_mid","magic","zeros","sequence","palindrome","double"]
        weights  = [3, 5, 3, 1, 1, 3]
    pattern = random.choices(patterns, weights=weights, k=1)[0]
    def rand(n): return "".join(random.choice("0123456789") for _ in range(n))
    if pattern == "repeat_high": return random.choice("0123456789") * 9
    if pattern == "repeat_mid":  return random.choice("0123456789") * 6 + rand(3)
    if pattern == "sequence":    return "123456789" if random.random() < 0.5 else "987654321"
    if pattern == "zeros":       return random.choice("123456789") + random.choice("0123456789") + "0" * 7
    if pattern == "magic":
        magic = random.choice(["777","888","999","000","111","222","555","666"])
        return magic + rand(6) if random.random() < 0.5 else rand(6) + magic
    if pattern == "palindrome":
        half = rand(4); mid = random.choice("0123456789")
        return half + mid + half[::-1]
    if pattern == "double":
        s = ""
        for _ in range(4):
            d = random.choice("0123456789"); s += d + d
        return s + random.choice("0123456789")
    return rand(9)


def weighted_country(mode="normal"):
    names = list(COUNTRIES.keys())
    weights = []
    for c in names:
        r = COUNTRIES[c]["rarity"]
        if mode == "super": w = 1.0 / (r ** 0.4)
        elif mode == "lucky": w = 1.0 / (r ** 0.7)
        else: w = 1.0 / (r ** 1.3)
        weights.append(w)
    return random.choices(names, weights=weights, k=1)[0]


def generate_number(mode="normal"):
    if mode == "super": chance = 0.95
    elif mode == "lucky": chance = 0.75
    else: chance = 0.10

    if random.random() < chance:
        number = generate_pattern(mode)
    else:
        number = "".join(random.choice("0123456789") for _ in range(9))

    cname = weighted_country(mode)
    country = COUNTRIES[cname]
    opname = random.choice(list(country["operators"].keys()))
    opmult = country["operators"][opname]

    beauty = beauty_score(number)
    if mode == "lucky": beauty = round(beauty * 1.4, 2)
    elif mode == "super": beauty = round(beauty * 2.0, 2)

    # ---- ANTI-STREAK ----
    st = STATE["streak"]
    if mode in ("lucky", "super"):
        if st["myth"] >= 1:
            beauty = round(beauty * 0.35, 2)
        elif st["legend"] >= 1:
            beauty = round(beauty * 0.55, 2)
        elif st["epic"] >= 2:
            beauty = round(beauty * 0.75, 2)

    price, rname, rmult, rcls, rcard = make_number(beauty, country, opmult)

    if rname == "МИФ": st["myth"] += 1
    else: st["myth"] = 0
    if rname in ("ЛЕГЕНДА", "МИФ"): st["legend"] += 1
    else: st["legend"] = 0
    if rname in ("ЭПИК", "ЛЕГЕНДА", "МИФ"): st["epic"] += 1
    else: st["epic"] = 0

    return {
        "number": number, "country": cname, "country_code": country["code"],
        "flag": country["flag"], "operator": opname, "beauty": beauty,
        "rarity": rname, "rarity_mult": rmult, "rarity_class": rcls,
        "rarity_card": rcard, "price": price,
    }


# ============================================================
#  СОСТОЯНИЕ
# ============================================================
STATE = {
    "balance": 100000,
    "last": None,
    "my_numbers": [],
    "stats": {"spins": 0, "sold": 0, "earned": 0, "spent": 0, "best_price": 0},
    "next_id": 1,
    "streak": {"epic": 0, "legend": 0, "myth": 0, "last_tier": 0},
}


# ============================================================
#  HTML
# ============================================================
PAGE = r"""
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Крути номер</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  :root {
    --bg: #0f1216;
    --text: #e6e9ee;
    --muted: #7a808a;
    --gold: #e8c877;
  }
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html, body {
    margin: 0; padding: 0; min-height: 100vh;
    background: radial-gradient(ellipse at top, #1e2634, #0a0d12 70%);
    color: var(--text);
    font-family: -apple-system, "Segoe UI", Roboto, system-ui, sans-serif;
    font-size: 14px; overflow-x: hidden;
  }
  body::before {
    content: ""; position: fixed; inset: 0; z-index: -1;
    background:
      radial-gradient(circle at 15% 20%, rgba(120,90,200,.12), transparent 45%),
      radial-gradient(circle at 85% 75%, rgba(200,150,80,.12), transparent 45%);
    animation: bgShift 20s ease-in-out infinite alternate;
  }
  @keyframes bgShift {
    0% { transform: translate(0,0) scale(1); }
    100% { transform: translate(-25px,-25px) scale(1.08); }
  }
  .game {
    max-width: 560px; margin: 0 auto; padding: 16px 14px 40px;
    display: flex; flex-direction: column; align-items: center;
    perspective: 1600px;
  }
  .top-bar {
    width: 100%; display: flex; justify-content: space-between;
    align-items: center; gap: 10px; margin-bottom: 14px;
  }
  .logo {
    font-size: 17px; font-weight: 800; letter-spacing: .5px;
    background: linear-gradient(90deg, #e8c877, #f5e5b8, #e8c877);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .balance-pill {
    display: flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 20px;
    background: linear-gradient(140deg, #2a3040, #14181f);
    border: 1px solid rgba(232,200,119,.3);
    box-shadow: 0 0 20px rgba(232,200,119,.15);
    font-size: 14px; font-weight: 700; color: var(--gold);
  }
  .balance-pill::before { content: "💰"; font-size: 15px; }
  .tabs {
    display: flex; gap: 6px; margin-bottom: 20px;
    background: rgba(0,0,0,.4); padding: 4px; border-radius: 12px;
  }
  .tab {
    padding: 8px 20px; border-radius: 8px; cursor: pointer;
    color: var(--muted); font-size: 13px; font-weight: 600;
    user-select: none; transition: all .25s;
    display: flex; align-items: center; gap: 6px;
  }
  .tab.active {
    background: linear-gradient(140deg, #3a4258, #20242c);
    color: var(--text);
    box-shadow: 0 2px 12px rgba(0,0,0,.4);
  }
  .tab .badge {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 18px; height: 18px; padding: 0 5px;
    background: var(--gold); color: #1a1e26;
    font-size: 10px; font-weight: 800; border-radius: 9px;
  }

  /* ============ 3D КОНТЕЙНЕР SIM-КАРТЫ ============ */
  .sim-stage {
    width: 100%; max-width: 360px;
    perspective: 1400px;
    margin-bottom: 24px;
    display: flex; justify-content: center;
  }

  .sim-3d {
    position: relative;
    width: 100%; aspect-ratio: 1.586 / 1;
    transform-style: preserve-3d;
    transform: rotateX(12deg) rotateY(-8deg);
    transition: transform .8s cubic-bezier(.2,.8,.2,1);
  }

  .sim-3d.idle {
    animation: simFloat 4s ease-in-out infinite;
  }
  @keyframes simFloat {
    0%, 100% { transform: rotateX(12deg) rotateY(-8deg) translateY(0); }
    50%      { transform: rotateX(12deg) rotateY(-8deg) translateY(-6px); }
  }

  /* Тень под картой */
  .sim-shadow {
    position: absolute; left: 6%; right: 6%; bottom: -22px; height: 30px;
    background: radial-gradient(ellipse at center, rgba(0,0,0,.85), transparent 75%);
    filter: blur(10px);
    border-radius: 50%;
    z-index: -1;
    transform: translateZ(-40px);
  }

  /* ============ ОСНОВА SIM-КАРТЫ ============ */
  .sim-body {
    position: absolute; inset: 0;
    border-radius: 16px;
    transform-style: preserve-3d;
    box-shadow:
      0 30px 60px rgba(0,0,0,.75),
      0 12px 24px rgba(0,0,0,.5),
      0 4px 8px rgba(0,0,0,.4);
  }

  /* Верхняя грань — срезанный левый нижний угол (как у настоящей SIM) */
  .sim-face {
    position: absolute; inset: 0;
    clip-path: polygon(0 0, 100% 0, 100% 100%, 22% 100%, 0 78%);
    border-radius: 14px;
    overflow: hidden;
    background: linear-gradient(140deg, #4a5058 0%, #2a3038 55%, #1a1e24 100%);
    transition: background 1s ease, filter 1s ease;
    box-shadow:
      inset 0 2px 4px rgba(255,255,255,.15),
      inset 0 -3px 6px rgba(0,0,0,.5),
      inset 4px 0 6px rgba(255,255,255,.06),
      inset -4px 0 6px rgba(0,0,0,.35);
  }

  /* Боковая грань (толщина карты) */
  .sim-edge-bottom {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 8px;
    background: linear-gradient(180deg, #1a1e24, #0a0c10);
    transform-origin: bottom;
    transform: translateY(100%) rotateX(-90deg);
    clip-path: polygon(0 0, 100% 0, 100% 100%, 22% 100%, 0 78%);
    border-radius: 0 0 4px 4px;
  }
  .sim-edge-right {
    position: absolute;
    right: 0; top: 0; bottom: 0;
    width: 8px;
    background: linear-gradient(90deg, #2a3038, #0a0c10);
    transform-origin: right;
    transform: translateX(100%) rotateY(90deg);
    border-radius: 0 4px 4px 0;
  }

  /* Глянцевая полоса */
  .sim-face::before {
    content: ""; position: absolute; inset: 0; z-index: 3;
    background: linear-gradient(115deg,
      transparent 30%,
      rgba(255,255,255,.10) 42%,
      rgba(255,255,255,.22) 50%,
      rgba(255,255,255,.10) 58%,
      transparent 70%);
    pointer-events: none;
  }

  /* Тиснение */
  .sim-face::after {
    content: ""; position: absolute; inset: 0; z-index: 2;
    background-image:
      repeating-linear-gradient(45deg, rgba(255,255,255,.015) 0 1px, transparent 1px 3px);
    opacity: .6;
    pointer-events: none;
  }

  .flash-layer {
    position: absolute; inset: 0; z-index: 20;
    pointer-events: none;
    opacity: 0;
  }
  @keyframes flashAnim {
    0% { opacity: 1; background: radial-gradient(circle at center, rgba(255,255,255,.9), transparent 65%); }
    100% { opacity: 0; background: radial-gradient(circle at center, rgba(255,255,255,.9), transparent 65%); }
  }

  /* ============ ЧИП 3D — сдвинут вниз-влево ============ */
  .sim-chip {
    position: absolute;
    left: 8%; top: 63%;
    transform: translateY(-50%) translateZ(2px);
    width: 58px; height: 44px;
    border-radius: 8px;
    background:
      linear-gradient(135deg, #e8cf88 0%, #c9a95a 25%, #f0d98a 50%, #b8923f 75%, #e8cf88 100%);
    box-shadow:
      0 4px 10px rgba(0,0,0,.65),
      inset 0 1px 2px rgba(255,255,255,.7),
      inset 0 -2px 4px rgba(0,0,0,.5),
      inset 2px 0 3px rgba(255,255,255,.3),
      inset -2px 0 3px rgba(0,0,0,.3);
    z-index: 5;
    overflow: hidden;
  }

  .sim-chip::before {
    content: ""; position: absolute; inset: 5px;
    background-image:
      linear-gradient(to right, rgba(0,0,0,.7) 2px, transparent 2px),
      linear-gradient(to right, rgba(0,0,0,.7) 2px, transparent 2px),
      linear-gradient(to bottom, rgba(0,0,0,.7) 2px, transparent 2px),
      linear-gradient(to bottom, rgba(0,0,0,.7) 2px, transparent 2px);
    background-size: 33.33% 100%, 33.33% 100%, 100% 50%, 100% 50%;
    background-position: 0 0, 66.66% 0, 0 0, 0 50%;
    background-repeat: no-repeat;
    border-radius: 3px;
  }

  .sim-chip::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(115deg,
      transparent 30%,
      rgba(255,255,255,.55) 48%,
      rgba(255,255,255,.75) 50%,
      rgba(255,255,255,.55) 52%,
      transparent 70%);
    animation: chipShine 3s ease-in-out infinite;
  }
  @keyframes chipShine {
    0%, 100% { transform: translateX(-100%); }
    50%      { transform: translateX(100%); }
  }

  /* ============ ОБЛОЖКИ ПО РЕДКОСТИ ============ */
  .sim-3d.rar-trash .sim-face {
    background: linear-gradient(140deg, #4a5058 0%, #2a3038 55%, #1a1e24 100%);
  }
  .sim-3d.rar-common .sim-face {
    background: linear-gradient(140deg, #5a6068 0%, #343a42 55%, #1e2228 100%);
  }
  .sim-3d.rar-uncommon .sim-face {
    background: linear-gradient(140deg, #2a5578 0%, #1e3a55 55%, #0f1e2e 100%);
    box-shadow:
      inset 0 2px 4px rgba(255,255,255,.2),
      inset 0 -3px 6px rgba(0,0,0,.5),
      inset 0 0 60px rgba(120,180,220,.25),
      0 0 40px rgba(120,180,220,.4);
  }
  .sim-3d.rar-rare .sim-face {
    background: linear-gradient(140deg, #1e3a78 0%, #1a2848 55%, #0a1424 100%);
    box-shadow:
      inset 0 2px 4px rgba(255,255,255,.2),
      inset 0 -3px 6px rgba(0,0,0,.5),
      inset 0 0 70px rgba(100,150,230,.3),
      0 0 55px rgba(100,150,230,.55);
  }
  .sim-3d.rar-epic .sim-face {
    background: linear-gradient(140deg, #5a2a8a 0%, #3a1a5a 55%, #1a0e2e 100%);
    box-shadow:
      inset 0 2px 4px rgba(255,255,255,.25),
      inset 0 -3px 6px rgba(0,0,0,.5),
      inset 0 0 80px rgba(180,120,240,.35),
      0 0 70px rgba(180,120,240,.7);
    animation: epicGlow 2.5s ease-in-out infinite;
  }
  @keyframes epicGlow {
    0%, 100% { filter: brightness(1); }
    50%      { filter: brightness(1.15); }
  }
  .sim-3d.rar-legend .sim-face {
    background: linear-gradient(140deg, #8a6a1a 0%, #5a4418 55%, #2e2208 100%);
    box-shadow:
      inset 0 2px 4px rgba(255,255,255,.3),
      inset 0 -3px 6px rgba(0,0,0,.5),
      inset 0 0 90px rgba(255,220,130,.4),
      0 0 90px rgba(255,220,130,.8);
    animation: legendGlow 2s ease-in-out infinite;
  }
  @keyframes legendGlow {
    0%, 100% { filter: brightness(1) saturate(1); }
    50%      { filter: brightness(1.25) saturate(1.2); }
  }
  .sim-3d.rar-myth .sim-face {
    background: linear-gradient(140deg, #a02a2a 0%, #6a1a3a 40%, #2a0e20 100%);
    box-shadow:
      inset 0 2px 4px rgba(255,255,255,.3),
      inset 0 -3px 6px rgba(0,0,0,.5),
      inset 0 0 100px rgba(255,140,80,.45),
      0 0 110px rgba(255,140,80,1);
    animation: mythGlow 1.6s ease-in-out infinite;
  }
  @keyframes mythGlow {
    0%, 100% { filter: brightness(1) saturate(1); }
    50%      { filter: brightness(1.3) saturate(1.3); }
  }

  /* ============ СОДЕРЖИМОЕ КАРТЫ ============ */
  .sim-content {
    position: absolute; inset: 0;
    padding: 12px 14px;
    display: flex; flex-direction: column; justify-content: space-between;
    z-index: 6;
    clip-path: polygon(0 0, 100% 0, 100% 100%, 22% 100%, 0 78%);
  }

  .sim-top {
    display: flex; justify-content: space-between; align-items: flex-start;
  }
  .sim-top .left { display: flex; align-items: center; gap: 6px; }
  .sim-top .right { display: flex; align-items: center; gap: 6px; }
  .big-flag {
    font-size: 22px; line-height: 1;
    filter: drop-shadow(0 2px 3px rgba(0,0,0,.8));
  }
  .country-name, .op-name {
    font-size: 11px; font-weight: 800; color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,.9);
    letter-spacing: .3px;
  }
  .op-logo {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 30px; height: 26px; padding: 0 6px;
    border-radius: 6px;
    background: rgba(0,0,0,.65);
    border: 1px solid rgba(255,255,255,.2);
    font-size: 11px; font-weight: 900; color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,.9);
    box-shadow: inset 0 1px 2px rgba(255,255,255,.15);
  }

  /* ============ НОМЕР — сдвинут правее, чтобы чип не мешал ============ */
  .number-block {
    display: flex; flex-direction: column; align-items: flex-end;
    padding-right: 4px;
    margin-top: 4px;
    margin-left: 70px;
  }
  .number-label {
    font-size: 8px; letter-spacing: 2px; color: rgba(255,255,255,.55);
    text-transform: uppercase; font-weight: 800; margin-bottom: 4px;
  }
  .number-row { display: flex; align-items: center; gap: 4px; }
  .prefix-box {
    padding: 0 7px; height: 30px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 900; color: var(--gold);
    background: rgba(0,0,0,.7);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 6px;
    font-variant-numeric: tabular-nums;
    text-shadow: 0 0 8px rgba(232,200,119,.6);
  }
  .digits-row { display: flex; gap: 2px; }
  .digit-box {
    width: 20px; height: 30px; border-radius: 5px;
    background: rgba(0,0,0,.75);
    border: 1px solid rgba(255,255,255,.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 900; color: #fff;
    overflow: hidden; position: relative;
    box-shadow: inset 0 -2px 4px rgba(0,0,0,.7);
  }
  .digit-box .reel {
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center;
    will-change: transform;
  }
  .digit-box .reel span { height: 30px; line-height: 30px; }
  .digit-box.locked { border-color: var(--gold); box-shadow: 0 0 8px rgba(232,200,119,.5); }
  .digit-box.win { animation: digitPulse .4s ease; }
  @keyframes digitPulse {
    0%   { transform: scale(1); }
    50%  { transform: scale(1.18); box-shadow: 0 0 14px currentColor; }
    100% { transform: scale(1); }
  }

  .sim-bottom {
    display: flex; justify-content: space-between; align-items: flex-end;
    padding-right: 8px;
  }
  .sim-bottom .col { display: flex; flex-direction: column; gap: 2px; align-items: flex-start; }
  .sim-bottom .right { align-items: flex-end; }
  .sim-info { font-size: 9px; color: rgba(255,255,255,.65); text-shadow: 0 1px 2px rgba(0,0,0,.9); }
  .sim-info b { color: #fff; font-weight: 800; }
  .sim-price {
    font-size: 13px; font-weight: 900; color: var(--gold);
    text-shadow: 0 0 10px rgba(232,200,119,.8), 0 1px 2px rgba(0,0,0,.9);
  }
  .sim-rarity {
    font-size: 9px; font-weight: 900; letter-spacing: 1px; text-transform: uppercase;
    padding: 2px 6px; border-radius: 4px;
    background: rgba(0,0,0,.6);
    border: 1px solid currentColor;
    text-shadow: 0 0 6px currentColor;
  }
  .r-trash    { color: #8b9199; }
  .r-common   { color: #b8bcc2; }
  .r-uncommon { color: #7ac0e8; }
  .r-rare     { color: #6a9aff; }
  .r-epic     { color: #b88aff; }
  .r-legend   { color: #ffd966; }
  .r-myth     { color: #ff9a5a; }

  /* ============ КНОПКИ ============ */
  .controls {
    display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
    width: 100%; max-width: 460px;
  }
  button {
    flex: 1 1 auto; min-width: 130px;
    padding: 13px 16px; border: 1px solid #333a44; border-radius: 12px;
    background: linear-gradient(140deg, #2a3040, #14181f);
    color: var(--text); font-size: 13px; font-weight: 700;
    cursor: pointer; transition: all .2s; font-family: inherit;
    box-shadow: 0 4px 12px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.06);
  }
  button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.12);
  }
  button:active:not(:disabled) { transform: translateY(0) scale(.98); }
  button:disabled { opacity: .4; cursor: not-allowed; }
  #spinNormal { border-color: rgba(150,170,200,.35); }
  #spinLucky {
    background: linear-gradient(140deg, #4a2e7a, #1e1230);
    border-color: rgba(180,120,240,.5); color: #e8d4ff;
  }
  #spinLucky:hover:not(:disabled) { box-shadow: 0 8px 22px rgba(180,120,240,.5); }
  #spinSuper {
    background: linear-gradient(140deg, #8a6a1a, #3a2810);
    border-color: rgba(255,220,130,.6); color: #ffe9a8;
  }
  #spinSuper:hover:not(:disabled) { box-shadow: 0 8px 24px rgba(255,220,130,.6); }

  /* ============ СТАТИСТИКА ============ */
  .stats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 8px; margin-top: 22px; width: 100%; max-width: 460px;
  }
  @media (max-width: 500px) { .stats { grid-template-columns: repeat(2, 1fr); } }
  .stat {
    background: linear-gradient(140deg, rgba(42,48,64,.7), rgba(20,24,31,.9));
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 12px; padding: 10px 8px; text-align: center;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
  }
  .stat .label {
    font-size: 10px; color: var(--muted); text-transform: uppercase;
    letter-spacing: .5px; margin-bottom: 4px; font-weight: 600;
  }
  .stat .value { font-size: 15px; color: var(--text); font-weight: 800; }

  /* ============ МОИ НОМЕРА ============ */
  .my-list {
    width: 100%; max-width: 460px;
    display: flex; flex-direction: column; gap: 10px;
  }
  .my-card {
    display: grid; grid-template-columns: 48px 1fr auto;
    gap: 12px; align-items: center;
    background: linear-gradient(140deg, #222836, #14181f);
    border: 1px solid #333a44; border-radius: 14px;
    padding: 12px 14px;
    transition: all .3s;
  }
  .my-card.rar-epic   { border-color: rgba(180,120,240,.6); box-shadow: 0 4px 22px rgba(180,120,240,.35); }
  .my-card.rar-legend { border-color: rgba(255,220,130,.7); box-shadow: 0 4px 24px rgba(255,220,130,.45); }
  .my-card.rar-myth   { border-color: rgba(255,140,80,.8); box-shadow: 0 4px 28px rgba(255,140,80,.55); }
  .my-card .flag-big { font-size: 28px; text-align: center; }
  .my-card .num-line {
    font-size: 16px; font-weight: 800; letter-spacing: .5px;
    color: #fff; font-variant-numeric: tabular-nums;
  }
  .my-card .num-line .p { color: var(--gold); margin-right: 3px; }
  .my-card .meta {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-top: 4px; font-size: 11px; color: var(--muted);
  }
  .my-card .meta b { color: var(--text); font-weight: 700; }
  .my-card .price-col { text-align: right; }
  .my-card .price-col .price { font-size: 16px; font-weight: 800; color: var(--gold); }
  .my-card .price-col .rar {
    font-size: 10px; font-weight: 800; letter-spacing: .5px;
    text-transform: uppercase; margin-top: 2px;
  }
  .my-card button {
    margin-top: 6px; padding: 6px 12px; font-size: 11.5px;
    min-width: auto; border-color: rgba(255,220,130,.5); color: #ffe9a8;
  }
  .empty {
    text-align: center; color: var(--muted); padding: 60px 20px; font-size: 14px;
    background: linear-gradient(140deg, rgba(42,48,64,.4), rgba(20,24,31,.7));
    border: 1px dashed rgba(255,255,255,.08); border-radius: 14px;
  }

  /* ============ TOAST ============ */
  .toast {
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%) translateY(20px);
    background: linear-gradient(140deg, #2e3546, #14181f);
    border: 1px solid rgba(232,200,119,.4); color: var(--text);
    padding: 12px 22px; border-radius: 12px;
    opacity: 0; pointer-events: none; z-index: 100;
    font-size: 13.5px; font-weight: 600;
    max-width: 90vw; text-align: center;
    box-shadow: 0 12px 30px rgba(0,0,0,.6), 0 0 30px rgba(232,200,119,.2);
    transition: opacity .3s, transform .3s;
  }
  .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
  #tab-my { display: none; width: 100%; flex-direction: column; align-items: center; }
</style>
</head>
<body>
<div class="game">
  <div class="top-bar">
    <div class="logo">📱 КРУТИ НОМЕР</div>
    <div class="balance-pill"><span id="balance">100000</span> ₽</div>
  </div>

  <div class="tabs">
    <div class="tab active" id="tabBtnGame">🎰 Крутить</div>
    <div class="tab" id="tabBtnMy">📂 Мои номера <span class="badge" id="my-count">0</span></div>
  </div>

  <div id="tab-game" style="width:100%; display:flex; flex-direction:column; align-items:center;">

    <div class="sim-stage">
      <div class="sim-3d rar-trash idle" id="sim-3d">
        <div class="sim-shadow"></div>
        <div class="sim-body">
          <div class="sim-face" id="sim-face">
            <div class="flash-layer" id="flash-layer"></div>
          </div>
          <div class="sim-edge-bottom"></div>
          <div class="sim-edge-right"></div>
        </div>

        <div class="sim-chip"></div>

        <div class="sim-content">
          <div class="sim-top">
            <div class="left">
              <span class="big-flag" id="flag-top">🏳️</span>
              <span class="country-name" id="country-name">—</span>
            </div>
            <div class="right">
              <span class="op-name" id="operator-name">—</span>
              <span class="op-logo" id="op-logo">?</span>
            </div>
          </div>

          <div class="number-block">
            <div class="number-label">НОМЕР</div>
            <div class="number-row">
              <div class="prefix-box" id="prefix">+—</div>
              <div class="digits-row" id="digits-row"></div>
            </div>
          </div>

          <div class="sim-bottom">
            <div class="col">
              <div class="sim-info">Режим: <b id="mode-info">—</b></div>
              <div class="sim-info">Красота: <b id="beauty">—</b></div>
            </div>
            <div class="col right">
              <div class="sim-rarity r-trash" id="rarity-info">—</div>
              <div class="sim-price"><span id="price">0</span> ₽</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="controls">
      <button id="spinNormal">Крутить — 150 ₽</button>
      <button id="spinLucky">Удача+ — 5000 ₽</button>
      <button id="spinSuper">Макс. удача — 20000 ₽</button>
    </div>

    <div class="stats">
      <div class="stat"><div class="label">Прокруток</div><div class="value" id="st-spins">0</div></div>
      <div class="stat"><div class="label">Продано</div><div class="value" id="st-sold">0</div></div>
      <div class="stat"><div class="label">Заработано</div><div class="value" id="st-earned">0</div></div>
      <div class="stat"><div class="label">Лучшая</div><div class="value" id="st-best">0</div></div>
    </div>
  </div>

  <div id="tab-my">
    <div class="my-list" id="my-list"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
(function() {
  "use strict";
  const $ = id => document.getElementById(id);
  const balanceEl = $("balance"), digitsRow = $("digits-row"), prefixEl = $("prefix");
  const flagTop = $("flag-top"), countryName = $("country-name");
  const operatorName = $("operator-name"), opLogo = $("op-logo");
  const beautyEl = $("beauty"), priceEl = $("price");
  const toastEl = $("toast");
  const stSpins = $("st-spins"), stSold = $("st-sold"), stEarned = $("st-earned"), stBest = $("st-best");
  const modeInfo = $("mode-info"), rarityInfo = $("rarity-info");
  const myList = $("my-list"), myCount = $("my-count");
  const tabGame = $("tab-game"), tabMy = $("tab-my");
  const tabBtnGame = $("tabBtnGame"), tabBtnMy = $("tabBtnMy");
  const sim3d = $("sim-3d"), simFace = $("sim-face"), flashLayer = $("flash-layer");
  const DIGITS = 9;
  let spinning = false;

  tabBtnGame.addEventListener("click", () => {
    tabBtnGame.classList.add("active");
    tabBtnMy.classList.remove("active");
    tabGame.style.display = "flex";
    tabMy.style.display = "none";
  });
  tabBtnMy.addEventListener("click", () => {
    tabBtnMy.classList.add("active");
    tabBtnGame.classList.remove("active");
    tabGame.style.display = "none";
    tabMy.style.display = "flex";
    loadMyNumbers();
  });

  function buildDigitsRow() {
    digitsRow.innerHTML = "";
    for (let i = 0; i < DIGITS; i++) {
      const box = document.createElement("div");
      box.className = "digit-box";
      const reel = document.createElement("div");
      reel.className = "reel";
      for (let k = 0; k < 30; k++) {
        const span = document.createElement("span");
        span.textContent = k % 10;
        reel.appendChild(span);
      }
      box.appendChild(reel);
      digitsRow.appendChild(box);
    }
  }
  buildDigitsRow();

  let toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2400);
  }

  function animateDigits(finalNumber) {
    return new Promise(resolve => {
      const boxes = Array.from(digitsRow.children);
      const stops  = boxes.map(() => 700 + Math.random() * 900);
      const speeds = boxes.map(() => 800 + Math.random() * 600);
      const pos    = boxes.map(() => 0);
      const start  = performance.now();
      function frame(now) {
        let done = true;
        for (let i = 0; i < boxes.length; i++) {
          const box = boxes[i];
          const reel = box.querySelector(".reel");
          const elapsed = now - start;
          const digit = parseInt(finalNumber[i], 10);
          if (elapsed < stops[i]) {
            done = false;
            pos[i] += speeds[i] / 60;
            reel.style.transform = "translateY(" + (-(pos[i] % 300)) + "px)";
            box.classList.remove("locked");
          } else {
            reel.style.transform = "translateY(" + (-digit * 30) + "px)";
            if (!box.classList.contains("locked")) {
              box.classList.add("locked", "win");
              setTimeout(() => box.classList.remove("win"), 400);
            }
          }
        }
        if (done) resolve(); else requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    });
  }

  function applyCardRarity(cardCls) {
    sim3d.classList.remove("rar-trash","rar-common","rar-uncommon","rar-rare","rar-epic","rar-legend","rar-myth","idle","flash");
    sim3d.classList.add(cardCls);
    if (["rar-epic", "rar-legend", "rar-myth"].includes(cardCls)) {
      flashLayer.style.animation = "none";
      void flashLayer.offsetWidth;
      flashLayer.style.animation = "flashAnim .9s ease-out";
    }
  }

  function showResult(r) {
    prefixEl.textContent    = r.country_code;
    flagTop.textContent     = r.flag;
    countryName.textContent = r.country;
    operatorName.textContent= r.operator;
    opLogo.textContent      = r.operator.slice(0, 2).toUpperCase();
    beautyEl.textContent    = r.beauty;
    priceEl.textContent     = r.price;
    rarityInfo.textContent  = r.rarity;
    rarityInfo.className    = "sim-rarity " + (r.rarity_class || "r-common");
    applyCardRarity(r.rarity_card || "rar-trash");
  }

  function updateStats(stats, balance, my_count) {
    stSpins.textContent  = stats.spins;
    stSold.textContent   = stats.sold;
    stEarned.textContent = stats.earned;
    stBest.textContent   = stats.best_price;
    balanceEl.textContent = balance;
    myCount.textContent   = my_count;
  }

  function setButtonsDisabled(state) {
    $("spinNormal").disabled = state;
    $("spinLucky").disabled  = state;
    $("spinSuper").disabled  = state;
  }

  async function loadState() {
    const res = await fetch("/api/state");
    const data = await res.json();
    updateStats(data.stats, data.balance, data.my_count);
    if (data.last) showResult(data.last);
  }

  async function spin(mode) {
    if (spinning) return;
    spinning = true;
    setButtonsDisabled(true);

    const res = await fetch("/api/spin", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({mode: mode})
    });
    const data = await res.json();

    if (data.error) {
      toast(data.error);
      spinning = false;
      setButtonsDisabled(false);
      return;
    }

    Array.from(digitsRow.children).forEach(b => b.classList.remove("locked"));
    modeInfo.textContent = {normal: "обычный", lucky: "удача+", super: "макс. удача"}[mode] || mode;

    sim3d.classList.remove("idle");
    sim3d.style.transform = "rotateX(25deg) rotateY(-15deg) translateY(8px) scale(.97)";
    simFace.style.filter = "brightness(.6)";
    applyCardRarity("rar-trash");

    await animateDigits(data.result.number);

    sim3d.style.transform = "";
    simFace.style.filter = "";
    sim3d.classList.add("idle");

    showResult(data.result);
    updateStats(data.stats, data.balance, data.my_count);

    if (data.result.kept) {
      if (data.result.rarity === "МИФ") toast("🔥 МИФ! Номер ушёл в «Мои номера»");
      else if (data.result.rarity === "ЛЕГЕНДА") toast("⭐ ЛЕГЕНДА! Номер ушёл в «Мои номера»");
      else if (data.result.rarity === "ЭПИК") toast("💜 ЭПИК! Номер ушёл в «Мои номера»");
    } else {
      toast("Продано за " + data.result.price + " ₽");
    }

    spinning = false;
    setButtonsDisabled(false);
  }

  async function loadMyNumbers() {
    const res = await fetch("/api/my");
    const data = await res.json();
    myCount.textContent = data.items.length;
    myList.innerHTML = "";
    if (!data.items.length) {
      myList.innerHTML = "<div class='empty'>Пока пусто.<br>Эпик и выше попадают сюда автоматически.</div>";
      return;
    }
    data.items.forEach(item => {
      const card = document.createElement("div");
      card.className = "my-card " + (item.rarity_card || "");
      const rc = item.rarity_class || "r-common";
      card.innerHTML =
        "<div class='flag-big'>" + item.flag + "</div>" +
        "<div>" +
          "<div class='num-line'><span class='p'>" + item.country_code + "</span>" + item.number + "</div>" +
          "<div class='meta'>" +
            "<span>Страна: <b>" + item.country + "</b></span>" +
            "<span>Оператор: <b>" + item.operator + "</b></span>" +
            "<span>Красота: <b>" + item.beauty + "</b></span>" +
          "</div>" +
        "</div>" +
        "<div class='price-col'>" +
          "<div class='price'>" + item.price + " ₽</div>" +
          "<div class='rar " + rc + "'>" + item.rarity + "</div>" +
          "<button data-id='" + item.id + "'>Продать</button>" +
        "</div>";
      card.querySelector("button").addEventListener("click", () => sellFromMy(item.id));
      myList.appendChild(card);
    });
  }

  async function sellFromMy(id) {
    const listRes = await fetch("/api/my");
    const listData = await listRes.json();
    const item = listData.items.find(x => x.id === id);
    if (!item) { toast("Номер не найден"); return; }

    const ok = confirm(
      "Продать этот номер?\n\n" +
      item.country_code + item.number + "\n" +
      "Страна: " + item.country + "\n" +
      "Оператор: " + item.operator + "\n" +
      "Редкость: " + item.rarity + "\n" +
      "Цена: " + item.price + " ₽"
    );
    if (!ok) return;

    const res = await fetch("/api/my/sell", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({id: id})
    });
    const data = await res.json();
    if (data.error) { toast(data.error); return; }
    updateStats(data.stats, data.balance, data.my_count);
    toast("Продан " + data.sold.country_code + data.sold.number + " за " + data.sold.price + " ₽");
    loadMyNumbers();
  }

  $("spinNormal").addEventListener("click", () => spin("normal"));
  $("spinLucky").addEventListener("click",  () => spin("lucky"));
  $("spinSuper").addEventListener("click",  () => spin("super"));

  loadState();
})();
</script>
</body>
</html>
"""


# ============================================================
#  МАРШРУТЫ
# ============================================================
@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/api/state")
def api_state():
    return jsonify({
        "balance": STATE["balance"], "last": STATE["last"],
        "stats": STATE["stats"], "my_count": len(STATE["my_numbers"]),
    })


@app.route("/api/spin", methods=["POST"])
def api_spin():
    data = request.get_json(force=True) or {}
    mode = data.get("mode", "normal")
    cost = {"normal": 150, "lucky": 5000, "super": 20000}.get(mode, 150)

    if STATE["balance"] < cost:
        return jsonify({"error": "Недостаточно средств"}), 400

    STATE["balance"] -= cost
    STATE["stats"]["spins"] += 1
    STATE["stats"]["spent"] += cost

    result = generate_number(mode)
    result["cost"] = cost
    result["mode"] = mode

    if result["rarity"] in KEEP_FROM:
        result["id"] = STATE["next_id"]
        STATE["next_id"] += 1
        result["kept"] = True
        STATE["my_numbers"].append(result)
    else:
        result["kept"] = False
        STATE["balance"] += result["price"]
        STATE["stats"]["sold"] += 1
        STATE["stats"]["earned"] += result["price"]
        STATE["stats"]["best_price"] = max(STATE["stats"]["best_price"], result["price"])

    STATE["last"] = result
    return jsonify({
        "result": result, "balance": STATE["balance"],
        "stats": STATE["stats"], "my_count": len(STATE["my_numbers"]),
    })


@app.route("/api/my")
def api_my():
    return jsonify({"items": STATE["my_numbers"]})


@app.route("/api/my/sell", methods=["POST"])
def api_my_sell():
    data = request.get_json(force=True) or {}
    id_ = data.get("id")
    for i, item in enumerate(STATE["my_numbers"]):
        if item["id"] == id_:
            STATE["my_numbers"].pop(i)
            price = item["price"]
            STATE["balance"] += price
            STATE["stats"]["sold"] += 1
            STATE["stats"]["earned"] += price
            STATE["stats"]["best_price"] = max(STATE["stats"]["best_price"], price)
            return jsonify({
                "sold": item, "balance": STATE["balance"],
                "stats": STATE["stats"], "my_count": len(STATE["my_numbers"]),
            })
    return jsonify({"error": "Номер не найден"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
