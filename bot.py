import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Здесь будем добавлять новые маршруты.
ROUTES = {
    "🏔 Пик Памяти друзей": {
        "file": "pamyati_druzey.gpx",
        "latitude": 43.030361,
        "longitude": 77.050556,
    },
    "🏔 Пик 28 героев Панфиловцев": {
        "file": "panfilovcev.gpx",
        "latitude": 43.079444,
        "longitude": 77.111944,
    },
}
HOME = ReplyKeyboardMarkup(
    [["🥾 Маршруты"]],
    resize_keyboard=True,
)

ROUTE_MENU = ReplyKeyboardMarkup(
    [
        ["📎 Скачать GPX"],
        ["🌤 Погода сегодня", "🌤 Погода завтра"],
        ["⬅️ К маршрутам"],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("route", None)
    await update.message.reply_text(
        "Привет! Я бот NIS Climbers 🏔\n"
        "Открой маршруты, чтобы выбрать трек и посмотреть погоду.",
        reply_markup=HOME,
    )


async def show_routes(update, context):
    context.user_data.pop("route", None)
    keyboard = ReplyKeyboardMarkup(
        [[name] for name in ROUTES] + [["🏠 Главное меню"]],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        "🥾 Выбери маршрут:",
        reply_markup=keyboard,
    )


async def send_track(update, name, route):
       path = BASE_DIR / "routes" / route["file"]
    if not path.is_file():
        path = BASE_DIR / route["file"]
    if not path.is_file():
        await update.message.reply_text(
            "Трек пока недоступен. Сообщи администратору клуба."
        )
        return

    with path.open("rb") as track:
        await update.message.reply_document(
            document=track,
            filename=route["file"],
            caption=f"{name}\nGPX-трек от NIS Climbers.",
        )


async def send_weather(update, name, route, day):
    params = {
        "latitude": route["latitude"],
        "longitude": route["longitude"],
        "daily": (
            "temperature_2m_min,temperature_2m_max,"
            "precipitation_sum,wind_speed_10m_max,"
            "wind_gusts_10m_max"
        ),
        "timezone": "Asia/Almaty",
        "wind_speed_unit": "ms",
        "forecast_days": 2,
    }

    await update.message.reply_text("Получаю прогноз…")

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params=params,
            )
            response.raise_for_status()
            daily = response.json()["daily"]

        def value(key):
            number = daily[key][day]
            return "нет данных" if number is None else str(number)

        message = (
            f"{name}\n"
            f"📅 {daily['time'][day]} (время Алматы)\n\n"
            f"🌡 Минимум: {value('temperature_2m_min')} °C\n"
            f"🌡 Максимум: {value('temperature_2m_max')} °C\n"
            f"🌧 Осадки за сутки: {value('precipitation_sum')} мм\n"
            f"💨 Максимальный ветер: {value('wind_speed_10m_max')} м/с\n"
            f"🌬 Порывы до: {value('wind_gusts_10m_max')} м/с\n\n"
            f"📍 Точка прогноза: "
            f"{route['latitude']}, {route['longitude']}\n"
            "Источник: https://open-meteo.com/\n\n"
            "В горах фактические условия могут отличаться. "
            "Прогноз не оценивает лавинную опасность "
            "и безопасность маршрута."
        )
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        await update.message.reply_text(
            "Не удалось получить прогноз. Попробуй позже."
        )
        return

    await update.message.reply_text(message)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text == "🏠 Главное меню":
        await start(update, context)
        return

    if text in ("🥾 Маршруты", "⬅️ К маршрутам"):
        await show_routes(update, context)
        return

    if text in ROUTES:
        context.user_data["route"] = text
        await update.message.reply_text(
            f"{text}\n\nСкачать трек или посмотреть погоду?",
            reply_markup=ROUTE_MENU,
        )
        return

    name = context.user_data.get("route")
    if name not in ROUTES:
        await update.message.reply_text(
            "Сначала открой маршруты и выбери нужный.",
            reply_markup=HOME,
        )
        return

    route = ROUTES[name]

    if text == "📎 Скачать GPX":
        await send_track(update, name, route)
    elif text == "🌤 Погода сегодня":
        await send_weather(update, name, route, 0)
    elif text == "🌤 Погода завтра":
        await send_weather(update, name, route, 1)
    else:
        await update.message.reply_text(
            f"Выбран маршрут: {name}\nВыбери действие кнопкой.",
            reply_markup=ROUTE_MENU,
        )



def main():
    if not TOKEN:
        raise RuntimeError(
            "Не найден TELEGRAM_BOT_TOKEN в настройках Render."
        )

    app = Application.builder().token(TOKEN.strip()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    port = int(os.environ.get("PORT", "10000"))
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not render_url:
        raise RuntimeError(
            "Не найден RENDER_EXTERNAL_URL в настройках Render."
        )

    webhook_path = "telegram-webhook"

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=f"{render_url.rstrip('/')}/{webhook_path}",
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()

    app.run_polling()


if __name__ == "__main__":
    main()
