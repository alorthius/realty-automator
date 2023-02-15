from queue import Queue
from json import load
from pprint import pprint

import ssl
from selenium import webdriver

from telethon import TelegramClient, sync  # dont remove sync import
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChatWriteForbiddenError, SlowModeWaitError

from src.estates import *
from src.enums import Distribution, Class


class Automator:
    CONFIGS_PATH = "data/configuration.json"
    OBJECTS_PER_PAGE = 25
    USER_ITER_BEGIN = 1

    USER_DICT = {1: "продаж-квартир",
                 2: "оренда-квартир",
                 3: "продаж-будинків",
                 4: "продаж-ділянок",
                 5: "оренда-ділянок",
                 6: "продаж-комерційна",
                 7: "оренда-комерційна"}

    def __init__(self, is_visible: bool = True):
        self.configs = Automator.__read_configs(self.CONFIGS_PATH)

        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")  # disable console output of webdriver
        if not is_visible:
            options.add_argument("headless")  # do not show the window
        options.page_load_strategy = "eager"  # do not load stylesheets, images and subframes
        self.driver = webdriver.Chrome(executable_path=self.configs["chromedriver_path"], chrome_options=options)
        self.driver.set_window_position(1000, 0)

        self.driver.implicitly_wait(1)  # second
        self.driver.set_page_load_timeout(10)  # seconds

        self.estates_queue = Queue()
        self.estates_dict = {}

    def __log_in_to_site(self) -> None:
        keys = self.configs["real_estate_authorization"]
        self.driver.get("https://www.real-estate.lviv.ua/login")
        self.driver.find_element(By.ID, "username").send_keys(keys["login"])
        self.driver.find_element(By.ID, "password").send_keys(keys["password"])
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

    @staticmethod
    def __read_configs(configs_path: str) -> dict:
        with open(configs_path, encoding="UTF-8") as f:
            return load(f)

    def __fill_queue(self, choice: int):
        link = "https://www.real-estate.lviv.ua/myrealty/" + self.USER_DICT[choice] + "/статус-активні"
        distribution_type = str(Distribution.from_int(choice))
        estate_class = str(Class.from_int(choice))

        page_counter = 1
        while True:
            link_to_page = link + f"/p-{page_counter}"
            self.driver.get(link_to_page)
            addresses = self.driver.find_elements(By.CLASS_NAME, "adr")
            if not addresses:
                break
            for entry in addresses:
                estate = eval(estate_class)(entry.get_attribute("href"), self.driver, distribution_type)
                self.estates_queue.put(estate)
            page_counter += 1

    def __parse_for_tg_all(self):
        key = self.USER_ITER_BEGIN
        while not(self.estates_queue.empty()):
            estate = self.estates_queue.get()
            estate.parse_tg()
            self.estates_dict[key] = estate
            key += 1

    def __post_to_tg_all(self, estates: [Estate]):
        ssl._create_default_https_context = ssl._create_unverified_context

        keys = self.configs["telegram_keys"]
        channels = self.configs["telegram_post_configs"]["channels"]["rent"]
        client = TelegramClient(keys["session"], keys["api_id"], keys["api_hash"])

        with client:
            for estate in estates:
                print(f"\nОбробляється об'єкт < {estate} >")
                self.__post_to_tg_one(estate, channels, client)

    def __post_to_tg_one(self, estate: Estate, channels: [str], client: TelegramClient):
        keys = self.configs["telegram_post_configs"]
        message_text = estate.create_tg_message_text(keys["sender_phone_number"])
        images = estate.retrieve_images(keys["images_qty"])

        for channel in channels:
            print(f"Відправляється у канал @{channel}")
            try:
                client.send_file(channel, caption=message_text, file=images)
                print("Відправлено.")
            except (ChannelPrivateError, ChatWriteForbiddenError):
                print(f"Немає дозволу відправляти повідомлення у канал {channel}.\nНе відправлено.")
            except SlowModeWaitError:
                print(f"У канал {channel} не можна відправляти повідомлення так часто.\nНе відправлено.")

        estate.delete_images(images)

    @staticmethod
    def __ask_user_choice(upper_bound: int):
        print("Виберіть один або декілька номерів через пробіл (наприклад: 1 2 6) та нажміть Enter.\nЯкщо бажаєте вибрати усі, нажміть Enter.")
        choices = str(input("-> ")).split()
        if choices:
            return map(lambda x: int(x), choices)
        begin_idx = Automator.USER_ITER_BEGIN
        return [i for i in range(begin_idx, begin_idx + upper_bound)]

    def __republish_all(self):
        while not(self.estates_queue.empty()):
            estate = self.estates_queue.get()
            self.republish_one(estate)

    @staticmethod
    def republish_one(estate: Estate):
        estate.parse_everything()
        creation_link = f"https://www.real-estate.lviv.ua/myrealty/{estate.get_name().lower()}/{estate.distribution}/new"
        estate.dublicate_estate(creation_link)

    def main_tg(self):
        print("Об'єкти обробляються. Зачекайте.")
        self.__log_in_to_site()
        self.__fill_queue(2)  # flats rent option

        self.__parse_for_tg_all()

        pprint(self.estates_dict)
        indices = self.__ask_user_choice(len(self.estates_dict))
        self.__post_to_tg_all(map(lambda x: self.estates_dict[x], indices))

        self.driver.close()

    def main_re(self):
        print("Об'єкти обробляються. Зачекайте.")
        self.__log_in_to_site()
        pprint(self.USER_DICT)
        choices = self.__ask_user_choice(len(self.USER_DICT))

        print("Об'єкти обробляються. Зачекайте.")
        for choice in choices:
            self.__fill_queue(choice)

        self.__republish_all()
        self.driver.close()
