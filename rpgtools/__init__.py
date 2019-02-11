"""Container module for the rpgtools packages."""

from random import choice, randint, sample
import os.path
import json


def _load_dict(filename):
    """Load a .json file from ./src/ and return it."""
    to_open = os.path.join(os.path.dirname(__file__), 'src', filename)
    with open(to_open, "r") as f:
        return json.load(f)


# Preload json data to reduce resource use
CHAR_DICT = _load_dict("char.json")
ADV_DICT = _load_dict("adv.json")
VERBOSE = False


# Simplify repeated calls for items in JSON dicts
def _extract(dict_, *args):
    """Return dict_[arg 1][arg 2]...[arg n]"""
    current = dict_
    try:
        for arg in args[:-1]:
            current = current[arg]
        return current[args[-1]]
    except KeyError:
        # Return a list with blank str so name generation uses choice() and not
        # name_gen_list()
        if VERBOSE:
            print(f"Failed to pull {args} with rpg._extract()! Returning ['']")
        return ['']


def _extract_choice(dct, *args):
    """Extract() a list and return a random.choice()"""
    lst = _extract(dct, *args)
    try:
        return choice(lst)
    except TypeError:
        if VERBOSE:
            print(f"extract_choice tried to choose from a {type(lst)}")
        return ''


def _generate_name_from_list(list_):
    """Pass a generator list and return the generated string."""
    """Input format: 'x,' for choice of x or nul; 'x,y' for choice of x or y;
    'x,y,' for a choice of x or y or nul. Pass a list in the order of
    generation, choices from which will be concatenated."""
    out = ""
    # For each line of the generator file, append an option on that line to out
    for string in list_:
        out += choice(string.split(","))
    return out.capitalize()


