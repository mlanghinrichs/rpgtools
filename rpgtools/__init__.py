"""Container module for the rpgtools packages."""

from random import choice, randint, sample
from os import path
import json


def _load_dict(filename):
    """Load a .json file from ./src/ and return it."""
    with open(path.join(path.dirname(__file__), 'src', filename), "r") as f:
        return json.load(f)


# Preload json data to reduce resource use
CHAR_DICT = _load_dict("char.json")
ADV_DICT = _load_dict("adv.json")


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
        print(f"Failed to pull {args} with rpg._extract()! Returning ['']")
        return ['']


def _extract_choice(dct, *args):
    """Extract() a list and return a random.choice()"""
    lst = _extract(dct, *args)
    try:
        return choice(lst)
    except TypeError:
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
    """Return a generated name from char_dict using args as path to generator."""
    inp = _extract(CHAR_DICT, *args)
    # Generate from generator, pick from list
    if isinstance(inp, str):
        return _generate_name_from_list(inp.split(';'))
    elif isinstance(inp, list):
        return choice(inp)
    else:
        raise TypeError(f'{type(inp)} is neither a string nor a list!')


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c."""

    def __init__(self, **kwargs):
        v = vars()["kwargs"]
        self.setting = self._choose_setting(v)
        self.race = self._choose_race(v)
        self.gender = self._choose_gender(v)
        self.name = self._choose_name(v)
        self.surname = self._choose_surname(v)
        self.age = self._choose_age(v)
        self.personality = self._choose_personality(v)

    def __str__(self):
        out = [f"{str(key).rjust(10, ' ')}: {str(val)}"
               for (key, val) in self.__dict__.items()]
        return "\n".join(out)

    # --- Initial randomization for unspecified characteristics ---
    def _choose_setting(self, args):
        if "setting" in args:
            return args["setting"]
        else:
            return choice(list(CHAR_DICT))

    def _choose_race(self, args):
        if "race" in args:
            return args["race"]
        else:
            races = [race for race in list(CHAR_DICT[self.setting])
                     if race not in ("quirk", "strength", "flaw", "desire", "fear")]
            return choice(races)

    def _choose_gender(self, args):
        if "gender" in args:
            return args["gender"]
        else:
            return choice(("male", "female"))

    def _choose_name(self, args):
        if "name" in args:
            return args["name"]
        else:
            return _generate_name_from_json(self.setting, self.race, self.gender)

    def _choose_surname(self, args):
        if "surname" in args:
            return args["surname"]
        else:
            return _generate_name_from_json(self.setting, self.race, "surnames")

    def _choose_age(self, args):
        if "age" in args:
            return args["age"]
        else:
            return randint(*_extract(CHAR_DICT, self.setting, self.race, 'agerange'))

    def _choose_personality(self, args):
        if "personality" in args:
            return args["personality"]
        else:
            _dict = {}
            for item in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
                _dict[item] = _extract_choice(CHAR_DICT, self.setting, item)
            return _dict


class Adventure:
    """Contains randomly generated data for running a session."""

    def __init__(self, adv_type, *, num_hours=3, num_elements=5, **kwargs):
        # Temp variables to shorten code
        d = ADV_DICT
        t = adv_type

        self.locale = _extract_choice(d, t, 'locales')
        self.sub_locale = _extract_choice(d, t, 'sub_locales')
        self.plot = _extract_choice(d, t, 'plots')
        self.objective = _extract_choice(d, t, 'objectives')
        self.hours = sample(_extract(d, t, 'hours'), num_hours)
        self.quest_giver = Character.random('fantasy')

        # Make temp list so we don't have to open and close the file
        story_elements = _extract(d, t, 'story_elements')
        self.story_atoms = []
        for i in range(num_elements):
            elems = sample(story_elements, num_elements)
            self.story_atoms.append(elems)

        # If user manually entered any details, overwrite the generated ones
        # TODO FIXME this does not work!
        self.__dict__.update((k, v) for k, v in vars().items() if k in ['locale',
                                                                        'sub_locale', 'plot', 'objective', 'hours',
                                                                        'story_elements', 'num_elements'])
        self.title = "THE " + _extract_choice(d, t, 'title_elements').upper()
        self.title += " OF " + self.locale.upper()

    def __str__(self):
        out = f"\n{self.title}\nIn {self.locale}, in {self.sub_locale};\nA {self.plot}, to {self.objective}."
        out += f"\n\nGiven by:\n{self.quest_giver}\n"
        for i in range(len(self.hours)):
            out += f"\nIn hour {i + 1}, {self.hours[i]}:"
            for j in range(self.num_elements):
                out += f"\n    {j + 1}. {self.story_atoms[i][j]}"
        return out

    def write(self, direc):
        """Write details to a txt file in ./{direc}/ named after the title."""

        # craft a string with the full save-to path & filename
        path = direc + "/" + self.title.replace(" ", "") + ".txt"
        # fix dramatic title capitalization
        path = path.lower()
        # make sure the filename doesn't exist yet
        if not path.isfile(path):
            with open(path, "w") as f:
                f.write(str(self))
            print("Wrote to " + path)
