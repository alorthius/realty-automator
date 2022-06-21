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
        self.description_items = [item.text for item in textarea.find_elements(By.TAG_NAME, "li")]
        self.driver.switch_to.default_content()

        # TODO: if li && p are none
        """
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
            message += f"\n\t{self.COLUMN_SYMBOL} {list_item}"
        message += f"\n{self.COLUMN_SYMBOL} {self.price} {self.currency}"
        message += f"\n{self.PHONE_SYMBOL} {phone_number}"
        print(message)
        return message

    def parse_full_price(self):
        self.price = self.driver.find_element(By.ID, "addobjecttype_price").get_attribute("value")
        self.currency = self.driver.find_element(By.ID, "addobjecttype_valuta").get_attribute("value")
        self.price_for = self.driver.find_element(By.ID, "addobjecttype_price_for").get_attribute("value")

    def parse_images(self, images_qty: int):
        self.driver.get(self.origin_link)
        images = []
        img_elements = self.driver.find_elements(By.CLASS_NAME, "fotorama__img")[:images_qty]
        for idx, element in enumerate(img_elements):
            link = element.get_attribute("src")
            print(link)
            filename = f"data/temp_photo_{idx}"
            urlretrieve(link, filename)
            images.append(filename)
        return images

    def prepare_to_tg(self):
        self.driver.get(self.origin_link)
        # Open edit menu
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[1]/div[1]/button[3]").click()
        edit_link = self.driver.find_element(By.XPATH, "/html/body/div[9]/div[2]/div/div[2]/ul/li[2]/a").get_attribute(
            "href")
        self.driver.get(edit_link)

        self.parse_full_price()
        self.parse_description()
