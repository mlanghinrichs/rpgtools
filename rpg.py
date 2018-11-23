from random import choice, randint, sample
import json, os

# Import json name, adventure data into dicts before doing anything else
def load_dict(filename):
    with open("./tbls/" + filename, "r") as f:
        return json.load(f)

char_dict = load_dict("char.json")
adv_dict = load_dict("adv.json")

def extract(dict_, *args):
    """Return dict_[arg1][arg2]... if the value is a string or list."""

    current = dict_ ## working dict starts as dict_
    
    try:
        for arg in args[:-1]:
            current = current[arg]
        return current[args[-1]]
    except KeyError:
        # Return a list with blank str so name generation uses choice() and not ngen_l()
        print(f"Tried to pull a nonexistent generator {args} with extract! Returning ['']")
        return ([''])


def extract_choice(dct, *args):
    lst = extract(dct, *args)
    try:
        return choice(lst)
    except TypeError:
        print(f"extract_choice tried to choose from a {type(lst)}")
        return ''


def ngen_l(list_):
    """n(ame)gen_l(ist) - Return a name string generated from inputted generator list."""
    """Input format: 'x,' for choice of x or nul; 'x,y' for choice of x or y; 'x,y,'
    for a choice of x or y or nul. Pass a list in the order of generation, choices from which 
    will be concatenated."""
    
    out = ""

    # For each line of the generator file, append one of the options on that line to out
    for string in list_:
        out += choice(string.split(","))
    
    # TODO - make this if/else to avoid sneaky bugs?
    # Try to capitalize out properly; if it's < 2 chars, skip this to avoid error 
    try: 
        return out[0].upper() + out[1:].lower()
    except IndexError:
        return out.upper()


def ngen_j(*args):
    """Return a generated name from char_dict using the args as a path to the generator."""
    inp = extract(char_dict, *args)

    # Proper list vs generator behavior - generate from generator, pick from list
    if isinstance(inp, str):
        return ngen_l(inp.split(';'))
    elif isinstance(inp, list):
        return choice(inp)
    else:
        raise TypeError(f'{type(inp)} is neither a string nor a list!')


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c."""

    # Initialize with any number of customized kwargs including skills, inventory, or stats.
    def __init__(self, setting="fantasy", race="human", gender="female", *, system="dnd",
                    chartype="npc", prof="fighter", skills={}, inv={}, stats={}):

        # Import each named var above as a local var for the instance
        self.__dict__.update((k, v) for k,v in vars().items() if k != 'self')

        # Generate name and surname from value provided
        self.name = ngen_j(setting, race, gender)
        self.surname = ngen_j(setting, race, 'surnames')

        # Get agerange list (should be two items) from char_dict - TODO add exception handling
        self.age = randint(*extract(char_dict, setting, race, 'agerange'))

        # Get features
        for feature in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
            self.__dict__[feature] = extract_choice(char_dict, setting, feature)

    def __str__(self):
        rstr = "Name: " + self.name + " " + self.surname
        rstr += "\nAge/Gender: " + str(self.age) + "/" + self.gender
        rstr += "\nRace: " + self.race
        for feature in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
            title = feature[0].upper() + feature[1:]
            rstr += f"\n{title}: {self.__dict__[feature]}"
        out = []
        for line in rstr.split("\n"):
            h1 = line.split()[0]
            h2 = " ".join(line.split()[1:])
            h1 += (12 - len(h1)) * "-"
            out.append(h1 + h2)
        return "\n".join(out)

    @classmethod
    def random(cls, setting="fantasy"):
        # TODO clean & comment races filter
        races = filter(lambda x: 'agerange' in char_dict[setting][x],
                            list(char_dict[setting].keys()))
        race = choice(list(races))
        gender = choice(('male', 'female'))
        return Character(setting, race, gender)


class Adventure:
    """Adventure objects, containing randomly generated data for running a session."""

    def __init__(self, adv_type, *, num_hours=3, num_elements=5, **kwargs):
        # Temp variables to increase legibility
        d = adv_dict
        t = adv_type
        
        # Set all adventure variables
        self.locale = extract_choice(d, t, 'locales')
        self.sub_locale = extract_choice(d, t, 'sub_locales')
        self.plot = extract_choice(d, t, 'plots') 
        self.objective = extract_choice(d, t, 'objectives')
        self.hours = sample(extract(d, t, 'hours'), num_hours)
        self.quest_giver = Character.random('fantasy')
        
        # Make temp story_elements list so we don't have to open and close it for each # in num_elements
        story_elements = extract(d, t, 'story_elements') 
        # A list of lists to contain x hours worth of atoms
        self.story_atoms = []
        for i in range(num_elements):
            # Pick 5 story elements and add them in a list to story_atoms
            elems = sample(story_elements, num_elements)
            self.story_atoms.append(elems)

        # If user manually entered any details, overwrite the generated ones
        self.__dict__.update((k, v) for k,v in vars().items() if k in ['locale',
            'sub_locale', 'plot', 'objective', 'hours', 'story_elements', 'num_elements'])

        # Finally, set a title for the adventure
        self.title = "THE " + extract_choice(d, t, 'title_elements').upper() + " OF " + self.locale.upper()
        
    
    def __str__(self):
        out = f"\n{self.title}\nIn {self.locale}, in {self.sub_locale};\nA {self.plot}, to {self.objective}."
        out += f"\n\nGiven by:\n{self.quest_giver}\n"
        # Nested "In hour x, [stuff]: y random elements"
        for i in range(len(self.hours)):
            out += f"\nIn hour {i+1}, {self.hours[i]}:"
            for j in range(self.num_elements):
                out += f"\n    {j+1}. {self.story_atoms[i][j]}"
        return out

    def write(self, direc):
        """Write adventure details to a txt file in ./direc/ named after the title."""
        
        # craft a string with the full save-to path & filename
        path = direc + "/" + self.title.replace(" ", "") + ".txt"
        # fix dramatic title capitalization
        path = path.lower() 
        # make sure the filename doesn't exist yet
        if not os.path.isfile(path): 
            with open(path, "w") as f:
                f.write(str(self))
            print("Wrote to " + path)


def mainLoop():
    """Primary input loop for running rpg.py as a program."""

    print("Welcome to rpgtools v0.2.\nEnter a command or type 'help' for more options.")
    while True:
        inp = input(" > ").split()
        try:
            if inp[0] == 'help':
                print("- char(acter) [setting] [race] [gender] | random : describe a character")
                print("- adv(enture) [source] : describe an adventure")
                print("- q(uit): quit program")
            elif inp[0] == "char" or inp[0] == "character":
                if inp[1] == "random":
                    char = Character.random('fantasy')
                else:
                    char = Character(*inp[1:]) ## Pass args after 'char'/'character' to Character
                print(char)
            elif inp[0] == "adv" or inp[0] == "adventure":
                new = Adventure(inp[1])
                print(new)
            elif inp[0] == "q" or inp[0] == "quit":
                break
            else:
                print(f" x {inp[0]} is not a supported command.")
        except IndexError:
            print(f"'{' '.join(inp)}' requires a command or more arguments.")


mainLoop()

