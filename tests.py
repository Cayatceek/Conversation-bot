from database import db

# Добавляем запись
db.add_entry(user_id=12345, date="2025-03-03", time="12:30", text="Сегодня был отличный день!", mood="😊", is_important=True)

# Получаем записи за дату
print(db.get_entries(12345, "2025-03-03"))

# Редактируем запись
db.edit_entry(entry_id=1, new_text="Обновлённый текст!")

# Удаляем запись
db.delete_entry(1)
