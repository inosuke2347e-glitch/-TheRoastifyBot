# main.py
# RoastifyBot (clean, safe, Hinglish+English) - ready to paste into GitHub file editor
# - Reads BOT_TOKEN from environment (use .env locally or set env var on Render)
# - Commands: /joke, /motivate, /street, /insult
# - Auto-replies to greetings; detects NSFW keywords and replies with a firm, safe message
# - Colab/Jupyter safe (uses nest_asyncio) and suitable for Render deployment

# Requirements (put in requirements.txt):
# python-telegram-bot==21.4
# python-dotenv
# nest_asyncio

from dotenv import load_dotenv
import os
import re
import random
import asyncio
import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""  # Set this in Render or your environment

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Put it in a .env file or set an environment variable.")

# -------------------------
# Content pools (50 each)
# Clean, non-explicit, non-personalized lines in Hinglish + English
# -------------------------

jokes = [
    "Life ka scene meme pe hi tikka hai 😂",
    "Wifi slow hai ya brain buffering mein hai?",
    "Alarm aur main: toxic relationship ⏰",
    "Exam dekh ke pen ne bhi chhod diya saath 😭",
    "Every friendship has one genius and one Wi-Fi borrower 😎",
    "Mera mood kabhi update nahi karta, bas crash karta hai.",
    "Google se puchh le, main bhi fan hoon uska 🤷",
    "Overthinking is my cardio 💭",
    "Calm hoon... bas caps lock mein bol raha hoon 😤",
    "Wallet empty, memes full-of-life.",
    "Sent a meme. Got ghosted by laughter.",
    "Job nahi mil rahi, par hope pending hai 😂",
    "Loading... dreams 99% (please wait).",
    "Karma thoda late aata hai, par aata jaroor hai.",
    "Searched 'how to be happy' — internet crashed.",
    "Battery low? Nah, motivation low 🔋",
    "Plans folder mein pending, archive mein ambition.",
    "Dreams buffering... try again later ⏳",
    "Adulting ka tutorial missing hai, link bhejo pls.",
    "Low balance alert, high hopes.",
    "Mood ka Wi-Fi off hai bro.",
    "Goals and naps: same boat 🛶",
    "One day job — today meme production.",
    "When life gives lemons, add tequila 🍋",
    "Update available — storage full 💾",
    "Energy-efficient mode: activated.",
    "Work smart... or at least look like you are 😎",
    "Vacation > motivation (temporary logic).",
    "Trying to adult. Failing successfully.",
    "Even Google needs to chill sometimes.",
    "If overthinking burned calories, fit hota.",
    "Brain: many problems. Me: same.",
    "Talent: napping anywhere, anytime 💤",
    "Life reboot required — please save work.",
    "System hang? Try unplugging problems.",
    "Rich people suffer too — apparently.",
    "Luck seems offline for me today.",
    "Exam time: everyone remembers, I remember memes.",
    "Told to chill — now stress doubled.",
    "Multitask? I multi-nap 😴",
    "Small phone, big feelings.",
    "Target today: look productive.",
    "Ignore notifications, they’re emotional.",
    "Side character energy, main plot pending.",
    "Gym allergy: only cures are memes.",
    "Sunday + nap = love language.",
    "Static IP of life — not moving 💻",
    "Chai + sarcasm = daily combo ☕",
    "Happy if Wi-Fi strong, everything else secondary."
]

motivate = [
    "Mehnat kar — result thoda late aata hai par aata hai 🔥",
    "Alarm snooze mat kar; tera time aayega 💪",
    "Stop doubting — overthinking wastes energy.",
    "Zindagi short hai; priorities set kar 💥",
    "Small steps matter — ek kadam roz.",
    "Darr ke aage growth milti hai, try karo 📶",
    "Vibe strong rakho; tribe ban jayegi 🔥",
    "Winners plan, then act — nap strategically 😎",
    "Aaj ki mehnat kal ka proof banegi.",
    "Compete with yourself, not others 💯",
    "Patience rakho; mango bhi season mein aata hai 🥭",
    "Control your remote — take the lead 📱",
    "Hard work abhi bland lagta hai, kal legendary hoga.",
    "Soch badi rakho; storage expand karna mat bhool.",
    "Buffering is temporary — keep going 🔄",
    "Hustle builds the muscle of success 💪",
    "Restart nahi, persistence chahiye 🎮",
    "Underrated banna mat — results dikha do.",
    "Be your own benchmark, not a copy.",
    "Pain aaj, punchline kal — keep going.",
    "Fail karna part of learning; repeat wiser 🚀",
    "Credit failures as lessons; grow from them 🌱",
    "Life infuses humor into hard work 😂",
    "Process chal raha hai — trust it ⚙️",
    "Try and keep trying; memes will follow 😜",
    "Big problems = bigger stories later 💪",
    "Small struggle, big chai — energy restored ☕",
    "Silent mode today, ringtone tomorrow 🔊",
    "Consistency > talent when talent sleeps.",
    "Survive but aim to dominate 🔥",
    "Daily progress beats overnight wonders 📈",
    "Excuses stop growth; action starts it.",
    "Wi-Fi strong — focus stronger 😂",
    "Keep screenshots of progress as proof.",
    "Believe and search the rest on Google 💻",
    "No shortcuts — hustle + chai ☕",
    "Debug life like code — iterate continuously.",
    "Update late but powerful — be that ⚡",
    "Each fall saves data for growth 💾",
    "Write your own story; don't copy-paste.",
    "Silent achiever > loud starter 💪",
    "Work while others chill — results pay.",
    "Patience helps even with slow internet.",
    "Let life auto-save your effort 😎",
    "High confidence, low expectations — win.",
    "Karma checks you — show effort.",
    "Main character energy — speak your line 💬",
    "Small steps, huge impact — like EMI savings 😅",
    "Update your attitude to latest version 💥",
    "Dream big, sleep well — repeat 😴"
]

