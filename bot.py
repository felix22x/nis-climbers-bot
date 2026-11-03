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
    '🏔 Пик Титова': {'file': 'Пик Титова.gpx', 'latitude': 43.075026, 'longitude': 77.048696},
    '🏔 Малая Алматинская кругосветка': {'file': 'Малая Алматинская кругосветка.gpx', 'latitude': 43.149454, 'longitude': 77.116494},
    '🏔 Пик Валерия Хрищатого': {'file': 'pik_khrishchatogo.gpx', 'latitude': 43.08761, 'longitude': 77.09589},
    '🏔 Пик Каргалинский — Пик Каменский': {'file': 'pik-kargalinskii-pik-kamenskii-cherez-kaskabas-spusk-cherez-.gpx', 'latitude': 43.060703, 'longitude': 76.854761},
    '🏔 Пик Карнизный через Проходное': {'file': 't303665559_karnizny_peak_through_the_gorge_prohodnoe_пик.gpx', 'latitude': 43.011832, 'longitude': 76.945988},
    '🏔 Пик Молодая Гвардия': {'file': '2022_07_24_0843_Wikiloc_Трек_на_пик_Молодая_Гвардия_часть_2_.gpx', 'latitude': 43.006825, 'longitude': 77.085311},
    '🏔 Пик Турист': {'file': '2025-07-06-1913 Космостанция-Пик Турист.gpx', 'latitude': 43.028767, 'longitude': 76.952073},
    '🏔 Пик Чкалова': {'file': 'Пик Чкалова с запада, 1А-1Б.gpx', 'latitude': 43.103611, 'longitude': 77.127500},
    '🏔 Большой Алматинский пик': {'file': 'БАП из Проходного.gpx', 'latitude': 43.055, 'longitude': 76.934167},
    '🏔 Пик Советов': {'file': 'Пик Советов (3).gpx', 'latitude': 43.023611, 'longitude': 77.037222},
    '🏔 Пик Антикайнен': {'file': 'Антикайнена_ 20-21 окт_ 2023 г_ 09_22_04.gpx', 'latitude': 43.072712, 'longitude': 77.111835},
    '🏔 Пик Физкультурник': {'file': '2023-07-14-1047 Пик Физкультурник.gpx', 'latitude': 43.092588, 'longitude': 77.115702},
    '🏔 Пик Букреева': {'file': 'Пионер_Подножие_Букреева_Лесной_перевал_Бутако.gpx', 'latitude': 43.166713, 'longitude': 77.134642},
    '🏔 Пик Погребецкого': {'file': 'Пик Погребецкого с юга.gpx', 'latitude': 43.034167, 'longitude': 77.071389},
    '🏔 Пик Кумбель': {'file': 'kok-zhailiau-tri-brata-kumbel.gpx', 'latitude': 43.120154, 'longitude': 77.030732},
    '🏔 Пик Малыш': {'file': 'Мемориал_Мынжылки_Пик_Малыш_Мемориал.gpx', 'latitude': 43.06586, 'longitude': 77.05686},
}


