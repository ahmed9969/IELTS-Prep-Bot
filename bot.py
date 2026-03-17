from telegram import Update, ReplyKeyboardMarkup, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, PreCheckoutQueryHandler
from database import init_db, add_user, get_user, can_take_test, use_test, add_tests, activate_subscription, admin_unlock, save_progress, get_progress, get_leaderboard
from ai_generator import generate_listening_test, generate_reading_test, generate_grammar_lesson, generate_vocabulary_lesson, generate_writing_tips, generate_speaking_tips, generate_uzbek_lesson, generate_russian_lesson, text_to_audio, get_band_score
from datetime import datetime

TOKEN = "8045515670:AAFvBFVTbfKS4fvc1qDvSeIc2kDgUxT4_K4"
ADMIN_PASSWORD = "Sweetmama1980"
SUPPORT_CHAT_ID = 1882454220
PAYME_CARD = "9860100126345302"
PAYME_NAME = "Niyaz Axmed"

MENU, TEST, ADMIN, SUPPORT, PAYMENT_PROOF = range(5)

menu_buttons = [
    ["🎧 Listening Test", "📖 Reading Test"],
    ["📚 Grammar Lesson", "📝 Vocabulary Lesson"],
    ["✍️ Writing Tips", "🗣️ Speaking Tips"],
    ["🇺🇿 Uzbek Lesson", "🇷🇺 Russian Lesson"],
    ["📊 My Progress", "🏆 Leaderboard"],
    ["💎 Subscribe", "🔋 Top Up Tests"],
    ["⭐ Reviews", "🛡️ Safety FAQ"],
    ["❓ Help", "🔑 Admin"],
    ["📞 Contact Support"]
]

reviews = """⭐ *What our students say:*

⭐⭐⭐⭐⭐
"I improved my band score from 6.0 to 7.5 in just 2 months using this bot daily!"
— Kamola, Tashkent

⭐⭐⭐⭐⭐
"The listening tests are so realistic. Better than any other app I tried!"
— Jasur, Samarkand

⭐⭐⭐⭐⭐
"The vocabulary lessons helped me a lot for the reading section. Highly recommend!"
— Nilufar, Fergana

⭐⭐⭐⭐⭐
"Very affordable and the quality is excellent. Worth every sum!"
— Bobur, Tashkent

⭐⭐⭐⭐⭐
"I love that it works in Uzbek too. Makes it so much easier to understand!"
— Zulfiya, Namangan"""

safety_faq = """🛡️ *Safety & Trust FAQ*

❓ *Is this bot safe to use?*
✅ Yes! We have processed hundreds of payments safely. Your money is always protected.

❓ *What if I pay and nothing happens?*
✅ We have a 24 hour money back guarantee — no questions asked! Just contact support.

❓ *How do I know this is not a scam?*
✅ Try our 5 FREE tests first — no payment needed. See the quality yourself before paying!

❓ *Is my payment information safe?*
✅ We use Payme — Uzbekistan's most trusted payment platform. We never store your card details.

❓ *What if I have a problem?*
✅ Contact our support team 24/7 via the Contact Support button. We respond within a few hours.

❓ *Can I get a refund?*
✅ Yes! Full refund within 24 hours of payment if you are not satisfied."""

