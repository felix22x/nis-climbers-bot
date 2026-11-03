
import os
from pathlib import Path
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
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
    "🏔 Пик Молодежный": {
        "file": "molodezhny.gpx",
        "latitude": 43.054167,
        "longitude": 77.059167,
    },
    "🏔 Пик Пила": {
        "file": "pik-pila.gpx",
        "latitude": 43.025996,
        "longitude": 76.898009,
    },
    "🏔 Пик Скалистый": {
        "file": "Пик_Скалистый.gpx",
        "latitude": 43.0511,
        "longitude": 77.0062,
    },
    "🏔 Титова траверс": {
        "file": "Траверс_пиков_Малыш_Водолаз_Космонавт_Титова.gpx",
        "latitude": 43.075026,
        "longitude": 77.048696,
    },
    "🏔 Малая Алматинская кругосветка": {
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
    "🏔 Большой Алматинский пик": {
        "file": "bolshoy_almatinskiy_pik.gpx",
        "latitude": 43.055,
        "longitude": 76.934167,
    },
    "🏔 Пик Советов": {
        "file": "pik_sovetov.gpx",
        "latitude": 43.023611,
        "longitude": 77.037222,
    },
    "🏔 Пик Антикайнен": {
        "file": "pik_antikaynen.gpx",
        "latitude": 43.072712,
        "longitude": 77.111835,
    },
    "🏔 Пик Физкультурник": {
        "file": "pik_fizkulturnik.gpx",
        "latitude": 43.092588,
        "longitude": 77.115702,
    },
}

CATEGORIES = {
    "🟢 Лёгкие": [
        "🏔 Малая Алматинская кругосветка",
        "🏔 Большой Алматинский пик",
    ],
    "🟡 Средние": [
        "🏔 Пик 28 героев Панфиловцев",
        "🏔 Пик Пила",
        "🏔 Пик Скалистый",
        "🏔 Титова траверс",
        "🏔 Пик Молодежный",
        "🏔 Пик Карнизный через Проходное",
        "🏔 Пик Турист",
        "🏔 Пик Антикайнен",
    ],
    "🔴 Сложные": [
        "🏔 Пик Памяти друзей",
        "🏔 Пик Валерия Хрищатого",
        "🏔 Пик Каргалинский — Пик Каменский",
        "🏔 Пик Молодая Гвардия",
        "🏔 Пик Чкалова",
        "🏔 Пик Советов",
        "🏔 Пик Физкультурник",
    ],
}

HOME = ReplyKeyboardMarkup(
    [
        ["🏔 Маршруты"],
        ["🌐 Наши соцсети"],
    ],
    resize_keyboard=True,
)

DIFFICULTY_MENU = ReplyKeyboardMarkup(
    [
        ["🟢 Лёгкие"],
        ["🟡 Средние"],
        ["🔴 Сложные"],
        ["⬅️ Назад"],
    ],
    resize_keyboard=True,
)

ROUTE_MENU = ReplyKeyboardMarkup(
    [
        ["📥 Скачать GPX-трек"],
        ["🌤 Погода сегодня", "🌤 Погода завтра"],
        ["⬅️ К списку маршрутов"],
        ["🏠 Главное меню"],
    ],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🏔 Добро пожаловать в NIS Climbers!\n\n"
        "Выбери нужный раздел:",
        reply_markup=HOME,
    )


async def show_categories(update: Update):
    await update.message.reply_text(
        "🏔 Выбери сложность маршрута:",
        reply_markup=DIFFICULTY_MENU,
    )


async def show_category_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    context.user_data["category"] = category
    context.user_data.pop("route", None)

    names = CATEGORIES[category]

    keyboard = ReplyKeyboardMarkup(
        [[name] for name in names] + [["⬅️ К сложностям"]],
        resize_keyboard=True,
    )

    await update.message.reply_text(
        f"{category}\n\nВыбери маршрут:",
        reply_markup=keyboard,
    )


async def show_socials(update: Update):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💬 WhatsApp",
                    url="https://chat.whatsapp.com/Gt5lEOMfrNYADWl6q4pnkg",
                )
            ],
            [
                InlineKeyboardButton(
                    "📸 Instagram",
                    url="https://www.instagram.com/nis_climbers",
                )
            ],
            [
                InlineKeyboardButton(
                    "🎵 TikTok",
                    url="https://www.tiktok.com/@nis_climbers",
                )
            ],
        ]
    )

    await update.message.reply_text(
        "🌐 Наши социальные сети:",
        reply_markup=keyboard,
    )


