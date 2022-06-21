from queue import Queue
from json import load

from selenium import webdriver
from selenium.webdriver.common.by import By

from telethon import TelegramClient, sync
from telethon.errors.rpcerrorlist import ChannelPrivateError

from src.estate import Estate


class Automator:
    CONFIGS_PATH = "data/configuration.json"
    OBJECTS_PER_PAGE = 25

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.configs = Automator.__read_configs(self.CONFIGS_PATH)
        self.driver.implicitly_wait(10)  # seconds
        self.queue = Queue()
        self.dict = {}

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

    def __fill_queue(self):
        # The driver should be on a required page before calling this method
        # TODO: scroll and read all pages
        addresses = self.driver.find_elements(By.CLASS_NAME, "adr")
        for entry in addresses:
            self.queue.put(entry.get_attribute("href"))
            break

    def __parse_for_tg(self):
        key = 1
        while not(self.queue.empty()):
            link = self.queue.get()
            estate = Estate(link, self.driver)
            estate.prepare_to_tg()

            self.dict[key] = estate
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
        images = estate.parse_images(keys["images_qty"])

        for channel in channels:
            print(f"Відправляється у канал @{channel}...")
            # destination = client.get_entity(channel)
            try:
                client.send_file(channel, caption=message_text, file=images)
                print("Відправлено.")
            except ChannelPrivateError:
                print(f"Немає дозволу відправляти повідомлення у канал {channel}.\nНе відправлено.")

    def main_tg(self):
        self.log_in_to_site()
        self.driver.get(
            "https://www.real-estate.lviv.ua/myrealty/%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B6-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%B0%D0%BA%D1%82%D0%B8%D0%B2%D0%BD%D1%96")
        self.__fill_queue()
        self.__parse_for_tg()
        # TODO: ask users choice
        self.post_to_tg_all(self.dict.values())