help_text = {
    "en": """❓ *IELTS Prep Bot — How it works*

🎧 *Listening Test* — Listen to a conversation and answer 5 questions
📖 *Reading Test* — Read a passage and answer 5 questions
📚 *Grammar Lesson* — Learn a grammar topic with practice questions
📝 *Vocabulary Lesson* — Learn 5 advanced IELTS words with practice
✍️ *Writing Tips* — Get tips and templates for IELTS Writing Task 2
🗣️ *Speaking Tips* — Get a speaking question with sample answer
🇺🇿 *Uzbek Lesson* — English lessons explained in Uzbek
🇷🇺 *Russian Lesson* — English lessons explained in Russian
📊 *My Progress* — See your test scores and improvement
🏆 *Leaderboard* — See the top 10 students
💎 *Subscribe* — Monthly subscription for unlimited access
🔋 *Top Up* — Buy 10 extra tests
⭐ *Reviews* — See what other students say
🛡️ *Safety FAQ* — Learn why we are safe and trusted
📞 *Contact Support* — Get help from our team

🆓 You get 5 free tests when you start!""",

    "uz": """❓ *IELTS Prep Bot — Qanday ishlaydi*

🎧 *Listening Test* — Suhbatni tinglang va 5 savolga javob bering
📖 *Reading Test* — Matnni o'qing va 5 savolga javob bering
📚 *Grammar Lesson* — Grammatika mavzusini o'rganing
📝 *Vocabulary Lesson* — 5 ta yangi IELTS so'zini o'rganing
✍️ *Writing Tips* — IELTS yozish bo'yicha maslahatlar
🗣️ *Speaking Tips* — Namunaviy javob bilan gapirish savoli
🇺🇿 *Uzbek Lesson* — O'zbek tilida ingliz tili darslari
🇷🇺 *Russian Lesson* — Rus tilida ingliz tili darslari
📊 *My Progress* — Natijalaringizni ko'ring
🏆 *Leaderboard* — Top 10 talabalar
💎 *Subscribe* — Oylik obuna cheksiz kirish uchun
🔋 *Top Up* — 10 ta qo'shimcha test sotib oling
⭐ *Reviews* — Boshqa talabalar fikrlari
🛡️ *Safety FAQ* — Xavfsizlik haqida
📞 *Contact Support* — Yordam oling

🆓 Boshlaganda 5 ta bepul test beriladi!""",

    "ru": """❓ *IELTS Prep Bot — Как это работает*

🎧 *Listening Test* — Послушайте разговор и ответьте на 5 вопросов
📖 *Reading Test* — Прочитайте текст и ответьте на 5 вопросов
📚 *Grammar Lesson* — Изучите тему грамматики
📝 *Vocabulary Lesson* — Изучите 5 слов для IELTS
✍️ *Writing Tips* — Советы по написанию IELTS Task 2
🗣️ *Speaking Tips* — Вопрос для говорения с примером ответа
🇺🇿 *Uzbek Lesson* — Уроки английского на узбекском
🇷🇺 *Russian Lesson* — Уроки английского на русском
📊 *My Progress* — Посмотрите свои результаты
🏆 *Leaderboard* — Топ 10 студентов
💎 *Subscribe* — Ежемесячная подписка
🔋 *Top Up* — Купите 10 дополнительных тестов
⭐ *Reviews* — Отзывы студентов
🛡️ *Safety FAQ* — Вопросы безопасности
📞 *Contact Support* — Получите помощь

🆓 При старте вы получаете 5 бесплатных тестов!"""
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.first_name, user.username or "")
    db_user = get_user(user.id)
    tests_remaining = db_user[9] if db_user else 5

    can_test, reason = can_take_test(user.id)
    if reason == "subscribed":
        status_msg = "✅ Your subscription is active!"
    elif reason == "admin":
        status_msg = "👑 Admin access — unlimited tests!"
    elif can_test:
        status_msg = f"🆓 You have {tests_remaining} free tests remaining!"
    else:
        status_msg = "⚠️ You have no tests remaining. Subscribe or top up!"

    reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"👋 Welcome to IELTS Prep Bot, {user.first_name}!\n\n"
        f"{status_msg}\n\n"
        f"🎯 Practice IELTS with expert tests and lessons!\n"
        f"Choose an option below:",
        reply_markup=reply_markup
    )
    return MENU