async def show_route(update: Update, context: ContextTypes.DEFAULT_TYPE, route_name: str):
    context.user_data["route"] = route_name

    await update.message.reply_text(
        f"{route_name}\n\n"
        "Что хочешь узнать?",
        reply_markup=ROUTE_MENU,
    )


async def send_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    route_name = context.user_data.get("route")

    if not route_name or route_name not in ROUTES:
        await update.message.reply_text("Сначала выбери маршрут.")
        return

    filename = ROUTES[route_name]["file"]

    candidates = [
        BASE_DIR / "routes" / filename,
        BASE_DIR / filename,
    ]

    track_path = next(
        (path for path in candidates if path.is_file()),
        None,
    )

    if track_path is None:
        await update.message.reply_text(
            "❌ Трек пока недоступен.\n"
            "Сообщи администратору клуба."
        )
        return

    with track_path.open("rb") as track:
        await update.message.reply_document(
            document=track,
            filename=track_path.name,
            caption=f"📍 GPX-трек: {route_name}",
        )


def weather_description(code):
    if code == 0:
        return "☀️ Ясно"
    if code in (1, 2, 3):
        return "⛅ Облачно"
    if code in (45, 48):
        return "🌫 Туман"
    if code in (51, 53, 55, 56, 57):
        return "🌦 Морось"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧 Дождь"
    if code in (71, 73, 75, 77, 85, 86):
        return "🌨 Снег"
    if code in (95, 96, 99):
        return "⛈ Гроза"
    return "🌤 Переменная погода"


async def send_weather(update: Update, context: ContextTypes.DEFAULT_TYPE, tomorrow=False):
    route_name = context.user_data.get("route")

    if not route_name or route_name not in ROUTES:
        await update.message.reply_text("Сначала выбери маршрут.")
        return

    route = ROUTES[route_name]

    target_date = date.today() + timedelta(days=1 if tomorrow else 0)
    day = target_date.isoformat()

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": route["latitude"],
        "longitude": route["longitude"],
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "Asia/Almaty",
        "start_date": day,
        "end_date": day,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        daily = data["daily"]

        code = daily["weather_code"][0]
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        rain = daily["precipitation_sum"][0]
        wind = daily["wind_speed_10m_max"][0]

        period = "завтра" if tomorrow else "сегодня"

        await update.message.reply_text(
            f"🌤 Погода на {period}\n"
            f"📍 {route_name}\n\n"
            f"{weather_description(code)}\n"
            f"🌡 Температура: {temp_min}°C — {temp_max}°C\n"
            f"💧 Осадки: {rain} мм\n"
            f"💨 Ветер: до {wind} км/ч\n\n"
            "⚠️ В горах погода может быстро меняться. "
            "Это ориентировочный прогноз, а не оценка безопасности маршрута."
        )

    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        await update.message.reply_text(
            "❌ Не удалось получить погоду. Попробуй позже."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    # Главное меню
    if text == "🏔 Маршруты":
        context.user_data.pop("route", None)
        await show_categories(update)
        return

    if text == "🌐 Наши соцсети":
        await show_socials(update)
        return

    if text in ("⬅️ Назад", "🏠 Главное меню"):
        context.user_data.clear()
        await update.message.reply_text(
            "🏠 Главное меню:",
            reply_markup=HOME,
        )
        return

    # Выбор сложности
    if text in CATEGORIES:
        await show_category_routes(update, context, text)
        return

    if text == "⬅️ К сложностям":
        context.user_data.pop("route", None)
        context.user_data.pop("category", None)
        await show_categories(update)
        return

    # Возврат к списку маршрутов
    if text == "⬅️ К списку маршрутов":
        category = context.user_data.get("category")

        if category in CATEGORIES:
            await show_category_routes(update, context, category)
        else:
            await show_categories(update)
        return

    # Выбор маршрута
    if text in ROUTES:
        category = context.user_data.get("category")

        if category in CATEGORIES and text in CATEGORIES[category]:
            await show_route(update, context, text)
        else:
            await update.message.reply_text(
                "Сначала выбери категорию маршрутов."
            )
        return

    # GPX
    if text == "📥 Скачать GPX-трек":
        await send_track(update, context)
        return

    # Погода
    if text == "🌤 Погода сегодня":
        await send_weather(update, context, tomorrow=False)
        return

    if text == "🌤 Погода завтра":
        await send_weather(update, context, tomorrow=True)
        return

    await update.message.reply_text(
        "Выбери действие с помощью кнопок или отправь /start."
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

    app = Application.builder().token(TOKEN.strip()).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    port = int(os.environ.get("PORT", "10000"))
    webhook_path = "telegram-webhook"

    print(f"Запускаю webhook на порту {port}", flush=True)

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=f"{render_url.rstrip('/')}/{webhook_path}",
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
