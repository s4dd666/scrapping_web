import time
import requests
from bs4 import BeautifulSoup
from lxml import html
from aiogram import Bot, Dispatcher, types, executor
import asyncio


# Токен вашего бота
TOKEN = ''

# ID вашего канала
CHANNEL_ID = ''

# URL сайта для парсинга
url = ''

# Заголовки для HTTP-запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Список заголовков последних новостей
last_news_titles = []


# Функция проверки новости в канале
def check_news_in_channel(title):
    global last_news
    for news in last_news:
        if news['title'] == title:
            return True
    return False


# Функция парсинга новостей
def parse_news():
    global is_auth, last_news_titles  # добавляем определение переменных

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Парсим HTML-код страницы
    soup = BeautifulSoup(response.text, 'lxml')

    # Находим все новости
    news_items = soup.find_all('div', {'class': 'td_module_16'})

    # Создаем список для хранения новых новостей

    new_news_items = []


    # Перебираем все новости
    for item in news_items:

        # Получаем заголовок и ссылку на новость
        title = item.find('h3', {'class': 'entry-title'}).text.strip()
        link = item.find('a')['href']

        # Проверяем, была ли уже опубликована данная новость

        if title not in last_news_titles:
            new_news_items.append({'title': title, 'link': link})

    # Обновляем список заголовков последних новостей
    last_news_titles = [item['title'] for item in new_news_items]
    return new_news_items


async def send_news_to_channel(news):
    # Отправляем каждую новость в канал
    for item in news:
        count = 0
        # Получаем заголовок и ссылку на новость
        title = item['title']
        link = item['link']
        count += 1
        # Создаем текст сообщения
        message_text = f"<b>{title}</b>\n\n{link}"
        print(count)
        # Отправляем сообщение в канал
        await bot.send_message(chat_id=CHANNEL_ID, text=message_text, parse_mode=types.ParseMode.HTML)


if __name__ == '__main__':

    # Бесконечный цикл
    while True:

        # Получаем новости
        news = parse_news()

        # Отправляем новости в канал
        if news:
            asyncio.run(send_news_to_channel(news))

        # Ждем 5 минут перед следующим циклом
        time.sleep(300)
