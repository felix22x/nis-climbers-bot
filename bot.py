import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
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
    "🏔Пик Молодежный": {
        "file": "molodezhny.gpx",
        "latitude": 43.054167,
        "longitude": 77.059167,
    },
    "🏔Пик Пила": {
        "file": "pik-pila.gpx",
        "latitude": 43.025996,
        "longitude": 76.898009,
    },
    "🏔Пик Скалистый": {
        "file": "Пик_Скалистый.gpx",
        "latitude": 43.0511,
        "longitude": 77.0062,
    },
    "🏔Титова траверс": {
        "file": "Траверс_пиков_Малыш_Водолаз_Космонавт_Титова.gpx",
        "latitude": 43.075026,
        "longitude": 77.048696,
    },
    "🏔Малая Алматинская кругосветка": {
        "file": "Малая Алматинская кругосветка.gpx",
        "latitude": 43.149454,
        "longitude": 77.116494,
    },
    
    "🏔 Пик Валерия Хрищатого": {
        "file": "pik_khrishchatogo.gpx",
        "latitude": 43.08761,
        "longitude": 77.09589,
    },
    "🏔 Пик Каргалинский — Пик Каменский": {
        "file": "kargalinskiy_kamenskiy.gpx",
        "latitude": 43.060703,
        "longitude": 76.854761,
    },
    "🏔 Пик Карнизный через Проходное": {
        "file": "karniznyy.gpx",
        "latitude": 43.011832,
        "longitude": 76.945988,
    },
    "🏔 Пик Молодая Гвардия": {
        "file": "molodaya_gvardiya.gpx",
        "latitude": 43.006825,
        "longitude": 77.085311,
    },
    "🏔 Пик Турист": {
        "file": "pik_turist.gpx",
        "latitude": 43.028767,
        "longitude": 76.952073,
    },
    "🏔 Пик Чкалова": {
        "file": "pik_chkalova.gpx",
        "latitude": 43.103611,
        "longitude": 77.127500,
    },

}

CATEGORIES = {
    "🟢 Лёгкие": [
        "🏔 Малая Алматинская кругосветка",
    ],
    "🟡 Средние": [
        "🏔 Пик 28 героев Панфиловцев",
        "🏔 Пик Пила",
        "🏔 Пик Скалистый",
        "🏔 Титова траверс",
        "🏔 Пик Молодежный",
        "🏔 Пик Карнизный через Проходное",
        "🏔 Пик Турист",
    ],
    "🔴 Сложные": [
        "🏔 Пик Памяти друзей",
        "🏔 Пик Валерия Хрищатого",
        "🏔 Пик Каргалинский — Пик Каменский",
        "🏔 Пик Молодая Гвардия",
        "🏔 Пик Чкалова",
    ],
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


async def show_categories(update, context):
    context.user_data.pop("route", None)
    context.user_data.pop("category", None)

    keyboard = ReplyKeyboardMarkup(
        [[category] for category in CATEGORIES]
        + [["🏠 Главное меню"]],
        resize_keyboard=True,
    )

    await update.message.reply_text(
        "🥾 Выбери категорию маршрутов:\n\n"
        "Категории заданы клубом. Снег, лёд и погода "
        "могут существенно изменить сложность.",
        reply_markup=keyboard,
    )


async def show_category_routes(update, context, category):
    context.user_data["category"] = category
    context.user_data.pop("route", None)

    keyboard = ReplyKeyboardMarkup(
        [[name] for name in CATEGORIES[category]]
        + [["⬅️ К категориям"], ["🏠 Главное меню"]],
        resize_keyboard=True,
    )

    await update.message.reply_text(
        f"{category}\nВыбери маршрут:",
        reply_markup=keyboard,
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text == "🏠 Главное меню":
        context.user_data.pop("category", None)
        await start(update, context)
        return

    if text in ("🥾 Маршруты", "⬅️ К категориям"):
        await show_categories(update, context)
        return

    if text in CATEGORIES:
        await show_category_routes(update, context, text)
        return

    if text == "⬅️ К маршрутам":
        category = context.user_data.get("category")

        if category in CATEGORIES:
            await show_category_routes(update, context, category)
        else:
            await show_categories(update, context)
        return

    if text in ROUTES:
        context.user_data["route"] = text

        for category, names in CATEGORIES.items():
            if text in names:
                context.user_data["category"] = category
                break

        await update.message.reply_text(
            f"{text}\n\nСкачать трек или посмотреть погоду?",
            reply_markup=ROUTE_MENU,
        )
        return

    name = context.user_data.get("route")

    if name not in ROUTES:
        await update.message.reply_text(
            "Открой маршруты и выбери категорию.",
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
    if not TOKEN or not TOKEN.strip():
        raise RuntimeError(
            "Не найден TELEGRAM_BOT_TOKEN в настройках Render."
        )

    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not render_url:
        raise RuntimeError(
            "Не найден RENDER_EXTERNAL_URL в настройках Render."
        )

    asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(TOKEN.strip()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    port = int(os.environ.get("PORT", "10000"))
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
