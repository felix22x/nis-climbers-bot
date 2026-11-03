import os
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

ROUTES = {
    '🏔 Пик Памяти друзей': {'file': 'pamyati_druzey.gpx', 'latitude': 43.030361, 'longitude': 77.050556},
    '🏔 Пик 28 героев Панфиловцев': {'file': 'panfilovcev.gpx', 'latitude': 43.079444, 'longitude': 77.111944},
    '🏔 Пик Молодежный': {'file': 'molodezhny.gpx', 'latitude': 43.054167, 'longitude': 77.059167},
    '🏔 Пик Пила': {'file': 'pik-pila.gpx', 'latitude': 43.025996, 'longitude': 76.898009},
    '🏔 Пик Скалистый': {'file': 'Пик_Скалистый.gpx', 'latitude': 43.0511, 'longitude': 77.0062},
    '🏔 Титова траверс': {'file': 'Траверс_пиков_Малыш_Водолаз_Космонавт_Титова.gpx', 'latitude': 43.075026, 'longitude': 77.048696},
    '🏔 Малая Алматинская кругосветка': {'file': 'Малая Алматинская кругосветка.gpx', 'latitude': 43.149454, 'longitude': 77.116494},
    '🏔 Пик Валерия Хрищатого': {'file': 'pik_khrishchatogo.gpx', 'latitude': 43.08761, 'longitude': 77.09589},
    '🏔 Пик Каргалинский — Пик Каменский': {'file': 'kargalinskiy_kamenskiy.gpx', 'latitude': 43.060703, 'longitude': 76.854761},
    '🏔 Пик Карнизный через Проходное': {'file': 'karniznyy.gpx', 'latitude': 43.011832, 'longitude': 76.945988},
    '🏔 Пик Молодая Гвардия': {'file': 'molodaya_gvardiya.gpx', 'latitude': 43.006825, 'longitude': 77.085311},
    '🏔 Пик Турист': {'file': 'pik_turist.gpx', 'latitude': 43.028767, 'longitude': 76.952073},
    '🏔 Пик Чкалова': {'file': 'pik_chkalova.gpx', 'latitude': 43.103611, 'longitude': 77.127500},
    '🏔 Большой Алматинский пик': {'file': 'bolshoy_almatinskiy_pik.gpx', 'latitude': 43.055, 'longitude': 76.934167},
    '🏔 Пик Советов': {'file': 'pik_sovetov.gpx', 'latitude': 43.023611, 'longitude': 77.037222},
    '🏔 Пик Антикайнен': {'file': 'pik_antikaynen.gpx', 'latitude': 43.072712, 'longitude': 77.111835},
    '🏔 Пик Физкультурник': {'file': 'pik_fizkulturnik.gpx', 'latitude': 43.092588, 'longitude': 77.115702},
    '🏔 Пик Букреева': {'file': 'Пионер_Подножие_Букреева_Лесной_перевал_Бутако.gpx', 'latitude': 43.166713, 'longitude': 77.134642},
    '🏔 Пик Погребецкого': {'file': 'Пик Погребецкого с юга.gpx', 'latitude': 43.034167, 'longitude': 77.071389},
    '🏔 Пик Кумбель': {'file': 'kok-zhailiau-tri-brata-kumbel.gpx', 'latitude': 43.120154, 'longitude': 77.030732},
    '🏔 Пик Малыш': {'file': 'Мемориал_Мынжылки_Пик_Малыш_Мемориал.gpx', 'latitude': 43.06586, 'longitude': 77.05686},
}

CATEGORIES = {
    '🟢 Лёгкие': [
        '🏔 Малая Алматинская кругосветка',
        '🏔 Большой Алматинский пик',
        '🏔 Пик Букреева',
        '🏔 Пик Кумбель',
    ],
    '🟡 Средние': [
        '🏔 Пик 28 героев Панфиловцев',
        '🏔 Пик Пила',
        '🏔 Пик Скалистый',
        '🏔 Титова траверс',
        '🏔 Пик Молодежный',
        '🏔 Пик Карнизный через Проходное',
        '🏔 Пик Турист',
        '🏔 Пик Антикайнен',
        '🏔 Пик Малыш',
    ],
    '🔴 Сложные': [
        '🏔 Пик Памяти друзей',
        '🏔 Пик Валерия Хрищатого',
        '🏔 Пик Каргалинский — Пик Каменский',
        '🏔 Пик Молодая Гвардия',
        '🏔 Пик Чкалова',
        '🏔 Пик Советов',
        '🏔 Пик Физкультурник',
        '🏔 Пик Погребецкого',
    ],
}

