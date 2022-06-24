from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from src.estate_base import parse_option, parse_placeholder, parse_checkbox, \
    select_option, fill_placeholder, tick_label


class HasRooms:
    rooms_num_locator = (By.ID, "addobjecttype_komnat")

    def __init__(self):
        super().__init__()
        self.rooms_num = None
        # print("HasRooms")

    def parse_rooms_num(self, driver: WebDriver):
        self.rooms_num = parse_option(driver, self.rooms_num_locator)

    def fill_rooms_num(self, driver: WebDriver):
        select_option(driver, self.rooms_num_locator, self.rooms_num)


class HasRoomType:
    room_type_locator = (By.ID, "addobjecttype_komnata")

    def __init__(self):
        super().__init__()
        self.room_type = None

    def parse_room_type(self, driver: WebDriver):
        self.room_type = parse_checkbox(driver, self.room_type_locator)

    def fill_room_type(self, driver: WebDriver):
        if self.room_type:
            tick_label(driver, self.room_type_locator)


class HasTotalArea:
    area_total_locator = (By.ID, "addobjecttype_so")

    def __init__(self):
        super().__init__()
        self.area_total = None

    def parse_total_area(self, driver: WebDriver):
        self.area_total = parse_placeholder(driver, self.area_total_locator)

    def fill_total_area(self, driver: WebDriver):
        fill_placeholder(driver, self.area_total_locator, self.area_total)


class HasSubAreas:
    area_living_locator = (By.ID, "addobjecttype_sj")
    area_kitchen_locator = (By.ID, "addobjecttype_sk")

    def __init__(self):
        super().__init__()
        self.area_living = None
        self.area_kitchen = None

    def parse_sub_areas(self, driver: WebDriver):
        self.area_living = parse_placeholder(driver, self.area_living_locator)
        self.area_kitchen = parse_placeholder(driver, self.area_kitchen_locator)

    def fill_sub_areas(self, driver: WebDriver):
        fill_placeholder(driver, self.area_living_locator, self.area_living)
        fill_placeholder(driver, self.area_kitchen_locator, self.area_kitchen)


class HasCurrFloor:
    floor_locator = (By.ID, "addobjecttype_floor")

    def __init__(self):
        super().__init__()
        self.floor = None

    def parse_curr_floor(self, driver: WebDriver):
        self.floor = parse_option(driver, self.floor_locator)

    def fill_curr_floor(self, driver: WebDriver):
        select_option(driver, self.floor_locator, self.floor)


class HasCeilingsAndWalls:
    floors_total_locator = (By.ID, "addobjecttype_floors")
    ceilings_height_locator = (By.ID, "addobjecttype_h")
    walls_material_locator = (By.ID, "addobjecttype_wall")

    def __init__(self):
        super().__init__()
        self.floors_total = None
        self.ceilings_height = None
        self.walls_material = None

    def parse_ceilings_and_floors(self, driver: WebDriver):
        self.floors_total = parse_option(driver, self.floors_total_locator)
        self.ceilings_height = parse_placeholder(driver, self.ceilings_height_locator)
        self.walls_material = parse_option(driver, self.walls_material_locator)

    def fill_ceilings_and_floors(self, driver: WebDriver):
        select_option(driver, self.floors_total_locator, self.floors_total)
        fill_placeholder(driver, self.ceilings_height_locator, self.ceilings_height)
        select_option(driver, self.walls_material_locator, self.walls_material)


