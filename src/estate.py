from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver

from urllib.request import urlretrieve


class Estate:
    COLUMN_SYMBOL = "•"
    PHONE_SYMBOL  = "📞"

    def __init__(self, link: str, driver: WebDriver):
        self.origin_link = link
        self.driver = driver

        self.town = None
        self.region = None
        self.letter = None
        self.street = None
        self.house_number = None

        self.price = None
        self.currency = None
        self.price_for = None

        # self.description = ""

        self.description_header = ""
        self.description_items = []

    def parse_description(self):
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/iframe"))

        textarea = self.driver.find_element(By.XPATH, "/html/body")
        self.description_header = textarea.find_element(By.TAG_NAME, "p").text

        self.description_items = textarea.find_elements(By.TAG_NAME, "li")
        # TODO: if li && p are none
        """
        self.driver.switch_to.default_content()
        self.driver.find_element(By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/ul/li[2]/div/a[1]").click()
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/iframe"))
        textarea = self.driver.find_element(By.XPATH, "/html/body")
        # textarea.send_keys(Keys.PAGE_DOWN)
        textarea.send_keys(entry.text + "\n")
        """

    def create_tg_message_text(self, phone_number: str) -> str:
        message = self.description_header
        for list_item in self.description_items:
            message += f"\n\t{self.COLUMN_SYMBOL} {list_item.text}"
        message += f"\n{self.COLUMN_SYMBOL} {self.price} {self.currency}"
        message += f"\n{self.PHONE_SYMBOL} {phone_number}"
        print(message)
        return message

    def parse_full_price(self):
        self.price = self.driver.find_element(By.ID, "addobjecttype_price").text
        self.currency = self.driver.find_element(By.ID, "addobjecttype_valuta").text
        self.price_for = self.driver.find_element(By.ID, "addobjecttype_price_for").text

    def parse_images(self, images_qty):
        images = []
        img_elements = self.driver.find_elements(By.CLASS_NAME, "fotorama__img")
        for idx, element in enumerate(img_elements):
            link = "https://www.real-estate.lviv.ua/" + element.get_attribute("src")
            filename = f"data/temp_photo_{idx}"
            urlretrieve(link, filename)
            images.append(filename)
        return images
