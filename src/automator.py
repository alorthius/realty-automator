from queue import Queue
from json import load
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By

from telethon import TelegramClient, sync
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChatWriteForbiddenError, SlowModeWaitError

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

    def __init__(self, is_visible: bool = True):
        self.configs = Automator.__read_configs(self.CONFIGS_PATH)

        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")  # disable console output of webdriver
        if not is_visible:
            options.add_argument("headless")  # do not show the window
        self.driver = webdriver.Chrome(executable_path=self.configs["chromedriver_path"], chrome_options=options)

        self.driver.implicitly_wait(10)  # seconds
        self.estates_queue = Queue()
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
        self.driver.implicitly_wait(1)

        page_counter = 1
        while True:
            link_to_page = link + f"/p-{page_counter}"
            self.driver.get(link_to_page)
            addresses = self.driver.find_elements(By.CLASS_NAME, "adr")
            if not addresses:
                break
            for entry in addresses:
                self.estates_queue.put(entry.get_attribute("href"))
            page_counter += 1

        self.driver.implicitly_wait(10)

    def __parse_for_tg_all(self):
        key = 1
        while not(self.estates_queue.empty()):
            link = self.estates_queue.get()
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
                print(f"\nОбробляється об'єкт < {estate} >")
                self.post_to_tg_one(estate, channels, client)

    def post_to_tg_one(self, estate: Estate, channels: [str], client: TelegramClient):
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
    def ask_user_choice(options_dict):
        pprint(options_dict)
        print("Виберіть один або декілька номерів через пробіл (наприклад: 1 2 6) та нажміть Enter.\nЯкщо бажаєте вибрати усі, нажміть Enter.")
        choices = str(input("-> ")).split()
        if not choices:
            return options_dict.values()
        return map(lambda x: options_dict[int(x)], choices)

    def main_tg(self):
        self.prepare_to_main()

        self.__parse_for_tg_all()
        objects = self.ask_user_choice(self.estates_dict)
        self.post_to_tg_all(objects)

        self.driver.close()

    def main_re(self):
        self.prepare_to_main()

        self.republish_all()

        self.driver.close()

    def republish_all(self):
        while not(self.estates_queue.empty()):
            link = self.estates_queue.get()
            estate = Estate(link, self.driver)
            self.republish_one(estate)
            break
            # TODO: self.delete_one(estate)

    def republish_one(self, estate: Estate):
        estate.parse_everything()


    def prepare_to_main(self):
        print("Об'єкти обробляються. Зачекайте.")
        self.log_in_to_site()
        choices = self.ask_user_choice(self.OPTIONS_DICT)
        print("Об'єкти обробляються. Зачекайте.")

        for choice in choices:
            page_link = "https://www.real-estate.lviv.ua/myrealty/" + choice + "/статус-активні"
            self.__fill_queue(page_link)
