## Description

This is a python script that uses 2 telegram bots. The first one sends you a message, after your code at [dvmn.org](https://dvmn.org) has been reviewed. The second one sends you programm logs.

## How to install

1) **Installing on a local machine**

- Create .env file with the next variables

        DVMN_TOKEN="Your dvmn token"
        TG_NOTIFICATION_BOT_TOKEN="First bot telegram token"
        TG_LOGGING_BOT_TOKEN="Second bot telegram token"
        TG_CHAT_ID="Your telegram chat id"

    - Get your dvmn token [here](https://dvmn.org/api/docs)

    - Telegram bot tokens are available after creation in @BotFather chat

    - For your chat id send, a message to @userinfobot 


- Install dependancies

        pip install -r requirements.txt

- Run the script

        python main.py


2) **Deploying with Heroku**

- Clone the repository, sign up or log in at [Heroku](https://www.heroku.com/)

- Create a new Heroku app, click on Deploy tab and connect your Github

- Type in the repository name and click Deploy Branch at the bottom of the page

- Set up environment variables at the Settings tab in Config Vars

- Turn on the 'bot' process on Resources tab


## Project Goals
The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org)