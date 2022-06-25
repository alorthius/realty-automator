from enum import Enum


class EnumBase(Enum):
    @classmethod
    def from_int(cls, n):
        for entry in cls:
            if n in entry.value:
                return entry


class Distribution(EnumBase):
    RENT = [2, 5, 7]
    SALE = [1, 3, 4, 6]

    def __str__(self):
        return self.name.lower()


class Class(EnumBase):
    FLAT = [1, 2]
    HOUSE = [3]
    LAND = [4, 5]
    COMMERCE = [6, 7]

    def __str__(self):
        return self.name.capitalize()
