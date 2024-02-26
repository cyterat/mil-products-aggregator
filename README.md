# 🛒 Military Products Aggregator

[![python](https://img.shields.io/badge/Python-3.12.0-FFD43B)](https://www.python.org/downloads/release/python-3120/)
[![pdf](https://img.shields.io/badge/PDF-stores_scraping_information-f0463c)](assets/mil-gear-stores-scraping.pdf)
[![telegram](https://img.shields.io/badge/Telegram_Bot-Find_Military_Gear_UA-229ED9)](https://web.telegram.org/k/#@find_mil_gear_ua_bot)

## 1. Script

The `scraper.py` script can be used separately from the telegram bot. It is a data scraping and aggregation script for military gear from various Ukrainian online stores. Retrieves discount price (if available) and excludes out-of-stock products.

The script can also produce a JSON list of dictionaries, if a respective flag is used, where each dictionary represents a scraped website.

### 1.1 Output

#### 1.1.1 Terminal output example

Search term: __"сумка скидання"__ (dump pouch)

<sub>_Note: not all output is visible in the screenshot_</sub><br>

![terminal-output-example](assets/mil-products-scraper-cli-interface-example.png)

#### 1.1.2 JSON file

Search term: __"сумка скидання"__ (dump pouch)

<sub>_Note: only end lines are included in the screenshot_</sub>

![json-output-example](assets/mil-products-scraper-json-example.png)

Example of the format of a single scraped website in `output.json`:

- __website__: str,
- __search_query_url__: str,
- __price_uah_min__: int,
- __price_uah_max__: int,
- __products_qty__: int,
- __social_network__: str,
- __tel_vodafone__: str,
- __tel_kyivstar__: str,
- __details__:
  - __product__: str, __price_uah__: int
  - . . .

## 2. Implemented features

### 2.1 ☑ __asynchronous scraping__

__🚀 Nearly 6x faster!__

Before:

<sub>_❗ Important: script has been renamed __~~main.py~~ → scraper.py___</sub>

![no-async-terminal-output-example](assets/time-no-async.png)

After:

<sub>_❗ Important: script has been renamed __~~main.py~~ → scraper.py___</sub>

![async-terminal-output-example](assets/time-async.png)

***

### 2.2 ☑ __logging__

Script logs are now stored in the respective '__script_name.log__' file within '__logs__' folder

***

### 2.3 ☑ __command-line interface__

    usage: scraper.py [-h] [-n NAME] [-j] [-v]

    options:
      -h, --help            show this help message and exit
      
      -n NAME, --name NAME  name of the product to scrape
                            (use underscore instead of space between words: сумка_скидання)
      
      -j, --json            write output to JSON file in 'data' folder
      
      -v, --verbose         display data after scraping

***

### 2.4 ☑ __telegram bot__

⚡ The telegram bot [@find_mil_gear_ua_bot](https://web.telegram.org/k/#@find_mil_gear_ua_bot) has been built on top of a `scraper.py` script.

***

### 2.5 ☑ __containerized telegram bot__

The docker container with the telegram bot ![containerized-bot](assets/telegram-bot/docker-telegram-bot.png)

## 3. Telegram Bot - disabled  ⛔

<img src="assets/telegram-bot/telegram-bot-qr.jpg" width="150" align="left" margin="20px">

[@find_mil_gear_ua_bot](https://web.telegram.org/k/#@find_mil_gear_ua_bot) can retrieve a sorted list of prices for the in-stock military clothing, gear, etc. from __27__ online stores.

Currently supported:
[Abrams](https://abrams.com.ua), [AlphaBravo](https://alphabravo.com.ua), [Ataka](https://attack.kiev.ua), [Avis Gear](https://avisgear.com),
[Balistyka](https://globalballistics.com.ua), [Global Ballisticks](https://globalballistics.com.ua), [Grad Gear](https://gradgear.com.ua),
[Ibis](https://ibis.net.ua), [Kamber](https://kamber.com.ua), [Killa](https://killa.com.ua), [Militarist](https://militarist.ua),
[Militarka](https://militarka.com.ua), [Molli](https://molliua.com), [Prof1Group](https://prof1group.ua), [Punisher](https://punisher.com.ua),
[Real Defence](https://real-def.com), [Specprom-kr](https://specprom-kr.com.ua), [Sts](https://sts-gear.com), [Sturm](https://sturm.com.ua),
[Stvol](https://stvol.ua), [Tactical Gear](https://tacticalgear.ua), [Tactical Systems](https://tactical-systems.com.ua), [Tur Gear](https://turgear.com.ua/),
[Ukr Armor](https://ukrarmor.com.ua), [UKRTAC](https://ukrtac.com/en/), [UTactic](https://utactic.com), [Velmet](https://velmet.ua),

The telegram bot has been_built on top of a `scraper.py` script. More information about it [here](#1-script)
<br clear="left">

### 3.1 Private chat example

<img src="assets/telegram-bot/telegram-bot-showcase.png" align="left"><br clear="left">

### 3.2 Group chat

<img src="assets/telegram-bot/telegram-bot-group-1.png" align="left"><br clear="left">

❗ _NOTE: THE BOT NEEDS ADMIN RIGHTS TO WORK IN GROUP CHATS,<br>All other permissions can be disabled as shown below_

<img src="assets/telegram-bot/telegram-bot-group-2.png" width>

## 4. Future ideas

🔥 High priority:

- Add more websites

- ~~Implement async to reduce the overall scraping time~~ ✅

- ~~Implement logging to improve maintainability~~ ✅

- ~~Develop a CLI for the script~~ ✅

<br>

🌟 Medium priority:

- ~~Create a Telegram Bot~~ ✅
  - ~~Create a docker container with a bot~~
  - Use webhooks instead of polling

<br>

✨ Low priority:

- ~~Include searched product page url in `WebsiteScraper`~~ ✅

- Include more phone number fields in `WebsiteScraper`
