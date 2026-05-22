#!/usr/bin/env python3
"""
◆ CHIEF — Telegram Bot (двосторонній)
Запуск: python3 chief_telegram.py
"""

import time, datetime, requests, json, os, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN   = "8974626121:AAGpfDvsVO_Mwlq4cP61V609sB3s9gBXAYc"
CHAT_ID = "5655637193"
API     = f"https://api.telegram.org/bot{TOKEN}"
DATA_FILE = os.path.join(os.path.dirname(__file__), "chief_data.json")

# ─── ДАНІ ───────────────────────────────────────────
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"log": {}, "sessions": [], "habits": {}, "tasks": []}

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def today():
    return datetime.date.today().isoformat()

def days_left():
    return (datetime.date(2026, 6, 30) - datetime.date.today()).days

# ─── ВІДПРАВКА ───────────────────────────────────────
def send(text, reply_markup=None):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(f"{API}/sendMessage", json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[send error] {e}")
        return False

# ─── КОМАНДИ ─────────────────────────────────────────
def cmd_start():
    send(f"""◆ *CHIEF — активований* ✅

Привіт, Дада. Система запущена.

*Доступні команди:*
/plan — план дня
/focus — старт 60-хв сесії
/done — відмітити задачу
/stats — статистика дня
/habits — звички сьогодні
/sleep [год] — записати сон
/energy [1-10] — записати енергію
/tiktok [хв] — записати TikTok
/vu — прогрес до ВУ
/chinese — 5 слів дня
/log — заповнити лог дня
/help — всі команди

До ВУ: *{days_left()} днів*.""")

def cmd_plan():
    d = days_left()
    now_h = datetime.datetime.now().hour
    greeting = "Доброго ранку" if now_h < 12 else "Добрий день" if now_h < 17 else "Добрий вечір"
    send(f"""◆ *CHIEF — ПЛАН ДНЯ*
{greeting}! До ВУ: *{d} днів*

🎯 *Топ-3 задачі:*
1. Підготувати/перевірити уроки
2. Економіка — 1 тема (60 хв deep work)
3. Додати ДЗ учням

🧠 *Deep Work блоки:*
▸ Блок 1 — 60 хв: Економіка
▸ Блок 2 — 60 хв: Уроки/робота

🇨🇳 Китайська: 5 слів + 10 хв повторення

💪 Звички: вода / пілатес / читання / сон / прогулянка

⚠️ TikTok ліміт: *20 хв*. Все понад — вкрадений час від ВУ.

Починай. /focus щоб стартувати сесію.""")

def cmd_focus():
    data = load()
    session = {
        "date": today(),
        "start": datetime.datetime.now().isoformat(),
        "type": "work"
    }
    data["sessions"].append(session)
    save(data)
    send(f"""◆ *FOCUS MODE — СТАРТ* ⏱

⏰ 60 хвилин. Таймер пішов.

Правила:
• Телефон — лицем вниз
• TikTok — закрито
• Одна задача — до кінця

Напиши /done коли завершиш сесію.

До ВУ: *{days_left()} днів*.""")

    # Нагадування через 60 хвилин
    def remind():
        time.sleep(3600)
        send(f"""◆ *60 ХВИЛИН — ЗАВЕРШЕНО* ✅

Сесія закінчена. Напиши /done щоб відмітити.

Зроби перерву 10 хвилин, потім /focus знову.""")
    threading.Thread(target=remind, daemon=True).start()

def cmd_done():
    data = load()
    sessions_today = [s for s in data["sessions"] if s["date"] == today()]
    count = len(sessions_today)
    send(f"""◆ *СЕСІЮ ВІДМІЧЕНО* ✅

Сьогодні завершено сесій: *{count}*
Deep work: *{count} год*

{'🔥 Відмінно! Ще одна?' if count >= 2 else '💪 Добре. Перерва 10 хв, потім /focus'}""")

def cmd_stats():
    data = load()
    log_today = data.get("log", {}).get(today(), {})
    sessions_today = [s for s in data["sessions"] if s["date"] == today()]

    send(f"""◆ *CHIEF — СТАТИСТИКА ДНЯ*
📅 {datetime.date.today().strftime('%d.%m.%Y')}

⏱ Deep Work: *{len(sessions_today)} сесій*
😴 Сон: *{log_today.get('sleep', '—')} год*
⚡ Енергія: *{log_today.get('energy', '—')}/10*
🎯 Продуктивність: *{log_today.get('prod', '—')}/10*
📱 TikTok: *{log_today.get('tt', 0)} хв*

До ВУ: *{days_left()} днів*

{'⚠️ TikTok понад 30 хв — зверни увагу' if log_today.get('tt', 0) > 30 else '✅ TikTok в нормі'}""")

def cmd_habits():
    data = load()
    hd = data.get("habits", {}).get(today(), {})
    habits = [
        ("💧", "Вода 2л+", "water"),
        ("🧘", "Пілатес", "pilates"),
        ("📚", "Читання", "reading"),
        ("😴", "Сон 8-9 год", "sleep"),
        ("🇨🇳", "Китайська", "chinese"),
        ("🚶", "Прогулянка", "walk"),
        ("💼", "Робота 4год+", "work"),
    ]
    lines = []
    done = 0
    for icon, label, key in habits:
        status = "✅" if hd.get(key) else "⬜"
        lines.append(f"{status} {icon} {label}")
        if hd.get(key): done += 1

    pct = round(done / len(habits) * 100)
    send(f"""◆ *CHIEF — ЗВИЧКИ СЬОГОДНІ*

{chr(10).join(lines)}

Прогрес: *{done}/{len(habits)} ({pct}%)*

{'🔥 Чудово!' if pct >= 70 else '💪 Є куди рости' if pct >= 40 else '⚠️ Критично мало'}""")

def cmd_sleep(args):
    if not args:
        send("Вкажи години: /sleep 7.5")
        return
    try:
        hours = float(args[0])
        data = load()
        if today() not in data["log"]: data["log"][today()] = {}
        data["log"][today()]["sleep"] = hours
        save(data)
        msg = "✅ Відмінно!" if hours >= 8 else "⚠️ Маловато. Ціль: 8-9 год" if hours >= 6 else "🚨 Критично мало сну!"
        send(f"◆ Сон записано: *{hours} год* {msg}")
    except:
        send("Невірний формат. Приклад: /sleep 7.5")

def cmd_energy(args):
    if not args:
        send("Вкажи рівень: /energy 7")
        return
    try:
        val = int(args[0])
        if not 1 <= val <= 10: raise ValueError
        data = load()
        if today() not in data["log"]: data["log"][today()] = {}
        data["log"][today()]["energy"] = val
        save(data)
        emoji = "🔥" if val >= 8 else "⚡" if val >= 5 else "😴"
        send(f"◆ Енергія записана: *{val}/10* {emoji}")
    except:
        send("Невірний формат. Приклад: /energy 7 (від 1 до 10)")

def cmd_tiktok(args):
    if not args:
        send("Вкажи хвилини: /tiktok 20")
        return
    try:
        mins = int(args[0])
        data = load()
        if today() not in data["log"]: data["log"][today()] = {}
        data["log"][today()]["tt"] = mins
        save(data)
        if mins > 60:
            send(f"🚨 *{mins} хв TikTok* — це {mins/60:.1f} год. До ВУ {days_left()} днів. Це твій вибір.")
        elif mins > 30:
            send(f"⚠️ *{mins} хв TikTok* записано. Понад ліміт. Завтра менше.")
        else:
            send(f"✅ *{mins} хв TikTok* — в межах норми.")
    except:
        send("Невірний формат. Приклад: /tiktok 20")

def cmd_vu():
    d = days_left()
    urgency = "🚨 КРИТИЧНО" if d < 14 else "⚠️ ПОСПІШАЙ" if d < 25 else "⏳ Є час, але не зволікай"
    send(f"""◆ *CHIEF — ВСТУП ДО ВУ*

До дедлайну: *{d} днів* {urgency}
Дедлайн: 30 червня 2026

📊 *Фокус:* Економіка (слабке місце)
📐 *Математика:* добре — підтримуй темп

*Щодня:*
▸ 1 тема економіки (60 хв)
▸ 5 задач математики (30 хв)
▸ Повторення попередньої теми (15 хв)

Відкрий дашборд щоб відмітити теми: chief\_dashboard.html""")

def cmd_chinese():
    words = [
        ("你好", "nǐ hǎo", "Привіт"),
        ("努力", "nǔ lì", "Старатися"),
        ("成功", "chéng gōng", "Успіх"),
        ("学习", "xué xí", "Навчатися"),
        ("坚持", "jiān chí", "Наполегливість"),
        ("大学", "dà xué", "Університет"),
        ("经济", "jīng jì", "Економіка"),
        ("时间", "shí jiān", "Час"),
        ("目标", "mù biāo", "Мета"),
        ("今天", "jīn tiān", "Сьогодні"),
        ("明天", "míng tiān", "Завтра"),
        ("工作", "gōng zuò", "Робота"),
        ("朋友", "péng yǒu", "Друг"),
        ("快乐", "kuài lè", "Щастя"),
        ("数学", "shù xué", "Математика"),
    ]
    import random
    chosen = random.sample(words, 5)
    lines = [f"*{c}* — {p} — {t}" for c, p, t in chosen]
    send(f"""◆ *CHIEF — 中文 — 5 СЛІВ ДНЯ*

{chr(10).join(lines)}

Повтори кожне 3 рази вголос.
Завтра буде новий набір.""")

def cmd_log():
    send(f"""◆ *CHIEF — ЛОГ ДНЯ*

Заповни по черзі:
/sleep [год] — години сну
/energy [1-10] — енергія
/tiktok [хв] — TikTok сьогодні

Приклад:
/sleep 7.5
/energy 7
/tiktok 15

Або відкрий дашборд: chief\_dashboard.html""")

def cmd_help():
    send("""◆ *CHIEF — КОМАНДИ*

/plan — план дня
/focus — старт 60-хв сесії ⏱
/done — завершити сесію ✅
/stats — статистика дня 📊
/habits — звички сьогодні 💪
/vu — прогрес до ВУ 🎓
/chinese — 5 слів дня 🇨🇳
/log — заповнити лог
/sleep [год] — записати сон
/energy [1-10] — записати енергію
/tiktok [хв] — записати TikTok

Scheduled:
▸ 07:30 ранковий план
▸ 13:00 денний чекін
▸ 21:30 вечірній звіт
▸ 23:00 нагадування спати""")

# ─── SCHEDULED MESSAGES ──────────────────────────────
SCHEDULE = {
    "07:30": lambda: cmd_plan(),
    "09:30": lambda: send(f"◆ *CHIEF — ФОКУС* ⏱\n\nЧи почала deep work сесію? Якщо ні — /focus прямо зараз.\n\nДо ВУ: *{days_left()} днів*"),
    "13:00": lambda: send(f"◆ *CHIEF — ЧЕКІН*\n\nСтатус: /stats\nТоп-задача ранку — виконана?\nDW сесія — була?\n\nЯкщо ні — /focus зараз."),
    "15:00": lambda: send(f"◆ *CHIEF — ФОКУС* ⏱\n\nВдруге нагадую. /focus\n\nДо ВУ: *{days_left()} днів*"),
    "21:00": lambda: send(f"◆ *CHIEF — ВЕЧІРНІЙ БЛОК*\n\nОстання deep work сесія дня. /focus\nПотім /stats щоб підбити підсумок."),
    "21:30": lambda: cmd_stats(),
    "23:00": lambda: send(f"◆ *CHIEF — СОН*\n\n23:00. Відклади телефон.\nПідйом о 07:00.\nСон = продуктивність = ВУ.\n\nДо дедлайну: *{days_left()} днів*"),
}

sent_today = {}

def scheduler():
    global sent_today
    while True:
        now = datetime.datetime.now()
        t = now.strftime("%H:%M")
        d = today()
        if d not in sent_today:
            sent_today = {d: set()}
        if t in SCHEDULE and t not in sent_today[d]:
            SCHEDULE[t]()
            sent_today[d].add(t)
        time.sleep(20)

# ─── POLLING ─────────────────────────────────────────
def handle(text):
    text = text.strip()
    parts = text.split()
    cmd = parts[0].lower().lstrip("/").split("@")[0]
    args = parts[1:]

    handlers = {
        "start":   cmd_start,
        "plan":    cmd_plan,
        "focus":   cmd_focus,
        "done":    cmd_done,
        "stats":   cmd_stats,
        "habits":  cmd_habits,
        "vu":      cmd_vu,
        "chinese": cmd_chinese,
        "log":     cmd_log,
        "help":    cmd_help,
        "sleep":   lambda: cmd_sleep(args),
        "energy":  lambda: cmd_energy(args),
        "tiktok":  lambda: cmd_tiktok(args),
    }
    if cmd in handlers:
        handlers[cmd]()
    else:
        send(f"Невідома команда: {text}\n\nНапиши /help щоб побачити всі команди.")

def poll():
    offset = None
    print("◆ CHIEF — polling запущено")
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message"]}
            if offset: params["offset"] = offset
            r = requests.get(f"{API}/getUpdates", params=params, timeout=35)
            data = r.json()
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))
                if text and chat_id == CHAT_ID:
                    print(f"[команда] {text}")
                    handle(text)
        except Exception as e:
            print(f"[poll error] {e}")
            time.sleep(5)

# ─── HTTP СЕРВЕР (синк з дашбордом) ──────────────────
class DataHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # без зайвих логів

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            body = json.dumps(load(), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/data':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                save(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._cors()
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'{{"error":"{e}"}}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    # Railway дає PORT як env змінну; локально — 8765
    port = int(os.environ.get('PORT', 8765))
    host = '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') else 'localhost'
    server = HTTPServer((host, port), DataHandler)
    print(f"◆ CHIEF API    : http://{host}:{port}/data")
    server.serve_forever()

# ─── MAIN ─────────────────────────────────────────────
if __name__ == "__main__":
    print("◆ CHIEF Telegram Bot — запуск")
    print(f"   Chat ID : {CHAT_ID}")
    print(f"   До ВУ   : {days_left()} днів")
    print("   Ctrl+C щоб зупинити\n")

    threading.Thread(target=run_server, daemon=True).start()
    cmd_start()
    threading.Thread(target=scheduler, daemon=True).start()
    poll()