from enum import Enum


class EnumExtended(Enum):
    @classmethod
    def values(cls):
        return [item.value for item in cls]

    @classmethod
    def names(cls):
        return [item.name for item in cls]

    @classmethod
    def find(cls, target):
        for item in cls:
            if item.value == target:
                return item
        return None
