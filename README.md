# 🛒 Military Products Aggregator
[![Python - 3.12.0](https://img.shields.io/badge/Python-3.12.0-f4d159)](https://www.python.org/downloads/release/python-3120/)
[![excel](https://img.shields.io/badge/excel-buy_mil_equipment-1D6F42)](data/buy_mil_equipment.xlsx)

***

Currently supported online stores:
[Ataka](https://attack.kiev.ua), [Abrams](https://abrams.com.ua), [Hofner](https://hofner.com.ua), [Ibis](https://ibis.net.ua),
[Kamber](https://kamber.com.ua), [Killa](https://killa.com.ua), [Maroder](https://maroder.com.ua), [Militarist](https://militarist.ua), 
[Militarka](https://militarka.com.ua), [Molli](https://molliua.com), [Prof1Group](https://prof1group.ua), [Punisher](https://punisher.com.ua)


***

### Script output

_Note: the `main.py` script produces a JSON list of dictionaries where each dictionary represents a scraped website._

Example of a single scraped website in `output.json`:
- __website__: str,
- __price_uah_min__: int,
- __price_uah_max__: int,
- __products_qty__: int,
- __social_network__: str,
- __tel_vodafone__: str,
- __tel_kyivstar__: str,
- __details__:
  - __product__: str, __price_uah__: int
  - __product__: str, __price_uah__: int
  - . . .

***

### Future ideas
- Add more websites
- Include websites and products urls in `output.json`
- Include more phone number fields in `output.json`
- Implement async to reduce the overall scraping time
