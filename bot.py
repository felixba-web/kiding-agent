# =========================
# 🔐 ENV
# =========================

TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = os.getenv("TELEGRAM_USER_ID")

if not TOKEN:
    raise Exception("TELEGRAM_TOKEN is missing")

if AUTHORIZED_USER_ID:
    try:
        print("Whitelist aktiv")
    except ValueError:
        print("WARNUNG: TELEGRAM_USER_ID ist keine gültige Zahl")
        AUTHORIZED_USER_ID = None
else:
    print("WARNUNG: TELEGRAM_USER_ID nicht gesetzt – Whitelist deaktiviert")
    AUTHORIZED_USER_ID = None

# =========================
# ⚙️ GLOBAL STATE
# =========================

START_TIME = time.time()
BOT_VERSION = "1.1.0"

# =========================
# 📊 LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("kiding_bot")

# =========================
# 🔒 SECURITY CHECK
# =========================

def is_authorized(update: Update) -> bool:
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    if chat_type != "private":
        logger.warning(f"Blocked non-private chat from {user_id}")
        return False

    if user_id != AUTHORIZED_USER_ID:
        logger.warning(f"Unauthorized access attempt from {user_id}")
        return False

    return True

# =========================
# 🛠 HELPERS
# =========================

def get_uptime():
    delta = timedelta(seconds=int(time.time() - START_TIME))
    return str(delta)

# =========================
# 🤖 COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    await update.message.reply_text(
        "🤖 *KIDING ist aktiv!*\n\n"
        "Verfügbare Befehle:\n"
        "/status – Systemstatus\n"
        "/uptime – Laufzeit\n"
        "/id – Chat-ID\n"
        "/ping – Verbindungstest\n"
        "/version – Bot-Version\n"
        "/mode – Aktueller Modus\n"
        "/setmode <name> – Modus ändern\n"
        "/pause – Trading pausieren\n"
        "/log – Letzte Systemmeldungen anzeigen\n",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    await update.message.reply_text(
        f"🟢 *Status: Online*\n"
        f"Uptime: `{get_uptime()}`\n"
        f"Version: `{BOT_VERSION}`\n"
        f"Modus: `{context.bot_data.get('mode','idle')}`\n"
        f"Pausiert: `{context.bot_data.get('paused', False)}`",
        parse_mode="Markdown"
    )

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(f"⏱ Uptime: {get_uptime()}")

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        f"🆔 Chat-ID: `{update.effective_chat.id}`",
        parse_mode="Markdown"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text("pong 🟢")

async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        f"🔢 Version: `{BOT_VERSION}`",
        parse_mode="Markdown"
    )

async def mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    await update.message.reply_text(
        f"🎛 Aktueller Modus: `{context.bot_data.get('mode','idle')}`",
        parse_mode="Markdown"
    )

async def setmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if len(context.args) != 1:
        return await update.message.reply_text("Bitte: /setmode <mode>")

    new_mode = context.args[0]
    context.bot_data["mode"] = new_mode

    await update.message.reply_text(
        f"🔧 Modus geändert zu: `{new_mode}`",
        parse_mode="Markdown"
    )

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    context.bot_data["paused"] = True
    context.bot_data["mode"] = "paused"

    await update.message.reply_text(
        "⏸ Trading wurde pausiert.",
        parse_mode="Markdown"
    )

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    logfile = "/app/log.txt"

    if not os.path.exists(logfile):
        return await update.message.reply_text("Noch keine Logs vorhanden.")

    with open(logfile, "r") as f:
        lines = f.readlines()[-10:]

    await update.message.reply_text(
        "📄 *Letzte Log-Einträge:*\n\n" + "".join(lines),
        parse_mode="Markdown"
    )

# =========================
# 🚀 APP START
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("uptime", uptime))
app.add_handler(CommandHandler("id", chat_id))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("version", version))
app.add_handler(CommandHandler("log", log))
app.add_handler(CommandHandler("mode", mode))
app.add_handler(CommandHandler("setmode", setmode))
app.add_handler(CommandHandler("pause", pause))

logger.info("KIDING Bot gestartet")

app.run_polling()
