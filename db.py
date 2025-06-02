import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from config import ADMIN_ID

router = Router()
db_name = "auth.db"  # НАЗВАНИЕ БД


class Form(StatesGroup):
    name = State()


def create_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        TelegramID INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Auth_links(
        Auth_link TEXT NOT NULL,
        UserID INTEGER NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users (UserID)
        )""")

    conn.commit()
    conn.close()


def is_admin(user_id: int):
    if user_id == ADMIN_ID:
        return True
    else:
        return True  # TODO: Считывание админки с БД


@router.message(Command("users"))
async def users_panel(message: Message):
    if is_admin(message.from_user.id):
        build = InlineKeyboardBuilder()
        build.button(text="Добавить пользователя", callback_data="add_user")
        build.button(text="Список пользователей", callback_data="users_list")

        build.adjust(1)
        await message.answer(
            "Панель управления пользователями:",
            reply_markup=build.as_markup()
        )


@router.callback_query(F.data == "add_user")
async def add_user_cb(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("Введите имя нового пользователя:")
    await state.set_state(Form.name)


@router.message(Form.name)
async def on_name_input(message: Message, state: FSMContext):
    user_name = message.text
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        await message.answer("Все хорошо, отвечаю")
        pass  # Тут уже нужна генерация ссылки
    except Exception as err:
        print(f"Произошла ошибка при добавлении пользователя: {err}")
        await message.answer("Произошла ошибка")
    finally:
        conn.close()
        await state.clear()


@router.callback_query(F.data == "users_list")
async def users_list_cb(cb: CallbackQuery):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT UserID, Name, TelegramID FROM Users")
    users = cursor.fetchall()

    if not users:
        text = "Пользователей нет"
    else:
        text = "<b>Список пользователей</b>\n"
        for user in users:
            user_id, name, tg_id = user
            text += f"{user_id}. {name} - {'Активен' if tg_id else 'Неактивен'}"
    await cb.message.edit_text(text, parse_mode=ParseMode.HTML)


async def main():
    create_db()
    bot_token = "6070749351:AAHYiHEoq40xZnGarhJNFxwjnEdEBeYUId4"
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
