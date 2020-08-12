import requests
import os
import time
import telegram
import logging
from textwrap import dedent
from dotenv import load_dotenv


def main():
  telegram_notification_bot_token = os.getenv('TG_NOTIFICATION_BOT_TOKEN')
  dvmn_token = os.getenv('DVMN_TOKEN')
  notification_bot = telegram.Bot(token=telegram_notification_bot_token)
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
        payload['timestamp'] = f'{server_response["timestamp_to_request"]}'
        continue

      if server_response['status'] == 'found':
        payload['timestamp'] = f'{server_response["last_attempt_timestamp"]}'
        review = server_response['new_attempts'][0]

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

    except requests.exceptions.ConnectionError:
      print('No internet connection, retrying in 10 seconds')
      time.sleep(10)
      continue

    except requests.exceptions.ReadTimeout:
      continue

    except Exception:
      logger.exception('Бот упал с ошибкой: ')
      time.sleep(10)
      continue


if __name__ == '__main__':

  load_dotenv()
  telegram_logging_bot_token = os.getenv('TG_LOGGING_BOT_TOKEN')
  logging_bot = telegram.Bot(token=telegram_logging_bot_token)
  chat_id = os.getenv('TG_CHAT_ID')

  class MyLogsHandler(logging.Handler):
    def emit(self, record):
      log_entry = self.format(record)
      logging_bot.send_message(chat_id=chat_id, text=log_entry)

  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logger.addHandler(MyLogsHandler())
  logger.info('Бот запущен')

  main()
