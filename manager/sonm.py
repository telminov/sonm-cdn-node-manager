from typing import List
from .base import Task, Manager

# можно сделать лучше
REGIONS_COUNTRIES = {
    'AF': ['CG', ],         # Африка
    'AN': [''],             # Антарктика
    'AS': [],               # Азия
    'EU': ['DE', 'RU'],     # Европа
    'NA': ['US', 'CA'],     # Северная Америка
    'OC': [],               # Океания
    'SA': [],               # Южная Америка
    'DEFAULT': ['DE']
}


class SonmManager(Manager):

    def get_countries(self, region: str) -> List[str]:
        """Т.к. в sonm оперируем понятием страны, мы преобразуем регион (континент) в список подходящих стран"""
        assert region in REGIONS_COUNTRIES
        return REGIONS_COUNTRIES[region]