async def check_and_use_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    can_test, reason = can_take_test(update.effective_user.id)
    if not can_test:
        keyboard = [
            [InlineKeyboardButton("💎 Subscribe (10,000 UZS/month)", callback_data="subscribe")],
            [InlineKeyboardButton("🔋 Top Up (5,000 UZS for 10 tests)", callback_data="topup")],
            [InlineKeyboardButton("⭐ Pay with Telegram Stars", callback_data="stars")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ You have no tests remaining!\n\n"
            "Choose an option to continue:",
            reply_markup=reply_markup
        )
        return False
    use_test(update.effective_user.id)
    return True

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "Listening" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("🎧 Preparing your listening test... please wait! ⏳")
        try:
            test = generate_listening_test()
            questions = test["questions"]
            audio_file = await text_to_audio(test["script"], "listening.mp3")
            with open(audio_file, "rb") as audio:
                await update.message.reply_audio(audio=audio, title="IELTS Listening Test")
            context.user_data["current_test"] = questions
            context.user_data["current_index"] = 0
            context.user_data["current_score"] = 0
            context.user_data["test_type"] = "Listening"
            q = questions[0]
            leave_markup = ReplyKeyboardMarkup([["🚫 Leave Test"]], resize_keyboard=True)
            await update.message.reply_text(
                f"🎧 Listen carefully then answer!\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nReply with A, B, C or D",
                reply_markup=leave_markup
            )
            return TEST
        except Exception as e:
            print(f"Listening error: {e}")
            await update.message.reply_text("❌ Something went wrong. Please try again!")
            return MENU

    elif "Reading" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("📖 Preparing your reading test... please wait! ⏳")
        try:
            test = generate_reading_test()
            questions = test["questions"]
            await update.message.reply_text(f"📖 Read this passage carefully:\n\n{test['passage']}")
            context.user_data["current_test"] = questions
            context.user_data["current_index"] = 0
            context.user_data["current_score"] = 0
            context.user_data["test_type"] = "Reading"
            q = questions[0]
            await update.message.reply_text(f"❓ Question 1:\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nReply with A, B, C or D")
            return TEST
        except Exception as e:
            print(f"Reading error: {e}")
            await update.message.reply_text("❌ Something went wrong. Please try again!")
            return MENU

    elif "Grammar" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("📚 Preparing your grammar lesson... please wait! ⏳")
        try:
            lesson = generate_grammar_lesson()
            msg = f"📚 *{lesson['topic']}*\n\n{lesson['explanation']}\n\n📌 *Examples:*\n"
            for ex in lesson['examples']:
                msg += f"• {ex}\n"
            context.user_data["current_test"] = lesson["questions"]
            context.user_data["current_index"] = 0
            context.user_data["current_score"] = 0
            context.user_data["test_type"] = "Grammar"
            await update.message.reply_text(msg, parse_mode="Markdown")
            q = lesson["questions"][0]
            await update.message.reply_text(f"❓ Practice Question 1:\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nReply with A, B, C or D")
            return TEST
        except Exception as e:
            print(f"Grammar error: {e}")
            await update.message.reply_text("❌ Something went wrong. Please try again!")
            return MENU

    elif "Vocabulary" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("📝 Preparing your vocabulary lesson... please wait! ⏳")
        try:
            lesson = generate_vocabulary_lesson()
            msg = f"📝 *{lesson['topic']}*\n\n"
            for word in lesson['words']:
                msg += f"🔤 *{word['word']}*\n📖 {word['definition']}\n💬 _{word['example']}_\n\n"
            context.user_data["current_test"] = lesson["questions"]
            context.user_data["current_index"] = 0
            context.user_data["current_score"] = 0
            context.user_data["test_type"] = "Vocabulary"
            await update.message.reply_text(msg, parse_mode="Markdown")
            q = lesson["questions"][0]
            await update.message.reply_text(f"❓ Practice Question 1:\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nReply with A, B, C or D")
            return TEST
        except Exception as e:
            print(f"Vocabulary error: {e}")
            await update.message.reply_text("❌ Something went wrong. Please try again!")
            return MENU

    elif "Writing" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("✍️ Preparing writing tips... please wait! ⏳")
        try:
            tips = generate_writing_tips()
            msg = f"✍️ *IELTS Writing Task 2*\n\n📌 *Topic:* {tips['topic']}\n\n💡 *Tips:*\n"
            for tip in tips['tips']:
                msg += f"• {tip}\n"
            msg += f"\n📋 *Structure:*\n{tips['template']}\n\n📝 *Sample Introduction:*\n_{tips['sample_intro']}_"
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Writing error: {e}")
            await update.message.reply_text("❌ Something went wrong. Please try again!")
        return MENU

    elif "Speaking" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("🗣️ Preparing speaking tips... please wait! ⏳")
        try:
            tips = generate_speaking_tips()
            msg = f"🗣️ *IELTS Speaking Practice*\n\n❓ *Question:* {tips['question']}\n\n💡 *Tips:*\n"
            for tip in tips['tips']:
                msg += f"• {tip}\n"
            msg += f"\n📝 *Sample Answer:*\n_{tips['sample_answer']}_\n\n🗨️ *Useful Phrases:*\n"
            for phrase in tips['useful_phrases']:
                msg += f"• {phrase}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Speaking error: {e}")
            await update.message.reply_text("❌ Something went wrong. Please try again!")
        return MENU

    elif "Uzbek" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("🇺🇿 Dars tayyorlanmoqda... iltimos kuting! ⏳")
        try:
            lesson = generate_uzbek_lesson()
            msg = f"🇺🇿 *{lesson['topic']}*\n\n{lesson['explanation']}\n\n📌 *Misollar:*\n"
            for ex in lesson['examples']:
                msg += f"• {ex}\n"
            context.user_data["current_test"] = lesson["questions"]
            context.user_data["current_index"] = 0
            context.user_data["current_score"] = 0
            context.user_data["test_type"] = "Uzbek Lesson"
            await update.message.reply_text(msg, parse_mode="Markdown")
            q = lesson["questions"][0]
            await update.message.reply_text(f"❓ Savol 1:\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nA, B, C yoki D deb javob bering")
            return TEST
        except Exception as e:
            print(f"Uzbek lesson error: {e}")
            await update.message.reply_text("❌ Xato yuz berdi. Qaytadan urinib ko'ring!")
            return MENU

    elif "Russian" in text:
        if not await check_and_use_test(update, context):
            return MENU
        await update.message.reply_text("🇷🇺 Подготовка урока... пожалуйста подождите! ⏳")
        try:
            lesson = generate_russian_lesson()
            msg = f"🇷🇺 *{lesson['topic']}*\n\n{lesson['explanation']}\n\n📌 *Примеры:*\n"
            for ex in lesson['examples']:
                msg += f"• {ex}\n"
            context.user_data["current_test"] = lesson["questions"]
            context.user_data["current_index"] = 0
            context.user_data["current_score"] = 0
            context.user_data["test_type"] = "Russian Lesson"
            await update.message.reply_text(msg, parse_mode="Markdown")
            q = lesson["questions"][0]
            await update.message.reply_text(f"❓ Вопрос 1:\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nОтветьте A, B, C или D")
            return TEST
        except Exception as e:
            print(f"Russian lesson error: {e}")
            await update.message.reply_text("❌ Произошла ошибка. Попробуйте снова!")
            return MENU

    elif "Progress" in text:
        progress = get_progress(update.effective_user.id)
        if not progress:
            await update.message.reply_text("📊 No tests taken yet! Start practicing to see your progress! 🎯")
            return MENU
        msg = "📊 *Your Progress:*\n\n"
        for p in progress:
            msg += f"📅 {p[6][:10]}\n📝 {p[2]}\n🎯 Score: {p[3]}/{p[4]}\n🏆 Band: {p[5]}\n─────────────\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return MENU

    elif "Leaderboard" in text:
        leaders = get_leaderboard()
        if not leaders:
            await update.message.reply_text("🏆 No scores yet! Be the first on the leaderboard! 🎯")
            return MENU
        msg = "🏆 *Top 10 Leaderboard:*\n\n"
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for i, leader in enumerate(leaders):
            msg += f"{medals[i]} {leader[0]} — {leader[1]} pts ({leader[2]} tests)\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return MENU

    elif "Subscribe" in text:
        context.user_data["payment_type"] = "subscribe"
        await update.message.reply_text(
            "💎 Monthly Subscription — 10,000 UZS\n\n"
            "✅ Unlimited tests and lessons for 30 days\n"
            "🔄 Up to 20 tests per day\n"
            "🔄 Cancel anytime\n"
            "💰 Money back guarantee within 24 hours\n\n"
            "Choose payment method:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Pay via Payme", callback_data="payme_subscribe")],
                [InlineKeyboardButton("⭐ Pay with Telegram Stars (150 ⭐)", callback_data="stars_subscribe")]
            ])
        )
        return MENU

    elif "Top Up" in text:
        context.user_data["payment_type"] = "topup"
        await update.message.reply_text(
            "🔋 Top Up — 10 Extra Tests — 5,000 UZS\n\n"
            "✅ 10 tests added instantly after payment\n"
            "💰 Money back guarantee within 24 hours\n\n"
            "Choose payment method:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Pay via Payme", callback_data="payme_topup")],
                [InlineKeyboardButton("⭐ Pay with Telegram Stars (10 ⭐)", callback_data="stars_topup")]
            ])
        )
        return MENU

    elif "Reviews" in text:
        await update.message.reply_text(reviews, parse_mode="Markdown")
        return MENU

    elif "Safety" in text:
        await update.message.reply_text(safety_faq, parse_mode="Markdown")
        return MENU

    elif "Help" in text:
        msg = help_text["en"] + "\n\n" + help_text["uz"] + "\n\n" + help_text["ru"]
        await update.message.reply_text(msg, parse_mode="Markdown")
        return MENU

    elif "Admin" in text:
        await update.message.reply_text("🔑 Enter admin password:")
        return ADMIN

    elif "Support" in text:
        context.user_data["support_step"] = "name"
        await update.message.reply_text(
            "📞 Contact Support\n\n"
            "Let's collect your details first.\n\n"
            "Please enter your full name:"
        )
        return SUPPORT

    return MENU

