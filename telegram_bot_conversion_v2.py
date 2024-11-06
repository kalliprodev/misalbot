from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from pdf2docx import Converter
from docx2pdf import convert
import os

# Bot tokeningiz va kanal username’ini kiriting
API_TOKEN = '7262665336:AAH1esqWR-qFhrgVVL244Y7EUEpDyxUdMTo'  # O'zingizning bot tokeningizni kiriting
CHANNEL_USERNAME = '@kallitest'  # O'zingizning kanalingiz username’ini yozing

# Telegram bot dasturini ishga tushirish
app = ApplicationBuilder().token(API_TOKEN).build()

# Foydalanuvchini kanalda obuna ekanligini tekshiruvchi funksiya
async def is_user_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Kanalǵa aǵza bolmaǵansiz! {e}")
        return False

# Start komandasi, tugmalar bilan boshlash
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Foydalanuvchining kanalingizga obuna bo‘lishini tekshirish
    is_subscribed = await is_user_subscribed(user_id, context)
    
    if is_subscribed:
        keyboard = [
            [
                InlineKeyboardButton("WORD'tı PDF'ke aylandırıw", callback_data="word_to_pdf"),
                InlineKeyboardButton("PDF'tı WORD'qa aylandırıw", callback_data="pdf_to_word")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("Sálem! Qanday konvertaciya kerek?", reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            f"Ótinish, botdan paydalanıw ushın kanalǵa aǵza bolıń : {CHANNEL_USERNAME}\n"
    " Aǵza bolǵanıńızdan keyin /start buyrıǵın qayta basıń."
        )

# Tugmalarni tanlashda fayl yuklashni so‘rash
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    is_subscribed = await is_user_subscribed(user_id, context)
    
    if is_subscribed:
        # Tugmani bosilganda qaysi turdagi o‘girish kerakligini saqlash
        if query.data == "word_to_pdf":
            context.user_data['conversion_type'] = "word_to_pdf"
            await query.message.reply_text("Word hújjetti júkleń.")
        elif query.data == "pdf_to_word":
            context.user_data['conversion_type'] = "pdf_to_word"
            await query.message.reply_text("PDF hújjetti júkleń.")
    else:
        await query.message.reply_text(
            f"Ótinish, botdan paydalanıw ushın kanalǵa aǵza bolıń : {CHANNEL_USERNAME}\n"
    "Aǵza bolǵanıńızdan keyin /start buyrıǵın qayta basıń."
        )

# Faylni qabul qilish va qayta ishlash
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_subscribed = await is_user_subscribed(user_id, context)

    if not is_subscribed:
        await update.message.reply_text(
            f"Ótinish, botdan paydalanıw ushın kanalǵa aǵza bolıń : {CHANNEL_USERNAME}\n"
    "Aǵza bolǵanıńızdan keyin /start buyrıǵın qayta basıń."
        )
        return

    file = await update.message.document.get_file()
    conversion_type = context.user_data.get('conversion_type')
    
    if conversion_type == "word_to_pdf":
        await update.message.reply_text("Hújjet PDF formatına ózgertilip atır... Iltimas kútiń ")
        await file.download_to_drive("input.docx")
        output_file = "output.pdf"
        
        # Word to PDF aylantirish (docx2pdf bilan)
        try:
            convert("input.docx", output_file)
        except Exception as e:
            await update.message.reply_text("Qátelik júz berdi:" + str(e))
            return
        
    elif conversion_type == "pdf_to_word":
        await update.message.reply_text("Hújjet WORD formatına ózgertilip atır... Iltimas kútiń")
        await file.download_to_drive("input.pdf")
        output_file = "output.docx"
        
        # PDF to Word aylantirish (pdf2docx bilan)
        try:
            cv = Converter("input.pdf")
            cv.convert(output_file)
            cv.close()
        except Exception as e:
            await update.message.reply_text("Qátelik júz berdi: " + str(e))
            return
    
    # Tayyor faylni foydalanuvchiga yuborish
    await update.message.reply_document(document=open(output_file, "rb"))
    
    # Vaqtinchalik fayllarni o‘chirish
    os.remove("input.docx")
    os.remove("input.pdf")
    os.remove(output_file)

# Bot komandalarini sozlash
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

# Botni ishga tushirish
app.run_polling()