street = [
    "Scene kya hai bhai? Battery low, hopes lower 😭",
    "Paise kam, attitude high — classic combo 😎",
    "Google bhi puchta hai 'tu thik hai?' 😂",
    "Thoda chill; duniya tere bina bhi chal rahi hai 🌍",
    "Follow karna? GPS bhi confuse ho gaya 😏",
    "Reels chal rahe, main life buffering kar raha hoon.",
    "Main banda nahi; main vibe hoon ⚡",
    "Trend tum, timeless main 😎",
    "Powerbank chahiye — battery low chal rahi hai 🔋",
    "Went to meet myself, I was busy 💀",
    "Late nahi, fashionably delayed hoon 😏",
    "Plan tha, execution nahi hua — typical 😂",
    "Street-tired hoon, not street-smart.",
    "Filter 'no chill' pe laga hua hai 🥶",
    "Every group needs one chaos agent — main hoon 😜",
    "Mood swing on chef mode — pet dog jealous 🐶",
    "Cute nahi, thoda brutal version hoon 😈",
    "No rules, only vibes 🔥",
    "Limited edition? Nah, discontinued model.",
    "Positive hoon, battery negative hai.",
    "Fake duniya, real memes 😏",
    "Multitask? Nah — multi-nap 😴",
    "Scene strong, motivation weak 😎",
    "Cool hoon, fridge nahi 🧊",
    "Lost? GPS confident hai 😂",
    "Sapne bade, budget chhota 🚗",
    "Online hoon, mood offline 💻",
    "Slow motion hero — dramatic entry 🎬",
    "Peaceful but notifications toxic 📱",
    "Struggle with style 😎",
    "Chill but deadline follows 🔥",
    "Simple hoon — complications attract karta hoon.",
    "Quote nahi banta, quote ban jaata hoon 💬",
    "Strong but sleepy 😴",
    "Favorite hoon apna — sabka headache 😜",
    "Mood changer — weather bhi react karta hai 🌦️",
    "Warranty expired — still awesome 😜",
    "Humble by name, spicy by action 😏",
    "Street remix version hoon 🎵",
    "Offline vibes even when online 😏",
    "Attitude pe GST nahi lagata 💰",
    "Meme ka supplier hoon 😂",
    "Sarcasm included, free of charge 😎",
    "Apni duniya ka admin hoon 👑",
    "Feature, not bug — limited edition 💥",
    "Weather mood: unpredictable 🌤️",
    "No refunds on personality 😜",
    "Born to chill, forced to hustle.",
    "Main vibe hoon — handle with care."
]

# SAFE "insults" pool: playful, non-personal, non-abusive comebacks / teasing lines
# IMPORTANT: these are intentionally non-targeted and light-hearted.
insults = [
    "Oof — that was a soft take, try again 😅",
    "Aaj energy low lag rahi hai, recharge kar le.",
    "Scene thoda weak tha, come stronger next time.",
    "Friendly roast: you're amusingly average today 😂",
    "That joke landed like a flat soda — refresh please.",
    "Nice try — but optimism needs practice.",
    "That was cute... in a 'trial version' way.",
    "Plot twist: your punchline needs debugging.",
    "I expected fireworks; got a sparkler.",
    "You bring the enthusiasm, I'll bring the roast-lite.",
    "Calm down, world doesn't need that much drama.",
    "That take is under construction, return later.",
    "Energy check: low. Motivation needed.",
    "Consider this a gentle nudge, not a nuclear strike.",
    "That clapback was on silent mode.",
    "You tried — applause for effort.",
    "A for attempt, B for delivery.",
    "I can't roast a sleeping legend; wake up first.",
    "Soft burn applied — warranty still valid.",
    "Friendly poke: upgrade your material.",
    "That one was a demo. Buy the full version.",
    "Next time, less talking, more surprising.",
    "Kind roast: you tried, ten points for effort.",
    "Your vibe's pending approval — resubmit.",
    "Too mild to roast — come back spicy."
]