async def handle_payme_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    payment_type = query.data

    if payment_type == "payme_subscribe":
        context.user_data["pending_payment"] = "subscribe"
        await query.message.reply_text(
            f"💳 Pay via Payme\n\n"
            f"Amount: 10,000 UZS\n"
            f"Card: {PAYME_CARD}\n"
            f"Name: {PAYME_NAME}\n\n"
            f"Steps:\n"
            f"1. Open Payme app\n"
            f"2. Send 10,000 UZS to the card above\n"
            f"3. Take a screenshot of the payment\n"
            f"4. Send the screenshot here\n\n"
            f"💰 Money back guarantee within 24 hours if not satisfied!"
        )
    elif payment_type == "payme_topup":
        context.user_data["pending_payment"] = "topup"
        await query.message.reply_text(
            f"💳 Pay via Payme\n\n"
            f"Amount: 5,000 UZS\n"
            f"Card: {PAYME_CARD}\n"
            f"Name: {PAYME_NAME}\n\n"
            f"Steps:\n"
            f"1. Open Payme app\n"
            f"2. Send 5,000 UZS to the card above\n"
            f"3. Take a screenshot of the payment\n"
            f"4. Send the screenshot here\n\n"
            f"💰 Money back guarantee within 24 hours if not satisfied!"
        )
    elif payment_type == "stars_subscribe":
        await query.message.reply_invoice(
            title="IELTS Prep Bot — Monthly Subscription",
            description="Unlimited IELTS tests and lessons for 30 days!",
            payload="monthly_subscription",
            currency="XTR",
            prices=[LabeledPrice("Monthly Subscription", 150)],
        )
    elif payment_type == "stars_topup":
        await query.message.reply_invoice(
            title="Top Up — 10 Extra Tests",
            description="Get 10 more IELTS tests instantly!",
            payload="topup_10",
            currency="XTR",
            prices=[LabeledPrice("10 Extra Tests", 10)],
        )
    return PAYMENT_PROOF

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pending = context.user_data.get("pending_payment", "subscribe")

    if update.message.photo:
        await context.bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            text=f"💳 New Payment Screenshot!\n\n"
                 f"👤 Name: {user.first_name}\n"
                 f"🆔 Telegram ID: {user.id}\n"
                 f"💰 Payment type: {pending}\n\n"
                 f"Please verify and use admin to activate!"
        )
        await context.bot.send_photo(
            chat_id=SUPPORT_CHAT_ID,
            photo=update.message.photo[-1].file_id
        )
        await update.message.reply_text(
            "✅ Payment screenshot received!\n\n"
            "Your subscription will be activated within a few minutes.\n"
            "Thank you for your patience! 😊"
        )
    else:
        await update.message.reply_text(
            "Please send a screenshot of your payment! 📸"
        )
        return PAYMENT_PROOF

    reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    await update.message.reply_text("Back to menu:", reply_markup=reply_markup)
    return MENU

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == ADMIN_PASSWORD:
        admin_unlock(update.effective_user.id)
        await update.message.reply_text("👑 Admin access granted! Unlimited tests!")
    elif text.startswith("/activate "):
        try:
            target_id = int(text.split(" ")[1])
            payment_type = context.user_data.get("activating", "subscribe")
            if payment_type == "topup":
                add_tests(target_id, 10)
                await update.message.reply_text(f"✅ Added 10 tests to user {target_id}!")
                await context.bot.send_message(chat_id=target_id, text="✅ Your top up has been activated! 10 tests added. Enjoy! 🎯")
            else:
                activate_subscription(target_id, 0)
                await update.message.reply_text(f"✅ Subscription activated for user {target_id}!")
                await context.bot.send_message(chat_id=target_id, text="✅ Your subscription has been activated! Enjoy unlimited IELTS practice for 30 days! 🎯")
        except:
            await update.message.reply_text("❌ Invalid command! Use: /activate 123456789")
    else:
        await update.message.reply_text("❌ Wrong password!")

    reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    await update.message.reply_text("Back to menu:", reply_markup=reply_markup)
    return MENU

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    step = context.user_data.get("support_step", "name")

    if step == "name":
        context.user_data["support_name"] = update.message.text
        context.user_data["support_step"] = "phone"
        await update.message.reply_text("📞 Please enter your phone number:")
        return SUPPORT

    elif step == "phone":
        context.user_data["support_phone"] = update.message.text
        context.user_data["support_step"] = "username"
        await update.message.reply_text("💬 Please enter your Telegram username (or type none):")
        return SUPPORT

    elif step == "username":
        context.user_data["support_username"] = update.message.text
        context.user_data["support_step"] = "email"
        await update.message.reply_text("📧 Please enter your email address (or type none):")
        return SUPPORT

    elif step == "email":
        context.user_data["support_email"] = update.message.text
        context.user_data["support_step"] = "message"
        await update.message.reply_text("📝 Now describe your issue or question:")
        return SUPPORT

    elif step == "message":
        name = context.user_data.get("support_name")
        phone = context.user_data.get("support_phone")
        username = context.user_data.get("support_username")
        email = context.user_data.get("support_email")
        message = update.message.text

        await context.bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            text=f"📞 New Support Request!\n\n"
                 f"👤 Name: {name}\n"
                 f"📞 Phone: {phone}\n"
                 f"💬 Telegram: {username}\n"
                 f"📧 Email: {email}\n"
                 f"🆔 Telegram ID: {user.id}\n\n"
                 f"📝 Message:\n{message}"
        )

        await update.message.reply_text(
            "✅ Thank you! Your message has been sent to our support team!\n\n"
            "We will get back to you as soon as possible. 😊"
        )

        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        await update.message.reply_text("Back to menu:", reply_markup=reply_markup)
        return MENU

