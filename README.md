# Realty-automator

A python web-scraper and automator for re-publishing free advertisements for a [Real-estate site](https://www.real-estate.lviv.ua/en/) and promoting them in the [Telegram](https://telegram.org/) chats.

***

### Functionality:
* Republish all active advertisements in one or more particular sections (sale/rent, flat/house/land/commerce)
  * Run: `python main.py re`

* Send the chosen advertisements from the site to the list of telegram channels
  * Run: `python main.py tg`

***

### Prerequisites:
* Have active profiles on [Real-estate site](https://www.real-estate.lviv.ua/en/) and [Telegram](https://telegram.org/) messenger

* Get [Telegram API](https://core.telegram.org/api/obtaining_api_id) (id and hash required)

* Parsing and automation were implemented using [Selenium](https://github.com/SeleniumHQ/selenium) API, for interaction with Telegram's API was used [Telethon](https://github.com/LonamiWebs/Telethon) library 

* Install them and all the rest python dependencies using `pip`:
  * `pip install -r requirements.txt`

* For **Linux** systems, also download [xclip package](https://github.com/astrand/xclip) using your package manager  

* Download [Chrome browser](https://www.google.com/intl/en/chrome/) and the corresponding to it version of the [ChromeDriver](https://sites.google.com/chromium.org/driver/downloads?authuser=0)

* Fill all the parameters in the [config file](data/configuration.json)