HOME = ReplyKeyboardMarkup([['🏔 Маршруты'], ['🌐 Наши соцсети']], resize_keyboard=True)
DIFFICULTY_MENU = ReplyKeyboardMarkup(
    [['🟢 Лёгкие'], ['🟡 Средние'], ['🔴 Сложные'], ['⬅️ Назад']],
    resize_keyboard=True,
)
ROUTE_MENU = ReplyKeyboardMarkup(
    [['📥 Скачать GPX-трек'], ['🌤 Погода сегодня', '🌤 Погода завтра'],
     ['📅 Погода на 5 дней'],
     ['⬅️ К списку маршрутов'], ['🏠 Главное меню']],
    resize_keyboard=True,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        '🏔 Добро пожаловать в NIS Climbers!\n\nВыбери нужный раздел:',
        reply_markup=HOME,
    )


async def show_categories(update: Update):
    await update.message.reply_text('🏔 Выбери сложность маршрута:', reply_markup=DIFFICULTY_MENU)


async def show_category_routes(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    context.user_data['category'] = category
    context.user_data.pop('route', None)
    keyboard = ReplyKeyboardMarkup(
        [[name] for name in CATEGORIES[category]] + [['⬅️ К сложностям']],
        resize_keyboard=True,
    )
    await update.message.reply_text(f'{category}\n\nВыбери маршрут:', reply_markup=keyboard)


async def show_socials(update: Update):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('💬 WhatsApp', url='https://chat.whatsapp.com/Gt5lEOMfrNYADWl6q4pnkg')],
        [InlineKeyboardButton('📸 Instagram', url='https://www.instagram.com/nis_climbers')],
        [InlineKeyboardButton('🎵 TikTok', url='https://www.tiktok.com/@nis_climbers')],
    ])
    await update.message.reply_text('🌐 Наши социальные сети:', reply_markup=keyboard)


async def show_route(update: Update, context: ContextTypes.DEFAULT_TYPE, route_name: str):
    context.user_data['route'] = route_name
    await update.message.reply_text(f'{route_name}\n\nЧто хочешь узнать?', reply_markup=ROUTE_MENU)


async def send_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    route_name = context.user_data.get('route')
    if route_name not in ROUTES:
        await update.message.reply_text('Сначала выбери маршрут.')
        return
    filename = ROUTES[route_name]['file']
    candidates = [BASE_DIR / 'routes' / filename, BASE_DIR / filename]
    track_path = next((path for path in candidates if path.is_file()), None)
    if track_path is None:
        await update.message.reply_text('❌ Трек пока недоступен. Сообщи администратору клуба.')
        return
    with track_path.open('rb') as track:
        await update.message.reply_document(
            document=track, filename=track_path.name, caption=f'📍 GPX-трек: {route_name}'
        )


def weather_description(code):
    if code == 0:
        return '☀️ Ясно'
    if code in (1, 2, 3):
        return '⛅ Облачно'
    if code in (45, 48):
        return '🌫 Туман'
    if code in (51, 53, 55, 56, 57):
        return '🌦 Морось'
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return '🌧 Дождь'
    if code in (71, 73, 75, 77, 85, 86):
        return '🌨 Снег'
    if code in (95, 96, 99):
        return '⛈ Гроза'
    return '🌤 Переменная погода'


