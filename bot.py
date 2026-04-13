import telebot
import requests
import time

TELEGRAM_TOKEN = "8769150868:AAHa8BrTy2pa9mUG_eDgzmRp6wGoeW0124Q"
API_KEY = "12636d8da8210574bc72fb6c191158bb"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

cache = {}
CACHE_TIME = 30

def get_live_score(query):
    now = time.time()
    if query in cache and now - cache[query]['time'] < CACHE_TIME:
        return cache[query]['data']

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"live": "all"}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    teams = [t.strip().lower() for t in query.split('-')]
    results = []

    for fixture in data.get("response", []):
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
            home_name = fixture["teams"]["home"]["name"]
            away_name = fixture["teams"]["away"]["name"]
            home_score = fixture["goals"]["home"]
            away_score = fixture["goals"]["away"]
            minute = fixture["fixture"]["status"]["elapsed"]
            result = f"⚽ CANLI MAÇ\n{home_name} {home_score} - {away_score} {away_name}\n⏱ {minute}. dakika"
            results.append(result)

    if results:
        final = "\n\n".join(results)
        cache[query] = {'data': final, 'time': now}
        return final

    return None

@bot.channel_post_handler(func=lambda message: True)
def handle_channel_message(message):
    try:
        text = message.text.strip()
        if len(text) < 3:
            return
        result = get_live_score(text)
        if result:
            bot.send_message(message.chat.id, result)
    except Exception as e:
        print(f"Hata: {e}")

print("Bot baslatildi...")
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot çalışıyor!')
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
bot.infinity_polling()
