import time

from sys import platform
from os import remove
from urllib.request import urlretrieve

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

import subprocess

if platform == 'win32':
    from src.clipboard_win import PutHtml


class Estate:
    COLUMN_SYMBOL = "•️"
    PHONE_SYMBOL = "📞"

    options_button_locator = (By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[1]/button[3]")
    edit_button_locator = (By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[2]/a")
    # delete_button_locator = (By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[6]/a")

    save_edited_locator = (By.XPATH, "//*[@id='post']/form/div[4]/div/button")

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

    # TODO: comments!
    parsers = ["address", "rooms_num", "room_type", "total_area", "sub_areas", "curr_floor",
               "ceilings_and_floors", "building_properties", "condition", "balcony",
               "plot", "is_cottage", "plot_category", "usage_types", "subtype", "price", "description"]

    def __init__(self, link: str, driver: WebDriver, distribution: str):
        super().__init__()
        self.origin_link = link
        self.driver = driver
        self.distribution = distribution

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

    def parse_description(self, driver: WebDriver):
        self.driver.switch_to.frame(self.driver.find_element(*self.textarea_frame_locator))
        textarea = self.driver.find_element(*self.textarea_locator)

        items = textarea.find_elements(*self.desc_items_locator)
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

    def parse_price(self, driver: WebDriver):
        self.price = parse_placeholder(self.driver, self.price_locator)
        self.currency = parse_option(self.driver, self.currency_locator)
        self.price_for = parse_option(self.driver, self.price_for_locator)

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

    def parse_address(self, driver: WebDriver):
        self.town = parse_option(self.driver, self.town_locator)
        if self.town != "Львів":
            self.city = parse_option(self.driver, self.city_locator)

        self.region = parse_option(self.driver, self.region_locator)
        self.letter = parse_option(self.driver, self.letter_locator)

        self.street = parse_option(self.driver, self.street_locator)
        if not self.street:
            self.street_rural = parse_placeholder(self.driver, self.street_rural_locator)

        self.house_number = parse_placeholder(self.driver, self.house_number_locator)

    def open_edit_menu(self):
        self.driver.get(self.origin_link)
        self.driver.find_element(*self.options_button_locator).click()
        edit_link = self.driver.find_element(*self.edit_button_locator).get_attribute("href")
        self.driver.get(edit_link)

    def __repr__(self):
        address = self.street
        if not address:
            address = self.street_rural
        return f"{address} - {self.price} {self.currency} - {self.distribution} - {self.get_name()}"

    @classmethod
    def get_name(cls):
        return cls.__name__

    def parse_tg(self):
        self.open_edit_menu()
        self.parse_address(self.driver)
        self.parse_price(self.driver)
        self.parse_description(self.driver)

    def parse_everything(self):
        self.open_edit_menu()
        time.sleep(0.5)
        for operation in self.parsers:
            try:
                eval(f"self.parse_{operation}(self.driver)")
            except AttributeError:
                pass

    def fill_address(self, driver: WebDriver):
        select_option(self.driver, self.town_locator, self.town)
        select_option(self.driver, self.region_locator, self.region)
        select_option(self.driver, self.city_locator, self.city)

        # city parameter can toggle the visibility of a letter one
        # neither WebDriverWait with EC or implicitly_wait helped
        if self.city: time.sleep(0.5)
        select_option(self.driver, self.letter_locator, self.letter)

        select_option(self.driver, self.street_locator, self.street)
        fill_placeholder(self.driver, self.street_rural_locator, self.street_rural)
        fill_placeholder(self.driver, self.house_number_locator, self.house_number)

    def fill_price(self, driver: WebDriver):
        fill_placeholder(self.driver, self.price_locator, self.price)
        select_option(self.driver, self.currency_locator, self.currency)
        select_option(self.driver, self.price_for_locator, self.price_for)

    def fill_description(self, driver: WebDriver):
        items = self.description_header + "\n"
        items += "<ul>" + "".join(["<li>" + x + "</li>" for x in self.description_items]) + "</ul>"
        if platform == 'win32':
            PutHtml(items)
        else:
            cmd = ["xclip", "-sel", "clip", "-t", "text/html", "-f"]  # commands to copy as html
            subprocess.check_output(cmd, input=items, text=True)  # copy

        self.driver.switch_to.frame(self.driver.find_element(*self.textarea_frame_locator))
        textarea = self.driver.find_element(*self.textarea_locator)
        # textarea.click()
        textarea.send_keys(Keys.LEFT_CONTROL + "v")
        self.driver.switch_to.default_content()

    def fill_everything(self):
        for operation in self.parsers:
            try:
                eval(f"self.fill_{operation}(self.driver)")
            except AttributeError:
                pass

    def finish_publishing(self):
        # time.sleep(5)
        button = self.driver.find_element(*self.save_edited_locator)
        # scroll
        action = ActionChains(self.driver)
        action.move_to_element(button).click().perform()

        # To publish as an active object:
        # self.driver.find_element(By.XPATH, "/html/body/div/div[2]/a").click()
        # self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/a[2]/span").click()
        # tick_label(self.driver, (By.ID, "promote_object_free_ad"))
        # self.driver.find_element(By.XPATH, "/html/body/div[1]/form/div[6]/button").click()

    def dublicate_estate(self, creation_link: str):
        self.driver.get(creation_link)
        self.fill_everything()
        self.finish_publishing()


def parse_option(driver: WebDriver, locator_tuple: (By, str)) -> str:
    return Select(driver.find_element(*locator_tuple)).first_selected_option.text


def parse_placeholder(driver: WebDriver, locator_tuple: (By, str)) -> str:
    return driver.find_element(*locator_tuple).get_attribute("value")


def parse_checkbox(driver: WebDriver, locator_tuple: (By, str)) -> str:
    return driver.find_element(*locator_tuple).get_attribute("checked")


def select_option(driver: WebDriver, locator_tuple: (By, str), text: str):
    if text:
        return Select(driver.find_element(*locator_tuple)).select_by_visible_text(text)


def fill_placeholder(driver: WebDriver, locator_tuple: (By, str), text: str):
    if text:
        return driver.find_element(*locator_tuple).send_keys(text)


def tick_label(driver: WebDriver, locator_tuple: (By, str)):
    return driver.find_element(*locator_tuple).click()