# -------------------------
# NSFW detection (safe response)
# -------------------------
nsfw_patterns = [
    r"\bsex\b", r"\bsexy\b", r"\bhorny\b", r"\bnude\b", r"\bnudes\b", r"\bnaked\b",
    r"\bsend nudes\b", r"\bsend nude\b", r"\bpics\b", r"\bphotos\b", r"\bvideo(s)?\b",
    r"\bxxx\b", r"\bporn\b", r"\badult\b", r"\bshow me\b", r"\bsend pic\b", r"\bsend photo\b"
]
nsfw_regex = re.compile("|".join(nsfw_patterns), flags=re.IGNORECASE)

nsfw_replies = [
    "Bhai, yeh Telegram hai, Tinder nahi — boundaries rakho 😏",
    "Please respect people. Talk properly or go home.",
    "This chat is PG-13. Keep it clean.",
    "Apni energy thoda tameez se channel kar, yaar.",
    "Bandi se baat kar, bot se kya umeed hai 😂"
]

# -------------------------
# Utilities
# -------------------------
greetings = {"hi","hello","hey","hoi","hii","helo","yo","sup","namaste"}

async def typing_then_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Simulate typing and send reply (adds small random delay)."""
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    except Exception:
        pass
    await asyncio.sleep(random.uniform(0.9, 1.8))
    # reply with plain text (no HTML) to keep it simple
    await update.message.reply_text(text)

def mention_text(user):
    """Build a simple mention text: prefer @username else first name."""
    if not user:
        return ""
    username = getattr(user, "username", None)
    if username:
        return f"@{username}"
    name = getattr(user, "first_name", "") or "Friend"
    return name

# -------------------------
# Handlers
# -------------------------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await typing_then_reply(update, context,
        "Hi! 👋 Type /joke, /street, /motivate, or /insult — I'll pick something for you!")

async def joke_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pick = random.choice(jokes)
    who = mention_text(update.effective_user)
    await typing_then_reply(update, context, f"{who} — {pick}")

async def motivate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pick = random.choice(motivate)
    who = mention_text(update.effective_user)
    await typing_then_reply(update, context, f"{who} — {pick}")

async def street_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pick = random.choice(street)
    who = mention_text(update.effective_user)
    await typing_then_reply(update, context, f"{who} — {pick}")

async def insult_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # these are light, non-personal teasing lines
    pick = random.choice(insults)
    who = mention_text(update.effective_user)
    await typing_then_reply(update, context, f"{who} — {pick}")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ("Commands:\n"
            "/joke - Get a quick joke\n"
            "/motivate - Get a tough-love motivation\n"
            "/street - Street-style one-liner\n"
            "/insult - Playful, light teasing (not personal)\n\n"
            "Or just say 'hi' in group/chat and I'll prompt you.")
    await typing_then_reply(update, context, text)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (update.message.text or "").strip()
    lower = msg.lower()

    # ignore bots
    if update.effective_user and getattr(update.effective_user, "is_bot", False):
        return

    # NSFW detection
    if nsfw_regex.search(lower):
        who = mention_text(update.effective_user)
        reply = random.choice(nsfw_replies)
        await typing_then_reply(update, context, f"{who} — {reply}")
        return

    # Greetings -> prompt menu
    if any(re.search(rf"\b{g}\b", lower) for g in greetings):
        who = mention_text(update.effective_user)
        await typing_then_reply(update, context, f"{who} — Hi! Type /joke, /street, /motivate, or /insult.")
        return

    # Direct keywords
    if re.search(r"\bjoke\b", lower):
        await joke_handler(update, context); return
    if re.search(r"\bmotivate\b|\bmotivation\b", lower):
        await motivate_handler(update, context); return
    if re.search(r"\bstreet\b", lower):
        await street_handler(update, context); return
    if re.search(r"\binsult\b|\broast\b", lower):
        await insult_handler(update, context); return

    # Default: small chance to auto-reply to keep it friendly (14% chance)
    if random.random() <= 0.14:
        pool = jokes + street + motivate
        pick = random.choice(pool)
        who = mention_text(update.effective_user)
        await typing_then_reply(update, context, f"{who} — {pick}")
    # otherwise remain silent

# -------------------------
# App setup
# -------------------------
def build_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("joke", joke_handler))
    app.add_handler(CommandHandler("motivate", motivate_handler))
    app.add_handler(CommandHandler("street", street_handler))
    app.add_handler(CommandHandler("insult", insult_handler))
    # catch-all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    return app

# -------------------------
# Run (Colab / Render safe)
# -------------------------
app = build_app()

async def main():
    # initialize and start polling
    await app.initialize()
    await app.start()
    print("🤖 RoastifyBot running...")
    await app.updater.start_polling()
    # keep the process alive
    await asyncio.Event().wait()

# For interactive environments (Colab/Jupyter) await main()
# For normal python environment you could use: asyncio.run(main())
# But the code below uses await which works in Colab/Render/etc when run as a script.
if __name__ == "__main__":
    # Running as script: use asyncio.run
    try:
        asyncio.run(main())
    except RuntimeError:
        # If event loop already running (Jupyter/Colab), use nest_asyncio approach and await
        import inspect
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # create task
            task = loop.create_task(main())
            # do not block here; main keeps running
        else:
            loop.run_until_complete(main())
