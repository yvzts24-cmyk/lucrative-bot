import requests
import time

API_KEY = "bdcc55d9443b4efca94ffa1ba7995d00"
BOT_TOKEN = "8769150868:AAEgJjvJr3olkp5-vEaxLEHlOdWh-pN257g"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
offset = 0

print("PRO LIVE BOT AKTİF...")

# ---------------- TELEGRAM ----------------

def send(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", data={
        "chat_id": chat_id,
        "text": text
    })

def get_updates():
    global offset
    return requests.get(
        f"{BASE_URL}/getUpdates",
        params={"offset": offset, "timeout": 30}
    ).json()

# ---------------- MATCH FINDER ----------------

def get_live_by_league(code):
    r = requests.get(
        "https://api.football-data.org/v4/matches",
        params={"competitions": code, "status": "LIVE"},
        headers={"X-Auth-Token": API_KEY}
    ).json()

    matches = r.get("matches", [])

    if not matches:
        return "❌ Canlı maç yok"

    result = []

    for m in matches:
        sh = m["score"]["fullTime"]["home"]
        sa = m["score"]["fullTime"]["away"]

        sh = "-" if sh is None else sh
        sa = "-" if sa is None else sa

        result.append(
            f"⚽ {m['homeTeam']['name']} {sh}-{sa} {m['awayTeam']['name']}\n⏱ {m['status']}"
        )

    return "\n\n".join(result)

# ---------------- TEAM SEARCH ----------------

def get_score(team):
    r = requests.get(
        "https://api.football-data.org/v4/matches",
        headers={"X-Auth-Token": API_KEY}
    ).json()

    team = team.lower()

    for m in r.get("matches", []):
        home = m["homeTeam"]["name"].lower()
        away = m["awayTeam"]["name"].lower()

        if team in home or team in away:

            sh = m["score"]["fullTime"]["home"]
            sa = m["score"]["fullTime"]["away"]

            sh = "-" if sh is None else sh
            sa = "-" if sa is None else sa

            return f"⚽ {m['homeTeam']['name']} {sh}-{sa} {m['awayTeam']['name']}\n⏱ {m['status']}"

    return "❌ Maç bulunamadı"

# ---------------- MAIN LOOP ----------------

while True:
    try:
        updates = get_updates()

        for u in updates.get("result", []):
            offset = u["update_id"] + 1

            message = u.get("message") or u.get("channel_post")

            if not message:
                continue

            text = message.get("text", "")
            chat_id = message["chat"]["id"]

            # ---------------- COMMANDS ----------------

            if text.startswith("/skor"):
                team = text.replace("/skor", "").strip()
                send(chat_id, get_score(team))

            elif text == "/superlig":
                send(chat_id, get_live_by_league("SA"))

            elif text == "/premierleague":
                send(chat_id, get_live_by_league("PL"))

            elif text == "/laliga":
                send(chat_id, get_live_by_league("PD"))

            elif text == "/bundesliga":
                send(chat_id, get_live_by_league("BL1"))

            elif text == "/live":
                send(chat_id, get_live_by_league(None))

    except Exception as e:
        print("HATA:", e)

    time.sleep(1)