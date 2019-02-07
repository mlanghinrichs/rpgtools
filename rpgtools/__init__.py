from random import choice, randint, sample
from os import path
import json


def load_dict(filename):
    with open(path.join(path.dirname(__file__), 'src', filename), "r") as f:
        return json.load(f)


# Preload json data to reduce resource use
CHAR_DICT = load_dict("char.json")
ADV_DICT = load_dict("adv.json")


# Simplify repeated calls for items in JSON dicts
def extract(dict_, *args):
    """Return dict_[arg 1][arg 2]...[arg n]"""
    current = dict_
    try:
        for arg in args[:-1]:
            current = current[arg]
        return current[args[-1]]
    except KeyError:
        # Return a list with blank str so name generation uses choice() and not
        # name_gen_list()
        print(f"Failed to pull {args} with rpg.extract()! Returning ['']")
        return ['']


def extract_choice(dct, *args):
    """Extract() a list and return a random.choice()"""
    lst = extract(dct, *args)
    try:
        return choice(lst)
    except TypeError:
        print(f"extract_choice tried to choose from a {type(lst)}")
        return ''


def generate_name_from_list(list_):
    """Return a name string generated from inputted generator list."""
    """Input format: 'x,' for choice of x or nul; 'x,y' for choice of x or y;
    'x,y,' for a choice of x or y or nul. Pass a list in the order of
    generation, choices from which will be concatenated."""

    out = ""
    # For each line of the generator file, append an option on that line to out
    for string in list_:
        out += choice(string.split(","))
    return out.capitalize()


def generate_name_from_json(*args):
    """Return a generated name from char_dict using args as path to generator."""
    inp = extract(CHAR_DICT, *args)

    # Proper list vs generator behavior - generate from generator, pick from list
    if isinstance(inp, str):
        return generate_name_from_list(inp.split(';'))
    elif isinstance(inp, list):
        return choice(inp)
    else:
        raise TypeError(f'{type(inp)} is neither a string nor a list!')


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c."""

    def __init__(self, *, setting, race, gender):
        self.__dict__.update((k, v) for k, v in vars().items() if k != 'self')
        self.name = generate_name_from_json(setting, race, gender)
        self.surname = generate_name_from_json(setting, race, 'surnames')
        # TODO add exception handling
        self.age = randint(*extract(CHAR_DICT, setting, race, 'agerange'))
        for f in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
            self.__dict__[f] = extract_choice(CHAR_DICT, setting, f)

    def __str__(self):
        out = [f"{str(k).rjust(10, ' ')}: {str(v)}" for (k, v) in self.__dict__.items()]
        return "\n".join(out)

    @classmethod
    def random(cls, setting):
        """Build a character with random attributes from the setting."""
        # Check setting dict for sub-dicts with an "agerange" key to filter out quirks etc.
        races = filter(lambda x: 'agerange' in CHAR_DICT[setting][x],
                       iter(CHAR_DICT[setting]))
        race = choice(list(races))
        gender = choice(('male', 'female'))
        return cls(setting, race, gender, rand=True)


class Adventure:
    """Contains randomly generated data for running a session."""

    def __init__(self, adv_type, *, num_hours=3, num_elements=5, **kwargs):
        # Temp variables to shorten code
        d = ADV_DICT
        t = adv_type

        self.locale = extract_choice(d, t, 'locales')
        self.sub_locale = extract_choice(d, t, 'sub_locales')
        self.plot = extract_choice(d, t, 'plots')
        self.objective = extract_choice(d, t, 'objectives')
        self.hours = sample(extract(d, t, 'hours'), num_hours)
        self.quest_giver = Character.random('fantasy')

        # Make temp list so we don't have to open and close the file
        story_elements = extract(d, t, 'story_elements')
        self.story_atoms = []
        for i in range(num_elements):
            elems = sample(story_elements, num_elements)
            self.story_atoms.append(elems)

        # If user manually entered any details, overwrite the generated ones
        # TODO FIXME this does not work!
        self.__dict__.update((k, v) for k, v in vars().items() if k in ['locale',
                                                                        'sub_locale', 'plot', 'objective', 'hours',
                                                                        'story_elements', 'num_elements'])
        self.title = "THE " + extract_choice(d, t, 'title_elements').upper()
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