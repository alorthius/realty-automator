from src.estate_base import Estate
from src.properties import *


class Flat(Estate, HasRooms, HasRoomType, HasTotalArea, HasSubAreas, HasCurrFloor, HasCeilingsAndWalls,
           HasBuildingProperties, HasCondition, HasBalcony):
    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)
        # print("Flat")


class House(Estate, HasRooms, HasRoomType, HasTotalArea, HasSubAreas, HasCeilingsAndWalls, HasBuildingProperties,
            HasCondition, HasBalcony, HasPlot, IsCottage):
    # Yet seems to be a logical mistake from the site.
    # The overall floors number uses the selector for a current floor
    floors_total_locator = (By.ID, "addobjecttype_floor")  # override HasCeilingsAndWalls variable

    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)


class Land(Estate, HasPlot, HasPlotCategory):
    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)


class Commerce(Estate, HasRooms, HasTotalArea, HasCurrFloor, HasCeilingsAndWalls, HasBuildingProperties, HasCondition,
               HasPlot, HasUsageTypes, HasSubtype):
    def __init__(self, link: str, driver: WebDriver):
        super().__init__(link, driver)
