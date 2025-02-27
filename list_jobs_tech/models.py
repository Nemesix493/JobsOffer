from pathlib import Path
import json

DB_PATH = Path(__file__).resolve().parent.parent / "DB"

class Model:

    MODEL_PATH = Path()

    def __init__(self, table_name):
        self._path = self.MODEL_PATH / f"{table_name}.json"
        self.load()

    def load(self):
        try:
            with open(self._path, 'r') as file:
                self._data = json.load(file)
        except:
            self._data = {}
    
    def save(self):
        with open(self._path, 'w') as file:
            json.dump(self._data, file)
    
    @property
    def data(self):
        return self._data

class Offers(Model):
    MODEL_PATH = DB_PATH / "offers"

class Techno(Model):
    MODEL_PATH = DB_PATH / "techno"

    def reset(self):
        for key in self.data:
            self._data[key] = 0
    
    def add_technologies(self, tech_list: list[str]):
        for tech in tech_list:
            tech_lower = tech.lower()
            if tech_lower not in self.data.keys():
                self._data[tech_lower] = 0
        

class Abilities(Model):
    MODEL_PATH = DB_PATH / "abilities"

    def add_or_update(self, new_abilities: dict):
        for key, val in new_abilities.items():
            self._data[key.lower()] = val


