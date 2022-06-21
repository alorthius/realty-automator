from queue import Queue
from json import load
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By

from telethon import TelegramClient, sync
from telethon.errors.rpcerrorlist import ChannelPrivateError

from src.estate import Estate


class Automator:
    CONFIGS_PATH = "data/configuration.json"
    OBJECTS_PER_PAGE = 25
    OPTIONS_DICT = {1: "продаж-квартир",
                    2: "оренда-квартир",
                    3: "продаж-будинків",
                    4: "продаж-ділянок",
                    5: "оренда-ділянок",
                    6: "продаж-комерційна",
                    7: "оренда-комерційна"}

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.configs = Automator.__read_configs(self.CONFIGS_PATH)
        self.driver.implicitly_wait(10)  # seconds
        self.queue = Queue()
        self.estates_dict = {}

    def log_in_to_site(self) -> None:
        keys = self.configs["real_estate_authorization"]
        self.driver.get("https://www.real-estate.lviv.ua/login")
        self.driver.find_element(By.ID, "username").send_keys(keys["login"])
        self.driver.find_element(By.ID, "password").send_keys(keys["password"])
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

    @staticmethod
    def __read_configs(configs_path: str) -> dict:
        with open(configs_path, encoding="UTF-8") as f:
            return load(f)

    def __fill_queue(self, link: str):
        # TODO: scroll and read all pages
        self.driver.get(link)
        addresses = self.driver.find_elements(By.CLASS_NAME, "adr")
        for entry in addresses:
            self.queue.put(entry.get_attribute("href"))
            # break

    def __parse_for_tg_all(self):
        key = 1
        while not(self.queue.empty()):
            link = self.queue.get()
            estate = Estate(link, self.driver)
            estate.prepare_to_tg()

            self.estates_dict[key] = estate
            key += 1

    def post_to_tg_all(self, estates: [Estate]):
        keys = self.configs["telegram_keys"]
        channels = self.configs["telegram_post_configs"]["channels"]["rent"]  # TODO: pick rent / sale
        client = TelegramClient(keys["session"], keys["api_id"], keys["api_hash"])

        with client:
            for estate in estates:
                self.post_to_tg_one(estate, channels, client)

    def post_to_tg_one(self, estate: Estate, channels: [str], client: TelegramClient):
        keys = self.configs["telegram_post_configs"]
        message_text = estate.create_tg_message_text(keys["sender_phone_number"])
        images = estate.retrieve_images(keys["images_qty"])

        for channel in channels:
            print(f"Відправляється у канал @{channel}...")
            try:
                client.send_file(channel, caption=message_text, file=images)
                print("Відправлено.")
            except ChannelPrivateError:
                print(f"Немає дозволу відправляти повідомлення у канал {channel}.\nНе відправлено.")

        estate.delete_images(images)

    @staticmethod
    def ask_user_choice(options_dict):
        pprint(options_dict)
        choices = str(input("Виберіть відповідний (або декілька) номерів через пробіл (наприклад: 1 2 6):\n-> ")).split()
        return map(lambda x: options_dict[int(x)], choices)

    def main_tg(self):
        self.log_in_to_site()

        choices = self.ask_user_choice(self.OPTIONS_DICT)
        for choice in choices:
            page_link = "https://www.real-estate.lviv.ua/myrealty/" + choice + "/статус-активні"
            self.__fill_queue(page_link)
        self.__parse_for_tg_all()

        objects = self.ask_user_choice(self.estates_dict)
        self.post_to_tg_all(objects)
