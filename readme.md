# weather\_bot by dhhghkd1

## install

1. clone repo:
    git clone https://github.com/dhhghkd1/weather_bot.git

2. create venv & activate:
    python -m venv venv && source venv/bin/activate

3. install deps:
    pip install -r requirements.txt

## configuration
1. get bot token from @BotFather in telegram(or any other bot api)
2. get weather api key from openweathermap.org(or any other weather api)
3. create .env file and add your tokens:
- bot=YOUR\_telegram\_token
- api\_key=YOUR\_weather\_api\_key

## run
python weather\_bot.py

## commands
- /start: register user
- /help: show available commands
- /reset: reset your data

## features

- type the city name to get current weather

