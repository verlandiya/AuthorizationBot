
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import config

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет!")
    print(message.from_user.id)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())