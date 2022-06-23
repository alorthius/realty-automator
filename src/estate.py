from os import remove
from urllib.request import urlretrieve

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select


class Estate:
    COLUMN_SYMBOL = "•️"
    PHONE_SYMBOL = "📞"

    options_button_locator = (By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[1]/button[3]")
    edit_button_locator = (By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[2]/a")
    delete_button_locator = (By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[6]/a")

    town_locator = (By.ID, "addobjecttype_obl")
    region_locator = (By.ID, "addobjecttype_region")
    letter_locator = (By.ID, "addobjecttype_letter")
    street_locator = (By.ID, "addobjecttype_street")
    house_number_locator = (By.ID, "addobjecttype_house")

    price_locator = (By.ID, "addobjecttype_price")
    currency_locator = (By.ID, "addobjecttype_valuta")
    price_for_locator = (By.ID, "addobjecttype_price_for")

    textarea_frame_locator = (By.XPATH, "//*[@id='addobjecttype_translations_ua']/div/iframe")
    textarea_locator = (By.XPATH, "/html/body")
    desc_header_locator = (By.TAG_NAME, "p")
    desc_items_locator = (By.TAG_NAME, "li")

    img_bar_locator = (By.CLASS_NAME, "fotorama__nav__shaft")
    img_locator = (By.CLASS_NAME, "fotorama__img")

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
        self.driver.switch_to.frame(self.driver.find_element(*self.textarea_frame_locator))
        textarea = self.driver.find_element(*self.textarea_locator)

        self.driver.implicitly_wait(1)  # seconds
        header = textarea.find_elements(*self.desc_header_locator)
        items = textarea.find_elements(*self.desc_items_locator)
        self.driver.implicitly_wait(10)  # seconds

        if not header and not items:
            self.description_header = textarea.text
        else:
            self.description_header = "\n".join(entry.text for entry in header)
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
        self.price = self.driver.find_element(*self.price_locator).get_attribute("value")
        self.currency = self.driver.find_element(*self.currency_locator).get_attribute("value")
        self.price_for = self.driver.find_element(*self.price_for_locator).get_attribute("value")

    def retrieve_images(self, images_qty: int):
        self.driver.get(self.origin_link)
        images = []
        img_bar = self.driver.find_element(*self.img_bar_locator)
        img_elements = img_bar.find_elements(*self.img_locator)[:images_qty]

        for idx, element in enumerate(img_elements):
            link = element.get_attribute("src")
            link = link.replace("/75x75/", "/800x600/", 1)  # choose image with better quality
            filename = f"data/temp_photos/img_{idx}.jpg"
            urlretrieve(link, filename)  # save image to file
            images.append(filename)
        return images

    @staticmethod
    def delete_images(images: [str]):
        for image in images:
            remove(image)

    def prepare_to_tg(self):
        self.open_edit_menu()
        self.parse_price()
        self.parse_address()
        self.parse_description()

    def parse_address(self):
        # TODO: інший населений пункт
        self.town = Select(self.driver.find_element(*self.town_locator)).first_selected_option.text
        self.region = self.driver.find_element(*self.region_locator).get_attribute("value")
        self.letter = self.driver.find_element(*self.letter_locator).get_attribute("value")
        self.street = Select(self.driver.find_element(*self.street_locator)).first_selected_option.text
        self.house_number = self.driver.find_element(*self.house_number_locator).get_attribute("value")

    def open_edit_menu(self):
        self.driver.get(self.origin_link)
        self.driver.find_element(*self.options_button_locator).click()
        edit_link = self.driver.find_element(*self.edit_button_locator).get_attribute("href")
        self.driver.get(edit_link)

    def __repr__(self):
        return f"{self.street} - {self.price} {self.currency}"
