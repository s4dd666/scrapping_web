import time
import requests
from bs4 import BeautifulSoup
from lxml import html
from aiogram import Bot, Dispatcher, types, executor
import asyncio


# Токен вашего бота
TOKEN = 'YOUR_TOKEN_BOT'

# ID вашего канала
CHANNEL_ID = 'TELEGRAM_CHANEL_ID'

# Логин и пароль для авторизации
USERNAME = 'YOUR_LOGIN'
PASSWORD = 'YOUR_PASS'

# URL сайта для парсинга
url = 'https://www.tesmanian.com/'

# Заголовки для HTTP-запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Сессия для сохранения cookies и авторизации
session = requests.Session()

# Флаг авторизации
is_auth = False

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Список заголовков последних новостей
last_news_titles = []
last_news = []


# Функция авторизации
def login():
    global is_auth
    login_url = url + 'user/login'

    # Отправляем GET-запрос на страницу авторизации, чтобы получить cookies
    response = session.get(login_url, headers=headers)

    # Парсим HTML-код страницы авторизации
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим скрытое поле csrf_token, которое необходимо отправить при авторизации
    csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')

    # Формируем данные для отправки POST-запроса на авторизацию
    data = {
        'csrf_token': csrf_token,
        'email': USERNAME,
        'password': PASSWORD,
        'remember': 'on',
        'submit': ''
    }

    # Отправляем POST-запрос на авторизацию
    response = session.post(login_url, headers=headers, data=data)

    # Проверяем успешность авторизации
    if response.status_code == 200:
        is_auth = True
    else:
        is_auth = False


# Функция проверки новости в канале
def check_news_in_channel(title):
    global last_news
    for news in last_news:
        if news['title'] == title:
            return True
    return False


def parse_news():
    global is_auth, last_news_titles, last_news

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise SystemExit(e)

    # Парсим HTML-код страницы
    soup = BeautifulSoup(response.text, 'lxml')

    # Находим все новости
    news_items = soup.find_all('div', {'class': 'td_module_16'})

    # Создаем список для хранения новых новостей
    new_news_items = []

    # Проверяем, авторизованы ли мы
    if not is_auth:
        login()

    # Перебираем все новости
    for item in news_items:

        # Получаем заголовок и ссылку на новость
        title = item.find('h3', {'class': 'entry-title'}).text.strip()
        link = item.find('a')['href']

        # Проверяем, была ли уже опубликована данная новость
        if title not in last_news_titles:
            new_news_items.append({'title': title, 'link': link})

    # Добавляем новости в начало списка last_news
    if new_news_items:
        last_news = new_news_items + last_news

    # Обновляем список заголовков последних новостей
    last_news_titles = [item['title'] for item in last_news]

    return new_news_items



async def send_news_to_channel(news):
    # Отправляем каждую новость в канал
    for item in news:

        # Получаем заголовок и ссылку на новость
        title = item['title']
        link = item['link']

        # Создаем текст сообщения
        message_text = f"<b>{title}</b>\n\n{link}"
        
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

        # Ждем 15 сек перед следующим циклом
        time.sleep(15)
