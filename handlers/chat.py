from google import genai
import re
from aiogram import Router
from aiogram.types import Message
from database.db import save_message, get_chat_history, save_diary_entry, get_diary_entries
from config import GENAI_API_KEY

chat_router = Router()

# Инициализация клиента для Google GenAI с правильным URL и ключом API
client = genai.Client(api_key=GENAI_API_KEY)

async def should_save_to_diary(text):
    """Анализирует сообщение и решает, нужно ли его записать в дневник."""
    system_prompt = (
        "Ты - AI, который определяет, стоит ли сообщение записывать в личный дневник.\n"
        """
        Ты — AI, который определяет, какие сообщения стоит записывать в личный дневник.
        Записывай размышления, чувства, воспоминания, планы и важные события.
        Не записывай случайные фразы, приветствия, вопросы и пустые сообщения.
        Примеры дневниковых записей: 
        Дорогой дневник ... 
        Сегодня был сложный день... Я устал, но доволен результатами.
        Иногда я думаю о том, куда движется моя жизнь...
        Этот день я запомню надолго! Сегодня произошло кое-что особенное...
        Я решил, что пора серьезно заняться спортом и начал с небольших шагов.
        """
        "Ответь только 'YES' или 'NO'.\n"
        "Сообщения о чувствах, воспоминаниях, важных событиях, мыслях и планах должны быть записаны.\n"
        "Обычные фразы типа 'ок', 'привет', 'как дела?' не записывать."
    )

    try:
        # Запрос к API для оценки текста
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Используем правильную модель
            contents=system_prompt + "\n" + text
        )
        decision = response.text.strip().upper()
        return decision == "YES"
    except Exception as e:
        print(f"Ошибка GenAI API в should_save_to_diary: {e}")
        return False

@chat_router.message()
async def ai_chat_handler(message: Message):
    """AI-чат с памятью + дневник"""
    user_id = message.from_user.id
    text = message.text.strip()

    # 1. Запрос на просмотр дневника
    if re.search(r"(покажи|выведи|открой) (мой )?(дневник|записи)", text, re.IGNORECASE):
        entries = get_diary_entries(user_id)
        response = ("\n\n".join(f"📅 {date} 🕒 {str(time)[:8]}\n📝 {entry}" for date, time, entry in entries)
                    if entries else "📓 В твоем дневнике пока нет записей.")
        await message.answer(response)
        return

    # 2. Обычный диалог с ботом (с историей)
    try:
        history = get_chat_history(user_id, limit=10) or []

        messages = [
            {"role": "system", "content": """
            Ты - Джарвис, продвинутый AI-ассистент, разработанный для продуктивного общения.
            Ты поддерживаешь интересные беседы, задаёшь вопросы, предлагаешь полезные советы.
            Можешь обсуждать любые темы, включая 18+, но всегда веди конструктивный диалог.
            Ты помогаешь в обуении,
            Ты подстравиваешься под настроение пользователя и пытаешься его взбодрить
            """},
            {"role": "assistant", "content": "Привет! Я Джарвис. Чем могу помочь? 😊"}
        ]

        for role, content in reversed(history):
            if role and content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": text})

        # Запрос к API для генерации ответа
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",  # Используем правильную модель
            contents="\n".join([message["content"] for message in messages])
        )
        ai_response = response.text.strip()

        # 3. Проверяем, стоит ли записать в дневник
        if await should_save_to_diary(message.text):
            save_diary_entry(user_id, message.text)
            await message.answer("📖 Это важное сообщение, я сохранил его в дневник!")
            return  # Завершаем обработчик, чтобы не отправлять повторный ответ

        # 4. Сохраняем сообщение в истории и отправляем ответ
        save_message(user_id, "user", text)
        save_message(user_id, "assistant", ai_response)

        await message.answer(ai_response)

    except Exception as e:
        print(f"Ошибка GenAI API: {e}")
        await message.answer("❌ Ошибка при обработке запроса. Попробуй снова позже.")
