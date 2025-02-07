import requests
from datetime import datetime
import pytz  # Import timezone library
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

BOT_TOKEN = "8055013676:AAFUH2F-xLDOcqH5lVYLsUJ-5GqoFnow7sE"
CALENDAR_TYPE = "julian"  # Use "gregorian" if needed

# Set your timezone (change 'Africa/Addis_Ababa' to your actual location)
LOCAL_TIMEZONE = pytz.timezone("Africa/Addis_Ababa")  # Example: Ethiopia timezone

async def get_readings(update: Update, context: CallbackContext) -> None:
    # Get the current date in your local timezone
    local_time = datetime.now(LOCAL_TIMEZONE)

    # Convert local time to Pacific Time (UTC-8)
    pacific = pytz.timezone("America/Los_Angeles")  # Orthocal API timezone
    today_pacific = local_time.astimezone(pacific)

    # Fetch the Julian calendar readings using the corrected date
    url = f"https://orthocal.info/api/{CALENDAR_TYPE}/{today_pacific.year}/{today_pacific.month}/{today_pacific.day}/"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        title = data.get("summary_title", "No title available")
        fast_level = data.get("fast_level_desc", "No fasting information")
        fast_exception = data.get("fast_exception_desc", "")
        readings_list = data.get("readings", [])

        readings_str = "\n".join([f"📖 {r['book']} {r['display']}" for r in readings_list])

        message = f"<b>{title}</b>\n<i>{fast_level} {fast_exception}</i>\n\n<u>Readings:</u>\n{readings_str}"

    except requests.exceptions.RequestException as e:
        message = f"❌ Error fetching readings: {e}"

    await update.message.reply_text(message, parse_mode="HTML")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Use /readings to get today's Orthodox readings.")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("readings", get_readings))

app.run_polling()
