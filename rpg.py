from random import choice, randint, sample
import json, os

# Import json name, adventure data into dicts before doing anything else
def load_dict(filename):
    with open("tbls/" + filename, "r") as f:
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

    for string in list_: ## For each line of the generator file,
        out += choice(string.split(",")) ## Append one of the options on that line to out
    
    # TODO - make this if/else to avoid sneaky bugs?
    try: ## Try to capitalize out properly; if it's < 2 chars, skip this to avoid error 
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
    def __init__(self, setting="fantasy", race="human", gender="male", *, system="dnd",
                    chartype="npc", prof="fighter", skills={}, inv={}, stats={}):

        # Import each named var above as a local var for the instance
        self.__dict__.update((k, v) for k,v in vars().items() if k != 'self')

        # Generate name and surname from value provided
        ## self.name = ngen_fkeys("tbls/names/", setting, race, gender)
        ## self.surname = ngen_fkeys("tbls/names/", setting, race, "surnames")
        self.name = ngen_j(setting, race, gender)
        self.surname = ngen_j(setting, race, 'surnames')

        # Get agerange list (should be two items) from char_dict
        self.age = randint(*extract(char_dict, setting, race, 'agerange'))

        # Get features
        for feature in ('quirk', 'strength', 'flaw', 'desire', 'fear'):
            self.__dict__[feature] = extract_choice(char_dict, setting, feature)

    def desc(self):
        rstr = "Name: " + self.name + " " + self.surname
        rstr += "\nAge: " + str(self.age)
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


class Adventure:
    """A class of Adventure objects, containing data/functions for a session."""

    def __init__(self, adv_type, *, num_hours=3, num_elements=3, **kwargs):
        # Temp variables to increase legibility
        d = adv_dict
        t = adv_type
        
        # Set all adventure variables
        self.locale = extract_choice(d, t, 'locales')
        self.sub_locale = extract_choice(d, t, 'sub_locales')
        self.plot = extract_choice(d, t, 'plots') 
        self.objective = extract_choice(d, t, 'objectives')
        self.hours = sample(extract(d, t, 'hours'), num_hours)
        self.story_elements = sample(extract(d, t, 'story_elements'), num_elements)

        # If user manually entered any details, overwrite the generated ones
        self.__dict__.update((k, v) for k,v in vars().items() if k in ['locale',
            'sub_locale', 'plot', 'objective', 'hours', 'story_elements', 'num_elements'])

        # Finally, set a title for the adventure
        self.title = "THE " + self.story_elements[0].upper() + " OF " + self.locale.upper()
        
    
    def desc(self):
        """Return a formatted str containing the adventure details written out."""

        out = f"""{self.title}
In {self.locale}, in {self.sub_locale};
A {self.plot}, to {self.objective}.

In hour 1, {self.hours[0]}.
In hour 2, {self.hours[1]}.
In hour 3, {self.hours[2]}.
   
Random elements:"""

        # Generalizable to any # of elements
        for n in range(len(self.story_elements)):
            out += "\n{}. {}".format(n+1, self.story_elements[n])

        # Return the description string
        return out

    def write(self, direc):
        """Write adventure details to a txt file in ./direc/ named after the title."""
        
        # Str containing path to save file to
        path = direc + "/" + self.title.replace(" ", "") + ".txt"
        path = path.lower() ## fix dramatic title capitalization
        if not os.path.isfile(path): ## make sure the filename doesn't exist yet
            with open(path, "w") as f:
                f.write(self.desc())
            print("Wrote to " + path)


def mainLoop():
    """Primary input loop for when you run the program."""

    print("Welcome to rpgtools v0.2.\nEnter a command or type 'help' for more options.")
    while True:
        inp = input(" > ").split()

        if inp[0] == 'help':
            print("- char(acter): opens character generator")
            print("- adv(enture): opens adventure generator")
            print("- q(uit): quits program")
        elif inp[0] == "char" or inp[0] == "character":
            char = Character(*inp[1:]) ## Pass args after 'char'/'character' to Character
            print(char.desc())
            # if charLoop():
            #     break
        elif inp[0] == "adv" or inp[0] == "adventure":
            advtype = input("What kind of adventure? > ")
            new = Adventure(advtype)
            print(new.desc())
        elif inp[0] == "q" or inp[0] == "quit":
            break


# def charLoop():
# 
#     print(" - Input 'n' or 'none' to generate character(s). Input 'q' or 'quit' to end program prematurely.\n -")
#     print(" - Available options:\n - setting\n - race\n - gender\n - system\n - char(acter)type\n - prof(ession)\n - namesource\n -")
# 
#     # key in main scope so it can be checked in main loop if 'q'/'quit' in subloop
#     key = ''
#     inpDict = {} # hold key/values to change in a dict so they can be passed to Character()
# 
#     # Subloop asks for key, then value. Completes on n/none and quits program on q/quit
#     while True:
#         key = input(" - Key to alter: ")
#         if key == 'q' or key == 'quit' or key == 'n' or key == 'none':
#             break # Subloop break condition (on n/none or q/quit)
#         else:
#             value = input(" - Value to set: ")
#             inpDict[key] = value
#             print(" - ")
# 
#     # Main loop break condition (on q/quit; continue on n/none)
#     if key == 'q' or key == 'quit':
#         return True
# 
#     # How many characters to make?
#     num = int(input(" - Number to generate? "))
# 
#     # Make that many and print their names, using data from inp(ut)Dict
#     for i in range(num):
#         temp = Character(**inpDict)
#         print(" -> \n" + temp.desc())


mainLoop()


# Main input loop - asks what you want to generate, then (currently) prints name(s) and surname(s)
# while True:
#     print("Welcome to rpgtools charGen v0.1a. Specify any kwargs you would like to alter below.")
#     print("Input 'n' or 'none' to generate character(s). Input 'q' or 'quit' to end program prematurely.")
# 
#     print("""
#             Available options:
#             setting
#             race
#             gender
#             system
#             char(acter)type
#             prof(ession)
#             """)
# 
#     # key in main scope so it can be checked in main loop if 'q'/'quit' in subloop
#     key = ''
#     inpDict = {} # hold key/values to change in a dict so they can be passed to Character()
# 
#     # Subloop asks for key, then value. Completes on n/none and quits program on q/quit
#     while True:
#         key = input("Key to alter: ")
#         if key == 'q' or key == 'quit' or key == 'n' or key == 'none':
#             break # Subloop break condition (on n/none or q/quit)
#         else:
#             value = input("Value to set: ")
#             inpDict[key] = value
#             print("")
# 
#     # Main loop break condition (on q/quit; continue on n/none)
#     if key == 'q' or key == 'quit':
#         break
# 
#     # How many characters to make?
#     num = int(input("Number to generate? "))
# 
#     # Make that many and print their names, using data from inp(ut)Dict
#     for i in range(num):
#         temp = Character(**inpDict)
#         print(temp.name + " " + temp.surname)
#     
#     # Currently, this isn't much of a loop - TODO make it repeatable
#     break
# 
