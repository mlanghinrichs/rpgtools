from random import choice, randint, sample
import json
import os
import dnd
import gsys

# Preload json data to reduce system strain
def load_dict(filename):
    with open("./src/" + filename, "r") as f:
        return json.load(f)
char_dict = load_dict("char.json")
adv_dict = load_dict("adv.json")

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
        return ([''])


def extract_choice(dct, *args):
    """Extract() a list and return a random.choice()"""
    lst = extract(dct, *args)
    try:
        return choice(lst)
    except TypeError:
        print(f"extract_choice tried to choose from a {type(lst)}")
        return ''


def name_gen_list(list_):
    """Return a name string generated from inputted generator list."""
    """Input format: 'x,' for choice of x or nul; 'x,y' for choice of x or y;
    'x,y,' for a choice of x or y or nul. Pass a list in the order of
    generation, choices from which will be concatenated."""
    
    out = ""
    # For each line of the generator file, append an option on that line to out
    for string in list_:
        out += choice(string.split(","))
    # TODO - make this if/else to avoid sneaky bugs?
    # Try to capitalize properly; if < 2 chars, skip this to avoid error 
    try: 
        return out.capitalize() 
    except IndexError:
        return out.upper()


def name_gen_json(*args):
    """Return a generated name from char_dict using args as path to generator."""
    inp = extract(char_dict, *args)

    # Proper list vs generator behavior - generate from generator, pick from list
    if isinstance(inp, str):
        return name_gen_list(inp.split(';'))
    elif isinstance(inp, list):
        return choice(inp)
    else:
        raise TypeError(f'{type(inp)} is neither a string nor a list!')


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c."""

    def __init__(self, setting="fantasy", race="human", gender="female", *,
                    chartype="npc", prof="fighter", inv={}, rand=False):
        self.__dict__.update((k, v) for k,v in vars().items() if k != 'self')
        self.name = name_gen_json(setting, race, gender)
        self.surname = name_gen_json(setting, race, 'surnames')
        # TODO add exception handling
        self.age = randint(*extract(char_dict, setting, race, 'agerange'))
        for f in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
            self.__dict__[f] = extract_choice(char_dict, setting, f)

    def __str__(self):
        out = [f"{str(k).rjust(10, ' ')}: {str(v)}" for (k,v) in self.__dict__.items()]
        return "\n".join(out)

    @classmethod
    def random(cls, setting="fantasy"):
        """Build a character with random attributes from the setting."""
        # Check setting dict for sub-dicts with an "agerange" key to filter out quirks etc.
        races = filter(lambda x: 'agerange' in char_dict[setting][x],
                       iter(char_dict[setting]))
        race = choice(list(races))
        gender = choice(('male', 'female'))
        return cls(setting, race, gender, rand=True)


class DNDChar(Character):
    """Class for D&D 5e characters."""

    def __init__(self, *args, proficiencies=(), level=1, **kwargs): 
        self._rawGen = dnd.CharGen()
        self.stats = self._rawGen.stats
        self.mods = self._rawGen.mods
        self.level = level
        # 5e proficiency mod scales with this formula (2 @ 1-4, 3 @ 5-8, etc)
        self.prof_mod = (level - 1)//4 + 2
        self.skills = self._rawGen.skills
        self.proficiencies = proficiencies

        # If this is a randomly generated character, get random proficiencies
        if 'rand' in kwargs and kwargs['rand'] == True:
            self.proficiencies = sample(list(dnd.skill_list), 5)
        for p in self.proficiencies:
            self.skills[p] += self.prof_mod
        # proficiencies and level not used by Character so don't bother passing
        super().__init__(*args, **kwargs)

    def __str__(self):
        # Hidden functions to shorten code below
        def pad(num, amount=3):
            return str(num).rjust(amount, " ")
        def padmod(num, amount=3):
            """Pad & format modifier"""
            if num < 0:
                return pad(num, amount)
            else:
                return pad("+" + str(num), amount)

        with open("src/dnd_ascii_charsheet.txt", "r") as f:
            ascii_sheet = f.read()
        pretty_print_skill_mods = []
        for s in dnd.skill_list:
            mod = padmod(self.skills[s], 3)
            # Mark proficient skills but make prof and non-prof the same length
            # to fit charsheet
            if s in self.proficiencies:
                mod += "*"
            else:
                mod += " "
            pretty_print_skill_mods.append(mod)
        out = ascii_sheet.format(
            self.name.ljust(18, " "),
            self.surname.ljust(18, " "),
            self.prof.ljust(18, " "),
            *[pad(self.stats[s], 3) for s in ('str', 'dex', 'con',
                                              'int', 'wis', 'cha')],
            *[padmod(self.mods[s], 3) for s in ('str', 'dex', 'con',
                                                'int', 'wis', 'cha')],
            padmod(self.prof_mod, 4),
            padmod(self.mods['dex'], 4),
            *pretty_print_skill_mods
            )
        return out


class Adventure:
    """Contains randomly generated data for running a session."""

    def __init__(self, adv_type, *, num_hours=3, num_elements=5, **kwargs):
        # Temp variables to shorten code
        d = adv_dict
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
        self.__dict__.update((k, v) for k,v in vars().items() if k in ['locale',
            'sub_locale', 'plot', 'objective', 'hours', 'story_elements', 'num_elements'])
        self.title = "THE " + extract_choice(d, t, 'title_elements').upper()
        self.title += " OF " + self.locale.upper()
        
    
    def __str__(self):
        out = f"\n{self.title}\nIn {self.locale}, in {self.sub_locale};\nA {self.plot}, to {self.objective}."
        out += f"\n\nGiven by:\n{self.quest_giver}\n"
        for i in range(len(self.hours)):
            out += f"\nIn hour {i+1}, {self.hours[i]}:"
            for j in range(self.num_elements):
                out += f"\n    {j+1}. {self.story_atoms[i][j]}"
        return out

    def write(self, direc):
        """Write details to a txt file in ./{direc}/ named after the title."""

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

    print("Welcome to rpgtools v0.2.",
          "Enter a command or type 'help' for more options.")

    while True:
        inp = input(" > ").split()
        try:
            if inp[0] == 'help':
                print("- char(acter) [setting] [race] [gender] | random : describe a character")
                print("- adv(enture) [source] : describe an adventure")
                print("- q(uit): quit program")

            elif inp[0] in ("char", "character"):
                if inp[1] == "random":
                    char = Character.random()
                else:
                    char = Character(*inp[1:])
                print(char)

            elif inp[0] == "dndchar":
                if inp[1] == "random":
                    char = DNDChar.random()
                else:
                    char = DNDChar(*inp[1:])
                print(char)

            # dnd by default, then try gsys, allow to break if gsys fails
            elif inp[0] == "roll":
                try:
                    print(dnd.Roll.string(inp[1]))
                except:
                    print(gsys.Roll(inp[1]))

            elif inp[0] in ("adv", "adventure"):
                new = Adventure(inp[1])
                print(new)

            elif inp[0] in ("q", "quit", ":q"):
                break

            else:
                print(f" x {inp[0]} is not a supported command.")

        except FileNotFoundError:
            print(f"'{' '.join(inp)}' requires a command or more arguments.")
        except IndexError:
            print("Something went wrong. Try that again?")

if __name__ == "__main__":
    mainLoop()

