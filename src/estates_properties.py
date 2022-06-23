from selenium.webdriver.common.by import By


class HasRooms:
    rooms_num_locator = (By.ID, "addobjecttype_komnat")

    def __init__(self):
        super().__init__()
        self.rooms_num = None


class HasRoomType:
    room_type_locator = (By.ID, "addobjecttype_komnata")

    def __init__(self):
        super().__init__()
        self.room_type = None


class HasTotalArea:
    area_total_locator = (By.ID, "addobjecttype_so")

    def __init__(self):
        super().__init__()
        self.room_type = None


class HasSubAreas:
    area_living_locator = (By.ID, "addobjecttype_sj")
    area_kitchen_locator = (By.ID, "addobjecttype_sk")

    def __init__(self):
        super().__init__()
        self.area_living = None
        self.area_kitchen = None


class HasCurrFloor:
    floor_locator = (By.ID, "addobjecttype_floor")

    def __init__(self):
        super().__init__()
        self.floor = None


class HasCeilingsAndWalls:
    floors_total_locator = (By.ID, "addobjecttype_floors")
    ceilings_height_locator = (By.ID, "addobjecttype_h")
    walls_material_locator = (By.ID, "addobjecttype_wall")

    def __init__(self):
        super().__init__()
        self.floors_total = None
        self.ceilings_height = None
        self.walls_material = None


class HasBuildingProperties:
    house_category_locator = (By.ID, "addobjecttype_house_category")
    is_new_building_locator = (By.ID, "addobjecttype_new_home")
    new_building_stage_locator = (By.ID, "addobjecttype_construction_stage")

    def __init__(self):
        super().__init__()
        self.house_category = None
        self.is_new_building = None
        self.new_building_stage = None


class HasCondition:
    condition_locator = (By.ID, "addobjecttype_stan")

    def __init__(self):
        super().__init__()
        self.condition = None


class HasBalcony:
    balcony_num_locator = (By.ID, "addobjecttype_balcon")

    def __init__(self):
        super().__init__()
        self.balcony_num = None


class HasPlot:
    plot_area_locator = (By.ID, "addobjecttype_su")
    plot_area_unit_locator = (By.ID, "addobjecttype_s_for")

    def __init__(self):
        super().__init__()
        self.plot_area = None
        self.plot_area_unit = None


class IsCottage:
    is_cottage_community_locator = (By.ID, "addobjecttype_community")

    def __init__(self):
        super().__init__()
        self.is_cottage_community = None


class HasPlotCategory:
    plot_category_locator = (By.ID, "addobjecttype_house_category")

    def __init__(self):
        super().__init__()
        self.plot_category = None


class HasUsageTypes:
    # A collection of labels
    # Last digit is intentionally invalid, should be in range [1, 9]
    usage_types_locator = (By.ID, "addobjecttype_space_use_0")

    def __init__(self):
        super().__init__()
        self.usage_types = None


class HasSubtype:
    subtype_locator = (By.ID, "addobjecttype_sub_type")

    def __init__(self):
        super().__init__()
        self.subtype = None
