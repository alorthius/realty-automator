from os import remove
from urllib.request import urlretrieve

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select


class Estate:
    COLUMN_SYMBOL = "•️"
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

        self.description_header = ""
        self.description_items = []

    def parse_description(self):
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/iframe"))
        textarea = self.driver.find_element(By.XPATH, "/html/body")

        self.driver.implicitly_wait(1)  # seconds
        header = textarea.find_elements(By.TAG_NAME, "p")
        items = textarea.find_elements(By.TAG_NAME, "li")
        self.driver.implicitly_wait(10)  # seconds

        if not header and not items:
            self.description_header = textarea.text
        else:
            self.description_header = header[0].text
            self.description_items = [x.text for x in items]

        self.driver.switch_to.default_content()
        # self.driver.find_element(By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/ul/li[2]/div/a[1]").click()
        # self.driver.switch_to.frame(
        #     self.driver.find_element(By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/iframe"))
        # textarea = self.driver.find_element(By.XPATH, "/html/body")
        # # textarea.send_keys(Keys.PAGE_DOWN)
        # textarea.send_keys(entry.text + "\n")

    def create_tg_message_text(self, phone_number: str) -> str:
        message = self.description_header
        for list_item in self.description_items:
            message += f"\n    {self.COLUMN_SYMBOL} {list_item}"
        message += f"\n{self.COLUMN_SYMBOL} {self.price} {self.currency}"
        message += f"\n{self.PHONE_SYMBOL} {phone_number}"
        return message

    def parse_price(self):
        self.price = self.driver.find_element(By.ID, "addobjecttype_price").get_attribute("value")
        self.currency = self.driver.find_element(By.ID, "addobjecttype_valuta").get_attribute("value")
        self.price_for = self.driver.find_element(By.ID, "addobjecttype_price_for").get_attribute("value")

    def retrieve_images(self, images_qty: int):
        self.driver.get(self.origin_link)
        images = []
        img_bar = self.driver.find_element(By.CLASS_NAME, "fotorama__nav__shaft")
        img_elements = img_bar.find_elements(By.CLASS_NAME, "fotorama__img")[:images_qty]

        for idx, element in enumerate(img_elements):
            link = element.get_attribute("src")
            link = link.replace("/75x75/", "/800x600/", 1)  # get better quality
            filename = f"data/temp_photos/img_{idx}.jpg"
            urlretrieve(link, filename)
            images.append(filename)
        return images

    @staticmethod
    def delete_images(images: [str]):
        for image in images:
            remove(image)

    def prepare_to_tg(self):
        self.driver.get(self.origin_link)
        # Open edit menu
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[1]/button[3]").click()
        edit_link = self.driver.find_element(By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[2]/a").get_attribute(
            "href")
        self.driver.get(edit_link)

        self.parse_price()
        self.parse_address()
        self.parse_description()
    #     parse address

    def parse_address(self):
        # TODO: override for будинок
        self.town = Select(self.driver.find_element(By.ID, "addobjecttype_obl")).first_selected_option.text
        self.region = self.driver.find_element(By.ID, "addobjecttype_region").get_attribute("value")
        self.letter = self.driver.find_element(By.ID, "addobjecttype_letter").get_attribute("value")
        self.street = Select(self.driver.find_element(By.ID, "addobjecttype_street")).first_selected_option.text
        self.house_number = self.driver.find_element(By.ID, "addobjecttype_house").get_attribute("value")

    def __repr__(self):
        return f"{self.street} - {self.price} {self.currency}"