# Время указано по предоставленным участниками расписаниям; это не норматив и не прогноз.
ROUTE_TIMINGS = {
    '🏔 Пик Памяти друзей': [('00:00', 'Старт'), ('01:30', 'БАО'), ('04:00', 'Кемпинг-зона'), ('06:00', 'Хижина Кызылсай'), ('10:00', 'Пик Памяти друзей')],
    '🏔 Пик 28 героев Панфиловцев': [('03:05', 'КА'), ('04:18', 'Мынжылкы'), ('05:33', 'Альпинград'), ('05:35', 'Озеро ММ'), ('09:18', 'Перевал ММ'), ('10:01', 'Пик 28 героев Панфиловцев')],
    '🏔 Пик Молодежный': [('22:00', 'Блокпост — старт'), ('22:15', 'Труба БАО'), ('23:03', 'Альпийская Роза'), ('01:30', 'Перевал Шукыр (следующий день)'), ('08:00', 'Пик ВЛКСМ'), ('09:00', 'Пик Молодёжный')],
    '🏔 Пик Пила': [('03:50', 'АА, источники — старт'), ('06:00–06:30', 'Терра, завтрак'), ('08:20', 'Верховье ущелья Проходного'), ('10:30–11:00', 'Цирк Пилы, подножье перевала'), ('12:30', 'Пик Пила')],
    '🏔 Пик Скалистый': [('05:26', 'Эдельвейс — старт'), ('07:22', 'Ущелье возле Альпийской Розы'), ('11:20', 'Пик Скалистый')],
    '🏔 Пик Титова': [('05:37', 'Конец асфальта — старт'), ('05:50', 'Мемориал'), ('07:23', 'Мынжылкы'), ('07:57', 'Выход с Мынжылков'), ('11:00', 'Под сыпухой'), ('11:17', 'Сыпуха'), ('11:35', 'Перевал'), ('12:30', 'Пик Титова')],
    '🏔 Малая Алматинская кругосветка': [('07:23', 'Старт'), ('08:38', 'Ущелье'), ('09:32', 'Качели'), ('11:10', 'Фурманова'), ('11:56', 'Панорама'), ('12:35', 'Башута'), ('14:28', 'Чимбулачка'), ('15:12', 'Комби-2 — финиш')],
    '🏔 Пик Каргалинский — Пик Каменский': [('05:55', 'Алма-Арасан — старт'), ('08:09', 'Терра'), ('12:15', 'Перевал'), ('12:54', 'Пик Каргалинский'), ('14:40', 'Пик Каменский')],
    '🏔 Пик Карнизный через Проходное': [('04:50', 'АА — старт'), ('07:00', 'Терра'), ('07:20', 'Выход с Терры'), ('12:00', 'Алма-Алагир'), ('12:45', 'Выход с Алма-Алагира'), ('13:45', 'Пик Карнизный')],
    '🏔 Пик Молодая Гвардия': [('22:00', 'Эдельвейс — старт'), ('23:15', 'БАО'), ('01:30', 'Хижина (следующий день)'), ('03:30', 'Выход с хижины'), ('09:00', 'Пик Молодая Гвардия')],
    '🏔 Пик Турист': [('03:00', 'Алма-Арасан — старт'), ('05:00', 'Терра'), ('05:20', 'Выход с Терры'), ('07:50', 'Космо'), ('08:10', 'Выход с Космо'), ('10:30–11:00', 'Пик Турист')],
    '🏔 Большой Алматинский пик': [('05:39', 'Алма-Арасан — старт'), ('08:45', 'Поляна Терра'), ('13:31', 'Южный пик'), ('14:14', 'Северный пик')],
    '🏔 Пик Советов': [('01:40', 'Эдельвейс — старт'), ('03:05', 'БАО'), ('03:13', 'Выход с БАО'), ('04:47', 'Кемпинг'), ('05:20', 'Выход с кемпинга'), ('06:46', '77-й меридиан'), ('09:15', 'Пик Советов')],
    '🏔 Пик Физкультурник': [('07:30', 'Шымбулак — старт'), ('09:05', 'Комби-2'), ('09:40', 'Выход с Комби-2'), ('11:20', 'Нунатак'), ('11:37', 'Выход с Нунатака'), ('14:40', 'Пик Физкультурник')],
    '🏔 Пик Букреева': [('08:00', 'Остановка «Пионер» — старт'), ('09:30', 'Зелёная табличка'), ('12:00', 'Пик Букреева')],
    '🏔 Пик Погребецкого': [('18:00', 'Эдельвейс — старт'), ('19:30', 'БАО'), ('21:30', 'Кемпинг-зона'), ('22:45', 'Хижина БАУ'), ('00:45', 'Хижина Кызылсай (следующий день)'), ('01:30', 'Выход с хижины'), ('02:30', 'Под пиком'), ('04:00', 'Пик Погребецкого')],
    '🏔 Пик Кумбель': [('07:31', 'Старт'), ('10:02', 'Кок-Жайлау'), ('12:02', 'Три Брата'), ('13:17', 'Пик Кумбель')],
    '🏔 Пик Малыш': [('04:00', 'Медеу — старт'), ('05:20', 'Мынжылкы'), ('07:56', 'Беседка на Т1'), ('09:40', 'Пик Малыш')],
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
        '🏔 Пик Титова',
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

HOME = ReplyKeyboardMarkup(
    [['🏔 Маршруты'], ['🌐 Наши соцсети'], ['🔴 Регистрация МЧС 🔴']],
    resize_keyboard=True,
)
DIFFICULTY_MENU = ReplyKeyboardMarkup(
    [['🟢 Лёгкие'], ['🟡 Средние'], ['🔴 Сложные'], ['⬅️ Назад']],
    resize_keyboard=True,
)
ROUTE_MENU = ReplyKeyboardMarkup(
    [['📥 Скачать GPX-трек'], ['⏱ Тайминги маршрута'], ['🌤 Погода сегодня', '🌤 Погода завтра'],
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
    buttons = [['📥 Скачать GPX-трек']]
    if route_name in ROUTE_TIMINGS:
        buttons.append(['⏱ Тайминги маршрута'])
    buttons += [['🌤 Погода сегодня', '🌤 Погода завтра'],
                ['📅 Погода на 5 дней'],
                ['⬅️ К списку маршрутов'], ['🏠 Главное меню']]
    await update.message.reply_text(
        f'{route_name}\n\nЧто хочешь узнать?',
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True),
    )


async def send_timings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    route_name = context.user_data.get('route')
    if route_name not in ROUTES:
        await update.message.reply_text('Сначала выбери маршрут.')
        return
    timings = ROUTE_TIMINGS.get(route_name)
    if not timings:
        await update.message.reply_text('Для этого маршрута тайминги пока не добавлены.')
        return

    # Диапазоны обозначают возможное время достижения точки или остановки.
    # При переходе через полночь учитываем следующие сутки.
    def minutes(time_string):
        first = time_string.split('–')[0]
        hour, minute = map(int, first.split(':'))
        return hour * 60 + minute

    elapsed = 0
    previous = minutes(timings[0][0])
    for time_string, _ in timings[1:]:
        current = minutes(time_string)
        elapsed += (current - previous) % (24 * 60)
        previous = current
    hours, mins = divmod(elapsed, 60)
    duration = f'{hours} ч {mins:02d} мин'
    if '–' in timings[-1][0]:
        end = timings[-1][0].split('–')[-1]
        end_minutes = minutes(end)
        start_minutes = minutes(timings[-1][0])
        max_elapsed = elapsed + (end_minutes - start_minutes) % (24 * 60)
        max_h, max_m = divmod(max_elapsed, 60)
        duration += f' — {max_h} ч {max_m:02d} мин'

    lines = [f'⏱ Тайминги: {route_name}', '']
    lines.extend(f'{time_string} — {point}' for time_string, point in timings)
    lines.extend(['', f'⏳ Общее время: {duration}', '',
                  '⚠️ Это примерное расписание из опыта участников, а не гарантия времени прохождения. '
                  'Учитывай погоду, состояние тропы, световой день и подготовку группы.'])
    await update.message.reply_text('\n'.join(lines))


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
    if message == '🔴 Регистрация МЧС 🔴':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('🔴 Перейти к регистрации', url='https://www.almatyhike.kz/ru')]
        ])
        await update.message.reply_text(
            'Регистрация перед походом:', reply_markup=keyboard
        )
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
    if message == '⏱ Тайминги маршрута':
        await send_timings(update, context)
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
    app = (
        Application.builder()
        .token(TOKEN.strip())
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .get_updates_connect_timeout(30)
        .get_updates_read_timeout(30)
        .build()
    )
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
        bootstrap_retries=10,
    )


if __name__ == '__main__':
    main()
    
