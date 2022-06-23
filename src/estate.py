from os import remove
from urllib.request import urlretrieve

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from src.estates_properties import *


class Estate:
    COLUMN_SYMBOL = "•️"
    PHONE_SYMBOL = "📞"

    options_button_locator = (By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[1]/button[3]")
    edit_button_locator = (By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[2]/a")
    delete_button_locator = (By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[6]/a")

    town_locator = (By.ID, "addobjecttype_obl")
    region_locator = (By.ID, "addobjecttype_region")
    city_locator = (By.ID, "addobjecttype_city")
    letter_locator = (By.ID, "addobjecttype_letter")
    street_locator = (By.ID, "addobjecttype_street")
    street_rural_locator = (By.ID, "addobjecttype_street2")
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
        super().__init__()
        self.origin_link = link
        self.driver = driver

        self.town = None
        self.region = None
        self.city = None
        self.letter = None
        self.street = None
        self.street_rural = None
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
        items = textarea.find_elements(*self.desc_items_locator)
        self.driver.implicitly_wait(10)  # seconds
        self.description_items = [x.text for x in items]
        self.description_header = textarea.text

        for item in self.description_items[:-1]:
            self.description_header = self.description_header.replace(item + "\n", "")
        if self.description_items:  # last entry
            self.description_header = self.description_header.replace(self.description_items[-1], "")

        # self.description_items = "<ul>" + "".join(["<li>" + x.text + "</li>" for x in items]) + "</ul>"

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
        self.price = self.parse_placehorder_value(self.price_locator)
        self.currency = self.parse_placehorder_value(self.currency_locator)
        self.price_for = self.parse_placehorder_value(self.price_for_locator)

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
        self.town = self.parse_selected_value(self.town_locator)
        if self.town != "Львів":
            self.city = self.parse_selected_value(self.city_locator)

        self.region = self.parse_selected_value(self.region_locator)

        try:
            self.letter = self.parse_selected_value(self.letter_locator)
        except NoSuchElementException:
            pass

        try:
            self.street = self.parse_selected_value(self.street_locator)
        except NoSuchElementException:
            self.street_rural = self.parse_placehorder_value(self.street_rural_locator)

        self.house_number = self.parse_placehorder_value(self.house_number_locator)

    def open_edit_menu(self):
        self.driver.get(self.origin_link)
        self.driver.find_element(*self.options_button_locator).click()
        edit_link = self.driver.find_element(*self.edit_button_locator).get_attribute("href")
        self.driver.get(edit_link)

    def __repr__(self):
        if self.street:
            return f"{self.street} - {self.price} {self.currency}"
        return f"{self.street_rural} - {self.price} {self.currency}"

    def parse_selected_value(self, locator_tuple: (By, str)):
        return Select(self.driver.find_element(*locator_tuple)).first_selected_option.text

    def parse_placehorder_value(self, locator_tuple: (By, str)):
        return self.driver.find_element(*locator_tuple).get_attribute("value")

    def parse_everything(self):
        self.open_edit_menu()
        self.parse_address()
        self.parse_price()
        self.parse_description()


class Flat(Estate, HasRooms, HasRoomType, HasTotalArea, HasSubAreas, HasCurrFloor, HasCeilingsAndWalls, HasBuildingProperties, HasCondition, HasBalcony):
    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)


class House(Estate, HasRooms, HasRoomType, HasTotalArea, HasSubAreas, HasCeilingsAndWalls, HasBuildingProperties, HasCondition, HasBalcony, HasPlot, IsCottage):
    # Yet seems to be a logical mistake from the site.
    # The overall floors number uses the selector for a current floor
    floors_total_locator = (By.ID, "addobjecttype_floor")  # override HasCeilingsAndWalls variable

    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)


class Land(Estate, HasPlot, HasPlotCategory):
    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)


class Commerce(Estate, HasRooms, HasTotalArea, HasCurrFloor, HasCeilingsAndWalls, HasBuildingProperties, HasCondition, HasPlot, HasUsageTypes, HasSubtype):
    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)
