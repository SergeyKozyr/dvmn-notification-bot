import requests
import os
import time
import telegram
import logging
from textwrap import dedent
from dotenv import load_dotenv


logger = logging.getLogger()


class MyLogsHandler(logging.Handler):

  def __init__(self, logging_bot, chat_id):
    super().__init__()
    self.chat_id = chat_id
    self.logging_bot = logging_bot

  def emit(self, record):
    log_entry = self.format(record)
    self.logging_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_dvmn_review(dvmn_token):

  headers = {'Authorization': f'Token {dvmn_token}'}
  payload = {}

  while True:
    try:
      response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=payload)
      response.raise_for_status()
      server_response = response.json()

      if 'error' in server_response:
        raise requests.exceptions.HTTPError(server_response['error'])

      if server_response['status'] == 'timeout':
        payload['timestamp'] = str(server_response["timestamp_to_request"])
        continue

      if server_response['status'] == 'found':
        payload['timestamp'] = str(server_response["last_attempt_timestamp"])
        review = server_response['new_attempts'][0]

    except requests.exceptions.ConnectionError:
      print('No internet connection, retrying in 10 seconds')
      time.sleep(10)
      continue

    except requests.exceptions.ReadTimeout:
      continue

  return review


def send_notification(review, notification_bot, chat_id):

  if review['is_negative']:
    notification_bot.send_message(chat_id=chat_id, text=dedent(f'''
    У вас проверили работу «{review['lesson_title']}»

    К сожалению, в работе нашлись ошибки.

    Ссылка на задачу: https://dvmn.org{review['lesson_url']}'''))

  else:
    notification_bot.send_message(chat_id=chat_id, text=dedent(f'''
  У вас проверили работу «{review['lesson_title']}»

  Преподавателю всё понравилось, можно приступать к следующему уроку!

  Ссылка на задачу: https://dvmn.org{review['lesson_url']}'''))


def main():

  load_dotenv()
  telegram_logging_bot_token = os.getenv('TG_LOGGING_BOT_TOKEN')
  telegram_notification_bot_token = os.getenv('TG_NOTIFICATION_BOT_TOKEN')
  chat_id = os.getenv('TG_CHAT_ID')
  dvmn_token = os.getenv('DVMN_TOKEN')

  logging_bot = telegram.Bot(token=telegram_logging_bot_token)
  notification_bot = telegram.Bot(token=telegram_notification_bot_token)

  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger.setLevel(logging.INFO)
  logger.addHandler(MyLogsHandler(logging_bot, chat_id))
  logger.info('Бот запущен')

  while True:

    try:
      review = get_dvmn_review(dvmn_token)
      send_notification(review, notification_bot, chat_id)

    except Exception:
      logger.exception('Бот упал с ошибкой: ')
      time.sleep(10)


if __name__ == '__main__':
  main()