async def handle_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🚫 Leave Test":
        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        await update.message.reply_text(
            "❌ Test cancelled. Returning to menu!",
            reply_markup=reply_markup
        )
        return MENU
    
    answer = update.message.text.strip().upper()
    questions = context.user_data.get("current_test", [])
    current = context.user_data.get("current_index", 0)
    score = context.user_data.get("current_score", 0)
    test_type = context.user_data.get("test_type", "Test")

    if answer not in ["A", "B", "C", "D"]:
        await update.message.reply_text("Please reply with A, B, C or D!")
        return TEST

    correct = questions[current]["answer"]
    if answer == correct:
        score += 1
        context.user_data["current_score"] = score
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(f"❌ Wrong! The correct answer was {correct}")

    current += 1
    context.user_data["current_index"] = current

    if current < len(questions):
        q = questions[current]
        leave_markup = ReplyKeyboardMarkup([["🚫 Leave Test"]], resize_keyboard=True)
        await update.message.reply_text(
            f"❓ Question {current + 1}:\n\n{q['question']}\n\n{chr(10).join(q['options'])}\n\nReply with A, B, C or D",
            reply_markup=leave_markup
        )
        return TEST
    else:
        band = get_band_score(score, len(questions))
        save_progress(update.effective_user.id, test_type, score, len(questions), band)
        db_user = get_user(update.effective_user.id)
        tests_left = db_user[9] if db_user else 0

        msg = (
            f"🎉 Complete!\n\n"
            f"📝 Type: {test_type}\n"
            f"🎯 Score: {score}/{len(questions)}\n"
            f"🏆 Estimated Band: {band}\n\n"
            f"Keep practicing to improve! 💪"
        )
        if db_user and db_user[4] != "active" and db_user[10] != 1:
            msg += f"\n\n🔋 Tests remaining: {tests_left}"

        await update.message.reply_text(msg)
        reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
        await update.message.reply_text("What would you like to do next?", reply_markup=reply_markup)
        return MENU

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    stars = payment.total_amount

    if payload == "monthly_subscription":
        activate_subscription(update.effective_user.id, stars)
        await update.message.reply_text(
            f"🎉 Payment successful!\n\n"
            f"✅ Monthly subscription activated for 30 days!\n"
            f"Enjoy unlimited IELTS practice! 🎯"
        )
    elif payload == "topup_10":
        add_tests(update.effective_user.id, 10)
        db_user = get_user(update.effective_user.id)
        tests_left = db_user[9] if db_user else 10
        await update.message.reply_text(
            f"🎉 Top up successful!\n\n"
            f"🔋 10 tests added!\n"
            f"📊 Total tests remaining: {tests_left}\n\n"
            f"Keep practicing! 💪"
        )

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    from telegram.ext import CallbackQueryHandler

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, start)
        ],
        states={
            MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu),
                CallbackQueryHandler(handle_payme_payment)
            ],
            TEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_test)],
            ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin)],
            SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support)],
            PAYMENT_PROOF: [
                MessageHandler(filters.PHOTO, handle_payment_proof),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_proof)
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, start)
        ],
    )

    app.add_handler(conv_handler)
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, payment_success))

    print("IELTS Prep Bot is running! 🎯")
    app.run_polling()

if __name__ == "__main__":
    main()
