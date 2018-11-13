from random import choice
import json, os

# Import json name, adventure data into dicts before doing anything else
ndata = {}
with open("tbls/names.json", "r") as f:
    ndata = json.load(f)

advdata = {}
with open("tbls/adv.json", "r") as f:
    advdata = json.load(f)


def tbl_json(dic, arg_tuple):
    """Takes a set of keys in a tuple and returns (list, listtype) tuple from ndata."""
    """e.g., ('foo', 'bar') as argument would return (ndata['foo']['bar'], 'list') if it
    found an array and (ndata['foo']['bar'], 'generator') if it found a string. Passed as
    tuple and not raw args to make passing the input through multiple funcs easier."""
    current = dic # working dict starts as dic
    
    try:
        for arg in arg_tuple: # for each path in the tuple,
            if isinstance(current[arg], dict): # if it finds a dict, go a level deeper
                current = current[arg]
            elif isinstance(current[arg], str): # if it finds a string, return the split list and a generator marker
                return (current[arg].split(";"), "generator")
            elif isinstance(current[arg], list): # if it finds a list, return the list and a list marker
                return (current[arg], "list")
            else: # if it finds none of these, throw an error
                raise IndexError('tbl_json called on sequence not ending in a string.')
    except KeyError:
        print(f"Tried to pull a nonexistent generator {arg_tuple} with tbl_json! Returning ''")
        return ([''], 'list')


def jchoice(dic, tup):
    return choice(tbl_json(dic,tup)[0])


def ngen_l(list_):
    """n(ame)gen_l(ist) - Return a name string generated from inputted generator list."""
    """Input format: 'x,' for choice of x or nul; 'x,y' for choice of x or y; 'x,y,'
    for a choice of x or y or nul. Pass a list in the order of generation, choices from which 
    will be concatenated."""
    
    out = ""

    for string in list_: # For each line of the generator file,
        out += choice(string.split(",")) # Append one of the options on that line to out
    
    # TODO - make this if/else to avoid sneaky bugs?
    try: # Try to capitalize out properly; if it's < 2 chars, skip this to avoid error 
        return out[0].upper() + out[1:].lower()
    except IndexError:
        return out.upper()


def ngen_j(arg_tuple):
    """Takes a set of keys in a tuple and returns a generated name from ndata."""
    inp = tbl_json(ndata, arg_tuple)

    # Proper list vs generator behavior - generate from generator, pick from list
    if inp[1] == "generator":
        return ngen_l(inp[0])
    elif inp[1] == "list":
        return choice(inp[0])
    else:
        raise TypeError('Bad/lacking tuple passes to ngen_j!')


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c."""

    # Initialize with any number of customized kwargs including skills, inventory, or stats.
    def __init__(self, *, setting="fantasy", race="human", gender="male", system="dnd",
                    chartype="npc", prof="fighter", namesource=None, skills={}, inv={}, stats={}):

        # Import each named var above as a local var for the instance
        self.__dict__.update((k, v) for k,v in vars().items() if k != 'self')

        # Generate name and surname from value provided
        # self.name = ngen_fkeys("tbls/names/", setting, race, gender)
        # self.surname = ngen_fkeys("tbls/names/", setting, race, "surnames")
        if not namesource:
            self.name = ngen_j((setting, race, gender))
            self.surname = ngen_j((setting, race, "surnames"))
        else:
            self.name = ngen_j((namesource, race, gender))
            self.surname = ngen_j((namesource, race, "surnames"))


class Adventure:
    """A class of Adventure objects, containing data/functions for a session."""

    def __init__(self, advtype, *, num_elements=3, **kwargs):
        # Temp variables to increase legibility
        d = advdata
        t = advtype
        
        # Set all adventure variables
        self.locale = jchoice(d, (t, 'locales'))
        self.sub_locale = jchoice(d, (t, 'sub_locales'))
        self.plot = jchoice(d, (t, 'plots')) 
        self.objective = jchoice(d, (t, 'objectives'))
        self.hours = [jchoice(d, (t, 'hours')) for x in range(3)]
        self.story_elements = [jchoice(d, (t, 'story_elements')) for x in range(num_elements)]

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
        path = path.lower() # fix dramatic title capitalization
        if not os.path.isfile(path): # make sure the filename doesn't exist yet
            with open(path, "w") as f:
                f.write(self.desc())
            print("Wrote to " + path)


x = Adventure("goh")
print("\n", x.desc(), "\n")


# Main input loop - asks what you want to generate, then (currently) prints name(s) and surname(s)
while True:
    print("Welcome to rpgtools charGen v0.1a. Specify any kwargs you would like to alter below.")
    print("Input 'n' or 'none' to generate character(s). Input 'q' or 'quit' to end program prematurely.")

    print("""
            Available options:
            setting
            race
            gender
            system
            char(acter)type
            prof(ession)
            """)

    # key in main scope so it can be checked in main loop if 'q'/'quit' in subloop
    key = ''
    inpDict = {} # hold key/values to change in a dict so they can be passed to Character()

    # Subloop asks for key, then value. Completes on n/none and quits program on q/quit
    while True:
        key = input("Key to alter: ")
        if key == 'q' or key == 'quit' or key == 'n' or key == 'none':
            break # Subloop break condition (on n/none or q/quit)
        else:
            value = input("Value to set: ")
            inpDict[key] = value
            print("")

    # Main loop break condition (on q/quit; continue on n/none)
    if key == 'q' or key == 'quit':
        break

    # How many characters to make?
    num = int(input("Number to generate? "))

    # Make that many and print their names, using data from inp(ut)Dict
    for i in range(num):
        temp = Character(**inpDict)
        print(temp.name + " " + temp.surname)
    
    # Currently, this isn't much of a loop - TODO make it repeatable
    break

