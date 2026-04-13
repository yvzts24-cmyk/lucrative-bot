import telebot
import requests
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = "8769150868:AAFNvBKyrncD-Af4raa0Kozi0I_M9sJzy0w"
API_KEY = "12636d8da8210574bc72fb6c191158bb"
CHANNEL_ID = -1002475367728

bot = telebot.TeleBot(TELEGRAM_TOKEN)

cache = {}
CACHE_TIME = 30
tracked_matches = {}
last_scores = {}

def get_live_fixtures():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"live": "all"}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json().get("response", [])
    except:
        return []

def find_match(query):
    fixtures = get_live_fixtures()
    teams = [t.strip().lower() for t in query.split('-')]
    results = []
    for fixture in fixtures:
        home = fixture["teams"]["home"]["name"].lower()
        away = fixture["teams"]["away"]["name"].lower()
        match = False
        if len(teams) == 1:
            if teams[0] in home or teams[0] in away:
                match = True
        else:
            if (teams[0] in home or teams[0] in away) and (teams[1] in home or teams[1] in away):
                match = True
        if match:
            results.append(fixture)
    return results

def format_score(fixture):
    home_name = fixture["teams"]["home"]["name"]
    away_name = fixture["teams"]["away"]["name"]
    home_score = fixture["goals"]["home"]
    away_score = fixture["goals"]["away"]
    minute = fixture["fixture"]["status"]["elapsed"]
    return f"⚽ CANLI MAC\n{home_name} {home_score} - {away_score} {away_name}\n⏱ {minute}. dakika"

def check_score_updates():
    while True:
        try:
            if tracked_matches:
                fixtures = get_live_fixtures()
                for query, data in list(tracked_matches.items()):
                    teams = [t.strip().lower() for t in query.split('-')]
                    for fixture in fixtures:
                        home = fixture["teams"]["home"]["name"].lower()
                        away = fixture["teams"]["away"]["name"].lower()
                        match = False
                        if len(teams) == 1:
                            if teams[0] in home or teams[0] in away:
                                match = True
                        else:
                            if (teams[0] in home or teams[0] in away) and (teams[1] in home or teams[1] in away):
                                match = True
                        if match:
                            fixture_id = fixture["fixture"]["id"]
                            home_score = fixture["goals"]["home"]
                            away_score = fixture["goals"]["away"]
                            status = fixture["fixture"]["status"]["short"]
                            score_key = f"{fixture_id}"
                            new_score = f"{home_score}-{away_score}"
                            if status == "FT":
                                if score_key in last_scores:
                                    home_name = fixture["teams"]["home"]["name"]
                                    away_name = fixture["teams"]["away"]["name"]
                                    bot.send_message(CHANNEL_ID, f"🏁 MAC BITTI\n{home_name} {home_score} - {away_score} {away_name}")
                                    del last_scores[score_key]
                                    if query in tracked_matches:
                                        del tracked_matches[query]
                            elif score_key in last_scores and last_scores[score_key] != new_score:
                                msg = format_score(fixture)
                                bot.send_message(CHANNEL_ID, f"🔴 GOL!\n{msg}")
                                last_scores[score_key] = new_score
                            elif score_key not in last_scores:
                                last_scores[score_key] = new_score
        except Exception as e:
            print(f"Guncelleme hatasi: {e}")
        time.sleep(60)

@bot.channel_post_handler(func=lambda message: True)
def handle_channel_message(message):
    try:
        text = message.text.strip()
        if len(text) < 3:
            return
        fixtures = find_match(text)
        if fixtures:
            for fixture in fixtures:
                result = format_score(fixture)
                bot.send_message(message.chat.id, result)
                fixture_id = fixture["fixture"]["id"]
                tracked_matches[text.lower()] = fixture_id
                last_scores[str(fixture_id)] = f"{fixture['goals']['home']}-{fixture['goals']['away']}"
    except Exception as e:
        print(f"Hata: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot calisiyor!')
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
threading.Thread(target=check_score_updates, daemon=True).start()
print("Bot baslatildi...")
bot.infinity_polling()
