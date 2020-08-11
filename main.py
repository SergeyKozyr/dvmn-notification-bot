import requests
import os
import time
import telegram
from textwrap import dedent
from dotenv import load_dotenv


def main():
  load_dotenv()
  telegram_token = os.getenv('TG_TOKEN')
  dvmn_token = os.getenv('DVMN_TOKEN')
  chat_id = os.getenv('TG_CHAT_ID')
  bot = telegram.Bot(token=telegram_token)
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
          bot.send_message(chat_id=chat_id, text=dedent(f'''
            У вас проверили работу «{review['lesson_title']}»

            К сожалению, в работе нашлись ошибки.

            Ссылка на задачу: https://dvmn.org{review['lesson_url']}'''))

        else:
          bot.send_message(chat_id=chat_id, text=dedent(f'''
          У вас проверили работу «{review['lesson_title']}»

          Преподавателю всё понравилось, можно приступать к следующему уроку!

          Ссылка на задачу: https://dvmn.org{review['lesson_url']}'''))

    except requests.exceptions.ConnectionError:
      print('No internet connection, retrying in 10 seconds')
      time.sleep(10)
      continue

    except requests.exceptions.ReadTimeout:
      continue


if __name__ == '__main__':
  main()
