    keyboard = [
        [InlineKeyboardButton(
            "💬 WhatsApp",
            url="https://chat.whatsapp.com/Gt5lEOMfrNYADWl6q4pnkg"
        )],
        [InlineKeyboardButton(
            "📸 Instagram",
            url="https://www.instagram.com/nis_climbers"
        )],
        [InlineKeyboardButton(
            "🎵 TikTok",
            url="https://www.tiktok.com/@nis_climbers"
        )],
    ]

    await update.message.reply_text(
        "🌐 Наши социальные сети:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()
    if text == "🌐 Наши соцсети":
        await show_socials(update, context)
        return
    
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
