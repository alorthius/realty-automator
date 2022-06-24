from os import remove
from urllib.request import urlretrieve

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select


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
        # print("Estate")
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
        self.price = parse_placeholder(self.driver, self.price_locator)
        # Mistake on the site - currency and price_for should be parsed as placeholders,
        # yet the value is selected as an op
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

    def prepare_to_tg(self):
        self.parse_base()

    def parse_address(self):
        self.town = parse_option(self.driver, self.town_locator)
        if self.town != "Львів":
            self.city = parse_option(self.driver, self.city_locator)

        self.region = parse_option(self.driver, self.region_locator)

        try:
            self.letter = parse_option(self.driver, self.letter_locator)
        except NoSuchElementException:
            pass

        try:
            self.street = parse_option(self.driver, self.street_locator)
        except NoSuchElementException:
            self.street_rural = parse_placeholder(self.driver, self.street_rural_locator)

        self.house_number = parse_placeholder(self.driver, self.house_number_locator)

    def open_edit_menu(self):
        self.driver.get(self.origin_link)
        self.driver.find_element(*self.options_button_locator).click()
        edit_link = self.driver.find_element(*self.edit_button_locator).get_attribute("href")
        self.driver.get(edit_link)

    def __repr__(self):
        if self.street:
            return f"{self.street} - {self.price} {self.currency}"
        return f"{self.street_rural} - {self.price} {self.currency}"

    def parse_base(self):
        self.open_edit_menu()
        self.parse_address()
        self.parse_price()
        self.parse_description()

    def parse_rest(self):
        # TODO: AHHAHAHAHA LOOK AT THIS SHIT
        parsers = ["self.parse_rooms_num", "self.parse_room_type", "self.parse_total_area",
                   "self.parse_sub_areas", "self.parse_curr_floor", "self.parse_ceilings_and_floors",
                   "self.parse_building_properties", "self.parse_condition", "self.parse_balcony",
                   "self.parse_plot", "self.parse_cottage", "self.parse_plot_cattegory",
                   "self.parse_usage_types", "self.parse_subtype"]

        for operation in parsers:
            try:
                eval(operation)(self.driver)
            except AttributeError:
                pass

        attrs = [self.rooms_num, self.room_type, self.area_total]
        for attr in attrs:
            try:
                print(attr)
            except AttributeError:
                pass


def parse_option(driver: WebDriver, locator_tuple: (By, str)) -> str:
    return Select(driver.find_element(*locator_tuple)).first_selected_option.text


def parse_placeholder(driver: WebDriver, locator_tuple: (By, str)) -> str:
    return driver.find_element(*locator_tuple).get_attribute("value")


def parse_checkbox(driver: WebDriver, locator_tuple: (By, str)) -> str:
    return driver.find_element(*locator_tuple).get_attribute("checked")


def select_option(driver: WebDriver, locator_tuple: (By, str), text: str):
    if text is not None:
        return Select(driver.find_element(*locator_tuple)).select_by_visible_text(text)


def fill_placeholder(driver: WebDriver, locator_tuple: (By, str), text: str):
    if text is not None:
        return driver.find_element(*locator_tuple).send_keys(text)


def tick_label(driver: WebDriver, locator_tuple: (By, str)):
    return driver.find_element(*locator_tuple).click()