class HasBuildingProperties:
    house_category_locator = (By.ID, "addobjecttype_house_category")
    is_new_building_locator = (By.ID, "addobjecttype_new_home")
    new_building_stage_locator = (By.ID, "addobjecttype_construction_stage")

    def __init__(self):
        super().__init__()
        self.house_category = None
        self.is_new_building = None
        self.new_building_stage = None

    def parse_building_properties(self, driver: WebDriver):
        self.house_category = parse_option(driver, self.house_category_locator)
        self.is_new_building = parse_checkbox(driver, self.is_new_building_locator)
        try:
            self.new_building_stage = parse_option(driver, self.new_building_stage_locator)
        except NoSuchElementException:
            pass

    def fill_building_properties(self, driver: WebDriver):
        select_option(driver, self.house_category_locator, self.house_category)
        if self.is_new_building:
            tick_label(driver, self.is_new_building_locator)
        try:
            select_option(driver, self.new_building_stage_locator, self.new_building_stage)
        except NoSuchElementException:
            pass


class HasCondition:
    condition_locator = (By.ID, "addobjecttype_stan")

    def __init__(self):
        super().__init__()
        self.condition = None

    def parse_condition(self, driver: WebDriver):
        self.condition = parse_option(driver, self.condition_locator)

    def fill_condition(self, driver: WebDriver):
        select_option(driver, self.condition_locator, self.condition)


class HasBalcony:
    balcony_num_locator = (By.ID, "addobjecttype_balcon")

    def __init__(self):
        super().__init__()
        self.balcony_num = None

    def parse_balcony(self, driver: WebDriver):
        self.balcony_num = parse_option(driver, self.balcony_num_locator)

    def fill_balcony(self, driver: WebDriver):
        select_option(driver, self.balcony_num_locator, self.balcony_num)


class HasPlot:
    plot_area_locator = (By.ID, "addobjecttype_su")
    plot_area_unit_locator = (By.ID, "addobjecttype_s_for")

    def __init__(self):
        super().__init__()
        self.plot_area = None
        self.plot_area_unit = None

    def parse_plot(self, driver: WebDriver):
        self.plot_area = parse_placeholder(driver, self.plot_area_locator)
        self.plot_area_unit = parse_option(driver, self.plot_area_unit_locator)

    def fill_plot(self, driver: WebDriver):
        fill_placeholder(driver, self.plot_area_locator, self.plot_area)
        select_option(driver, self.plot_area_unit_locator, self.plot_area_unit)


class IsCottage:
    is_cottage_community_locator = (By.ID, "addobjecttype_community")

    def __init__(self):
        super().__init__()
        self.is_cottage_community = None

    def parse_is_cottage(self, driver: WebDriver):
        self.is_cottage_community = parse_checkbox(driver, self.is_cottage_community_locator)

    def fill_is_cottage(self, driver: WebDriver):
        if self.is_cottage_community:
            tick_label(driver, self.is_cottage_community_locator)


class HasPlotCategory:
    plot_category_locator = (By.ID, "addobjecttype_house_category")

    def __init__(self):
        super().__init__()
        self.plot_category = None

    def parse_plot_cattegory(self, driver: WebDriver):
        self.plot_category = parse_option(driver, self.plot_category_locator)

    def fill_plot_cattegory(self, driver: WebDriver):
        select_option(driver, self.plot_category_locator, self.plot_category)


class HasUsageTypes:
    # A collection of labels
    # Last digit is intentionally invalid, should be in range [1, 9]
    usage_types_locator = (By.ID, "addobjecttype_space_use_")

    def __init__(self):
        super().__init__()
        self.usage_types = []  # list of locators

    def parse_usage_types(self, driver: WebDriver):
        for idx in range(1, 10):
            locator = (self.usage_types_locator[0], self.usage_types_locator[1] + str(idx))
            if parse_checkbox(driver, locator):
                self.usage_types.append(locator)

    def fill_usage_types(self, driver: WebDriver):
        for locator in self.usage_types:
            tick_label(driver, locator)


class HasSubtype:
    subtype_locator = (By.ID, "addobjecttype_sub_type")

    def __init__(self):
        super().__init__()
        self.subtype = None

    def parse_subtype(self, driver: WebDriver):
        self.subtype = parse_option(driver, self.subtype_locator)

    def fill_subtype(self, driver: WebDriver):
        select_option(driver, self.subtype_locator, self.subtype)