async def send_weather(update: Update, context: ContextTypes.DEFAULT_TYPE, tomorrow=False):
    route_name = context.user_data.get('route')
    if route_name not in ROUTES:
        await update.message.reply_text('Сначала выбери маршрут.')
        return
    route = ROUTES[route_name]
    target_date = datetime.now(ZoneInfo('Asia/Almaty')).date() + timedelta(days=int(tomorrow))
    day = target_date.isoformat()
    params = {
        'latitude': route['latitude'],
        'longitude': route['longitude'],
        'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
        'timezone': 'Asia/Almaty',
        'start_date': day,
        'end_date': day,
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get('https://api.open-meteo.com/v1/forecast', params=params)
            response.raise_for_status()
            daily = response.json()['daily']
        code = daily['weather_code'][0]
        temp_max = daily['temperature_2m_max'][0]
        temp_min = daily['temperature_2m_min'][0]
        rain = daily['precipitation_sum'][0]
        wind = daily['wind_speed_10m_max'][0]
        period = 'завтра' if tomorrow else 'сегодня'
        await update.message.reply_text(
            f'🌤 Погода на {period}\n📍 {route_name}\n\n'
            f'{weather_description(code)}\n'
            f'🌡 Температура: {temp_min}°C — {temp_max}°C\n'
            f'💧 Осадки: {rain} мм\n💨 Ветер: до {wind} км/ч\n\n'
            '⚠️ В горах погода может быстро меняться. '
            'Это ориентировочный прогноз, а не оценка безопасности маршрута.'
        )
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        await update.message.reply_text('❌ Не удалось получить погоду. Попробуй позже.')


# Подробный прогноз: пять отдельных дней, данные Open-Meteo каждые 3 часа.
WEATHER_DAY_PREFIX = '📅 Прогноз: '


def clothing_advice(feels_like, wind, rain, snow):
    """Примерный набор одежды для похода, не оценка безопасности выхода."""
    if feels_like <= -15:
        clothes = [
            'тёплое термобельё', 'флис или утепляющий средний слой',
            'тёплая пуховая куртка', 'ветро- и влагозащитный слой',
            'утеплённые штаны', 'зимние горные ботинки',
            'тёплые носки, шапка, бафф и варежки',
        ]
    elif feels_like <= -5:
        clothes = [
            'термобельё', 'флис', 'утеплённая куртка',
            'ветрозащитный слой', 'тёплые штаны',
            'подходящие горные ботинки, шапка и перчатки',
        ]
    elif feels_like <= 5:
        clothes = [
            'базовый слой', 'флис', 'куртка от ветра и осадков',
            'длинные походные брюки', 'горные ботинки',
            'шапка и перчатки в запас',
        ]
    elif feels_like <= 15:
        clothes = [
            'дышащая кофта или футболка', 'лёгкий флис',
            'ветровка', 'походные брюки и обувь',
        ]
    else:
        clothes = [
            'дышащая одежда', 'лёгкие походные брюки',
            'головной убор', 'ветровка на случай смены погоды',
        ]
    if rain or snow:
        clothes.append('непромокаемая внешняя одежда')
    if wind >= 30:
        clothes.append('надёжная защита лица и рук от ветра')
    return '🧥 Что надеть:\n• ' + '\n• '.join(dict.fromkeys(clothes))


async def show_five_day_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('route') not in ROUTES:
        await update.message.reply_text('Сначала выбери маршрут.')
        return
    today = datetime.now(ZoneInfo('Asia/Almaty')).date()
    dates = [(today + timedelta(days=i)).isoformat() for i in range(5)]
    context.user_data['weather_dates'] = dates
    keyboard = ReplyKeyboardMarkup(
        [[WEATHER_DAY_PREFIX + day] for day in dates]
        + [['⬅️ К маршруту'], ['🏠 Главное меню']],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        '🌤 Выбери день для подробного прогноза на 3-часовых интервалах:',
        reply_markup=keyboard,
    )


async def send_detailed_weather(update: Update, context: ContextTypes.DEFAULT_TYPE, day: str):
    route_name = context.user_data.get('route')
    if route_name not in ROUTES or day not in context.user_data.get('weather_dates', []):
        await update.message.reply_text('Сначала выбери маршрут и день прогноза.')
        return
    route = ROUTES[route_name]
    params = {
        'latitude': route['latitude'],
        'longitude': route['longitude'],
        'hourly': 'temperature_2m,apparent_temperature,precipitation_probability,precipitation,wind_speed_10m,weather_code',
        'timezone': 'Asia/Almaty',
        'start_date': day,
        'end_date': day,
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get('https://api.open-meteo.com/v1/forecast', params=params)
            response.raise_for_status()
            hourly = response.json()['hourly']

        entries = []
        for i, timestamp in enumerate(hourly['time']):
            hour = int(timestamp[11:13])
            if hour % 3 != 0:
                continue
            temp = hourly['temperature_2m'][i]
            feels = hourly['apparent_temperature'][i]
            wind = hourly['wind_speed_10m'][i]
            probability = hourly['precipitation_probability'][i]
            amount = hourly['precipitation'][i]
            code = hourly['weather_code'][i]
            if any(v is None for v in (temp, feels, wind, probability, amount, code)):
                continue
            entries.append((hour, temp, feels, wind, probability, amount, code))

        if not entries:
            await update.message.reply_text('Нет данных для выбранного дня.')
            return

        lines = [f'🏔 {route_name}', f'📅 {day} (время Алматы)', '',
                 'Температура каждые 3 часа:']
        for hour, temp, feels, wind, probability, amount, code in entries:
            lines.append(
                f'{hour:02d}:00  {weather_description(code)} | {temp:+.0f}°C '
                f'(ощущ. {feels:+.0f}°C)\n'
                f'   💨 {wind:.0f} км/ч | 💧 {probability:.0f}% ({amount:.1f} мм)'
            )

        # Берём самый холодный по ощущению период и наибольший ветер,
        # чтобы рекомендации не ориентировались только на дневной максимум.
        coldest = min(item[2] for item in entries)
        strongest_wind = max(item[3] for item in entries)
        wet = any(item[5] > 0 or item[4] >= 60 for item in entries)
        snow = any(item[6] in (71, 73, 75, 77, 85, 86) for item in entries)
        lines.extend(['', clothing_advice(coldest, strongest_wind, wet, snow)])
        if coldest <= -15 or strongest_wind >= 40:
            lines.append('\n⚠️ Сильный холод или ветер: лучше пересмотреть выход и проверить предупреждения.')
        lines.append(
            '\n⚠️ Это модельный прогноз для координат вершины, а не гарантия условий '
            'на тропе. В высокогорье погода меняется быстро; проверяй '
            'официальные предупреждения, состояние маршрута и экипировку.'
        )
        await update.message.reply_text('\n'.join(lines))
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        await update.message.reply_text('❌ Не удалось получить подробный прогноз. Попробуй позже.')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (update.message.text or '').strip()
    if message == '🏔 Маршруты':
        context.user_data.pop('route', None)
        await show_categories(update)
        return
    if message == '🌐 Наши соцсети':
        await show_socials(update)
        return
    if message in ('⬅️ Назад', '🏠 Главное меню'):
        context.user_data.clear()
        await update.message.reply_text('🏠 Главное меню:', reply_markup=HOME)
        return
    if message in CATEGORIES:
        await show_category_routes(update, context, message)
        return
    if message == '⬅️ К сложностям':
        context.user_data.pop('route', None)
        context.user_data.pop('category', None)
        await show_categories(update)
        return
    if message == '⬅️ К списку маршрутов':
        category = context.user_data.get('category')
        if category in CATEGORIES:
            await show_category_routes(update, context, category)
        else:
            await show_categories(update)
        return
    if message in ROUTES:
        category = context.user_data.get('category')
        if category in CATEGORIES and message in CATEGORIES[category]:
            await show_route(update, context, message)
        else:
            await update.message.reply_text('Сначала выбери категорию маршрутов.')
        return
    if message == '📅 Погода на 5 дней':
        await show_five_day_menu(update, context)
        return
    if message.startswith(WEATHER_DAY_PREFIX):
        await send_detailed_weather(update, context, message[len(WEATHER_DAY_PREFIX):])
        return
    if message == '⬅️ К маршруту':
        route_name = context.user_data.get('route')
        if route_name in ROUTES:
            await show_route(update, context, route_name)
        else:
            await show_categories(update)
        return
    if message == '📥 Скачать GPX-трек':
        await send_track(update, context)
        return
    if message == '🌤 Погода сегодня':
        await send_weather(update, context, tomorrow=False)
        return
    if message == '🌤 Погода завтра':
        await send_weather(update, context, tomorrow=True)
        return
    await update.message.reply_text('Выбери действие с помощью кнопок или отправь /start.')


def main():
    if not TOKEN or not TOKEN.strip():
        raise RuntimeError('Не найден TELEGRAM_BOT_TOKEN в настройках Render.')
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not render_url:
        raise RuntimeError('Не найден RENDER_EXTERNAL_URL в настройках Render.')
    app = Application.builder().token(TOKEN.strip()).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    port = int(os.environ.get('PORT', '10000'))
    webhook_path = 'telegram-webhook'
    print(f'Запускаю webhook на порту {port}', flush=True)
    app.run_webhook(
        listen='0.0.0.0',
        port=port,
        url_path=webhook_path,
        webhook_url=f"{render_url.rstrip('/')}/{webhook_path}",
        drop_pending_updates=False,
    )


if __name__ == '__main__':
    main()
