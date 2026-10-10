import os
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
DB = "bilimmix.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER DEFAULT 0
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                score INTEGER
            )
        """)

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Fanlar", callback_data="subjects"),
         InlineKeyboardButton("🧠 Testlar", callback_data="quiz")],
        [InlineKeyboardButton("🌐 Tillar", callback_data="languages"),
         InlineKeyboardButton("📅 Kunlik vazifa", callback_data="daily")],
        [InlineKeyboardButton("🏆 Reyting", callback_data="ranking"),
         InlineKeyboardButton("👑 Premium", callback_data="premium")],
        [InlineKeyboardButton("📄 Word / PDF", callback_data="documents"),
         InlineKeyboardButton("📊 PowerPoint", callback_data="slides")],
        [InlineKeyboardButton("🔄 Tarjimon", callback_data="translate"),
         InlineKeyboardButton("🤖 AI yordamchi", callback_data="ai")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with sqlite3.connect(DB) as con:
        con.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user.id,))
    await update.message.reply_text(
        "🤖 *BilimMix AI*\\nSizning aqlli o‘quv yordamchingiz!\\n\\nBo‘limni tanlang:",
        reply_markup=menu(),
        parse_mode="Markdown",
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data == "subjects":
        text = "📚 *Fanlar*\\n\\n📐 Matematika\\n💻 Informatika\\n🌍 Geografiya\\n📖 Ona tili"
    elif data == "quiz":
        with sqlite3.connect(DB) as con:
            con.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (uid,))
            con.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (uid,))
            con.execute("INSERT INTO results(user_id, subject, score) VALUES(?,?,?)",
                         (uid, "Umumiy test", 1))
        text = "🧠 Test bo‘limi\\n\\nHozircha demo test: 1 ball hisobingizga qo‘shildi."
    elif data == "languages":
        text = "🌐 Tillar\\n\\n🇺🇿 O‘zbekcha\\n🇬🇧 English\\n🇷🇺 Русский"
    elif data == "daily":
        text = "📅 *Bugungi vazifa*\\n\\n10 ta yangi so‘z o‘rganing va takrorlang!"
    elif data == "ranking":
        with sqlite3.connect(DB) as con:
            rows = con.execute(
                "SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10"
            ).fetchall()
        text = "🏆 *Reyting*\\n\\n" + (
            "\\n".join(f"{i}. ID {r[0]} — {r[1]} ball"
                       for i, r in enumerate(rows, 1)) or "Hali natijalar yo‘q."
        )
    elif data == "premium":
        text = "👑 *Premium demo*\\n\\nBu sinov rejimi. Hozircha to‘lov olinmaydi."
    elif data == "documents":
        text = "📄 Word/PDF yaratish funksiyasini keyingi bosqichda qo‘shamiz."
    elif data == "slides":
        text = "📊 PowerPoint yaratish funksiyasini keyingi bosqichda qo‘shamiz."
    elif data == "translate":
        text = "🔄 *Tarjimon*\\n\\nHozircha tarjima bo‘limi demo. To‘liq tarjimani keyin qo‘shamiz."
    else:
        text = "🤖 AI yordamchisi hozircha o‘chirilgan. Bot AI’siz ishlayveradi."

    await query.edit_message_text(text, reply_markup=menu(), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yordam: /start — menyuni ochish, /help — yordam.")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN Secret sozlanmagan.")
    init_db()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    print("BilimMix AI bot ishga tushmoqda...")
    app.run_polling()

if __name__ == "__main__":
    main()
