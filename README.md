# 🛒 Military Products Aggregator

[![python](https://img.shields.io/badge/Python-3.12.0-FFD43B)](https://www.python.org/downloads/release/python-3120/)
[![pdf](https://img.shields.io/badge/PDF-stores_scraping_information-f0463c)](assets/mil-gear-stores-scraping.pdf)
[![telegram](https://img.shields.io/badge/Telegram_Bot-Find_Military_Gear_UA-229ED9)](https://web.telegram.org/k/#@find_mil_gear_ua_bot)

## Telegram Bot

<img src="assets/telegram-bot/telegram-bot-qr.jpg" width="150" align="left" margin="20px">

The telegram bot has been_built on top of a `scraper.py` script from my other project.

[@find_mil_gear_ua_bot](https://web.telegram.org/k/#@find_mil_gear_ua_bot) can retrieve a sorted list of prices for the in-stock military clothing, gear, etc. from __26__ online stores.

Currently supported:
[Abrams](https://abrams.com.ua), [AlphaBravo](https://alphabravo.com.ua), [Ataka](https://attack.kiev.ua), [Avis Gear](https://avisgear.com),
[Balistyka](https://globalballistics.com.ua), [Global Ballisticks](https://globalballistics.com.ua), [Grad Gear](https://gradgear.com.ua),
[Ibis](https://ibis.net.ua), [Kamber](https://kamber.com.ua), [Killa](https://killa.com.ua), [Militarist](https://militarist.ua),
[Militarka](https://militarka.com.ua), [Molli](https://molliua.com), [Punisher](https://punisher.com.ua),
[Real Defence](https://real-def.com), [Specprom-kr](https://specprom-kr.com.ua), [Sts](https://sts-gear.com), [Sturm](https://sturm.com.ua),
[Stvol](https://stvol.ua), [Tactical Gear](https://tacticalgear.ua), [Tactical Systems](https://tactical-systems.com.ua), [Tur Gear](https://turgear.com.ua/),
[Ukr Armor](https://ukrarmor.com.ua), [UKRTAC](https://ukrtac.com/en/), [UTactic](https://utactic.com), [Velmet](https://velmet.ua),
<br clear="left">

### Private chat example

<img src="assets/telegram-bot/telegram-bot-showcase.png" align="left"><br clear="left">

### Group chat

<img src="assets/telegram-bot/telegram-bot-group-1.png" align="left"><br clear="left">

❗ _NOTE: THE BOT NEEDS ADMIN RIGHTS TO WORK IN GROUP CHATS,<br>All other permissions can be disabled as shown below_

<img src="assets/telegram-bot/telegram-bot-group-2.png" width>

### ☑ __containerized telegram bot__

  The docker container with the telegram bot ![containerized-bot](assets/telegram-bot/docker-telegram-bot.png)

## 🔥 Reminders

- Add more websites

- ~~Implement async to reduce the overall scraping time~~ ✅

- ~~Develop a CLI for the scraping script~~ ✅

- ~~Include searched product page url in `WebsiteScraper`~~ ✅

- ~~Create a docker container with a bot~~ ✅

- Deploy telegram bot on cloud platform