def _generate_name_from_json(*args):
    """Return generated name from char_dict using args as path to generator."""
    inp = _extract(CHAR_DICT, *args)
    # Generate from generator, pick from list
    if isinstance(inp, str):
        return _generate_name_from_list(inp.split(';'))
    elif isinstance(inp, list):
        return choice(inp)
    else:
        raise TypeError(f'{type(inp)} is neither a string nor a list!')


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c.

    Customizable attributes:
        * setting: fantasy, steampunk
        * race: human, elf, halforc, etc.
        * gender: male, female
        * name: (string)
        * surname: (string)
        * age: (int)
        * personality: (dict)"""

    def __init__(self, **kwargs):
        for item in ("setting",
                     "race",
                     "gender",
                     "name",
                     "surname",
                     "age",
                     "personality"):
            self.__dict__[item] = self._choose(item, kwargs)

    def __str__(self):
        out = [f"{str(key).rjust(10, ' ')}: {str(val)}"
               for (key, val) in self.__dict__.items()]
        return "\n".join(out)

    # --- Randomization for unspecified characteristics ---
    def _choose(self, item, args):
        if item in args:
            return args[item]
        else:
            if item == "setting":
                return choice(list(CHAR_DICT))
            elif item == "race":
                races = [race for race in list(CHAR_DICT[self.setting])
                         if race not in
                         ("quirk", "strength", "flaw", "desire", "fear")]
                return choice(races)
            elif item == "gender":
                return choice(("male", "female"))
            elif item == "name":
                new_args = (self.setting, self.race, self.gender)
                return _generate_name_from_json(*new_args)
            elif item == "surname":
                new_args = (self.setting, self.race, "surnames")
                return _generate_name_from_json(*new_args)
            elif item == "age":
                r = _extract(CHAR_DICT, self.setting, self.race, 'agerange')
                return randint(*r)
            elif item == "personality":
                dct = {}
                for item in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
                    dct[item] = _extract_choice(CHAR_DICT, self.setting, item)
                return dct

    def save(self, _path=""):
        """Save character to json file."""
        file_name = (self.name + self.surname).lower() + ".json"
        with open(os.path.join(_path, file_name), "w") as f:
            json.dump(self.__dict__, f, indent=4, separators=(",", ": "))
        return os.path.join(_path, file_name)

    @classmethod
    def load(cls, file_path):
        """Load character from json file."""
        with open(file_path, "r") as f:
            return cls(**json.load(f))


class Adventure:
    """Contains randomly generated data for running a session.

    Passable arguments:
        adv_type: 'goh', 'roshar' - body of ADV_DICT from which to pull data
        num_hours: int, the number of hours for which to generate elements
        num_elements: int, the number of elements to generate per hour
        locale: string, the region where the adventure takes place
        sub_locale: string, specific area in that region where it takes place
        plot: string, genre of adventure
        objective: string, grammar is imperative ("find a macguffin")
        hours: (overall description of an hour's plot * num_hours)
        story_atoms: ((element * num_elements) * num_hours)
        quest_giver: Character object
        title: string"""

    # Required stuff: adventure type, num_hours, num_elements,
    # locale, sub_locale, plot, objective, (hours), quest_giver, (story_atoms)
    def __init__(self, **kwargs):
        for item in ("adv_type",
                     "num_hours",
                     "num_elements",
                     "locale",
                     "sub_locale",
                     "plot",
                     "objective",
                     "hours",
                     "story_atoms",
                     "quest_giver",
                     "title"):
            self.__dict__[item] = self._choose(item, kwargs)

    def __str__(self):
        out = (f"\n{self.title}"
               + f"\nIn {self.locale}, in {self.sub_locale};"
               + f"\nA {self.plot}, to {self.objective}."
               + "\n\nGiven by:"
               + f"\n{self.quest_giver}\n")
        for i in range(len(self.hours)):
            out += f"\nIn hour {i + 1}, {self.hours[i]}:"
            for j in range(self.num_elements):
                out += f"\n    {j + 1}. {self.story_atoms[i][j]}"
        return out

    def _extr_adv(self, elem):
        """Extract adventure element from ADV_DICT[adv_type]."""
        return _extract_choice(ADV_DICT, self.adv_type, elem)

    def _choose(self, item, args):

        if item in args:
            return args[item]
        else:
            if item == "adv_type":
                return choice(list(ADV_DICT))
            elif item == "num_hours":
                return 3
            elif item == "num_elements":
                return 5
            elif item == "locale":
                return self._extr_adv('locales')
            elif item == "sub_locale":
                return self._extr_adv('sub_locales')
            elif item == "plot":
                return self._extr_adv('plots')
            elif item == "objective":
                return self._extr_adv('objectives')
            elif item == "hours":
                return sample(_extract(ADV_DICT, self.adv_type, 'hours'),
                              self.num_hours)
            elif item == "quest_giver":
                return Character()
            elif item == "story_atoms":
                story_elements = _extract(ADV_DICT, self.adv_type,
                                          'story_elements')
                out = []
                for i in range(self.num_hours):
                    elems = sample(story_elements, self.num_elements)
                    out.append(elems)
                return out
            elif item == "title":
                out = (
                   "THE "
                   + _extract_choice(ADV_DICT, self.adv_type, 'title_elements')
                   + " OF "
                   + self.locale
                )
                return out.upper()

    def build_quest_giver(self, **kwargs):
        self.quest_giver = Character(**kwargs)

    def markdown(self):
        qg = self.quest_giver
        qg_file = qg.name + qg.surname + ".json"
        qg_file = qg_file.lower()
        out = (f"## {self.title} ##"
               + f"\nIn {self.locale}, in {self.sub_locale};"
               + f" a {self.plot}, to {self.objective}."
               + "\n\nGiven by: "
               + f"[{qg.name} {qg.surname}](./{qg_file}), "
               + f"{qg.race} {qg.gender}.")
        for i in range(len(self.hours)):
            out += f"\n\nIn hour {i + 1}, {self.hours[i]}:\n"
            for j in range(self.num_elements):
                out += f"\n{j + 1}. {self.story_atoms[i][j]}"
        return out

    def write(self, _path="", file_format="text"):
        """Write details to a file named after the title."""
        file_name = self.title.replace(" ", "").lower()
        output = ""

        if file_format == "text":
            output = str(self)
            file_name += ".txt"
        elif file_format == "markdown":
            output = self.markdown()
            file_name += ".md"
            self.quest_giver.save(_path)

        to_save = os.path.join(_path, file_name)
        # Verify file doesn't already exist
        if not os.path.isfile(to_save):
            with open(to_save, "w") as f:
                f.write(output)
            print("Wrote to " + to_save)
        else:
            print(f"A file exists at {to_save}!")


# NOTES ON TABLE
# A faster implementation would have a dict backing and would test table place-
# ment via the following:
# Convert {1: a, (2,5): b, 6:c} to [(1, a), (2, b), (5, b), (6, c)]
# Gen random integer 0 < i <= bound
# sort list_of_tups by tup[0]
# for item in list_of_tups, if i <= item[0] { return item[1] }
#
# This would scale with number of boundary points and not number of integers
# and thus allow for arbitrarily-sized tables within the limits of int
# randomization
class Table:
    """Rolls on a table and returns a result."""

    def __init__(self, data):
        if isinstance(data, tuple) or isinstance(data, list):
            self._raw = list(data)
        elif isinstance(data, dict):
            self._raw = Table.list_from_dict(data)

        if len(self._raw) < 2:
            raise ValueError("Tables must have at least two options!"
                             + f" Options given: {len(self._raw)}")

    def __str__(self):
        out = f"TABLE: Roll 1d{self.die_size()}. "
        for (key, value) in self.to_dict().items():
            if isinstance(key, int):
                out += f"{key}: {value}, "
            else:
                out += f"{key[0]}-{key[1]}: {value}, "
        out = out[:-2]
        return out

    def __len__(self):
        return len(self._raw)

    def roll(self):
        """Return a result roll on the table."""
        return choice(self._raw)

    def to_tuple(self):
        return tuple(self._raw)

    def to_list(self):
        return self._raw

    def to_dict(self):
        raw = self._raw
        temp = {}
        for i in range(0, len(raw)):
            if raw[i] in temp:
                temp[raw[i]] += 1
            else:
                temp[raw[i]] = 1
        # {"red": 2, "heck": 1}
        index = 1
        out = {}
        for key in temp:
            if temp[key] == 1:
                out[index] = key
                index += 1
            else:
                out[(index, index + temp[key] - 1)] = key
                index += temp[key]
        return out

    def die_size(self):
        """Return what size die you would need to roll on this table."""
        poly_types = (2, 4, 6, 8, 12, 20, 100)
        for size in poly_types:
            if size >= len(self):
                return size
        return 0

    @staticmethod
    def list_from_dict(_dict):
        """Build a list from a dict with int and/or tuple-range keys.

        {1: "yadda", (2,3): "badda", 4: "boo"} ->
        ["yadda", "badda", "badda", "boo"]"""
        _list = []
        for key in _dict:
            if isinstance(key, tuple):
                # e.g. (2,5) -> range(2,6) so that 2, 3, 4, 5 are in the range
                for i in range(key[0], key[1]+1):
                    _list.append(_dict[key])
            else:
                _list.append(_dict[key])
        return _list
