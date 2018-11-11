from random import choice

def tbl(filename):
    """Return list with \\n stripped from lines in filename, making a 'table' to roll."""

    output = []

    try:
        with open(filename, "r") as f:
            for line in f.readlines():
                line = line[:-1] # Strip last char (probably newline)
                if len(line): # Check to avoid adding empty lines from file
                    output.append(line) # Append the line to output list
    except FileNotFoundError:
        output.append("Missing file!")

    return output


def c_tbl(filename):
    """Return random element from a loaded file list. Use for one-off rolls."""
    """For multiple rolls off the same table, load tbl into var and use choice to save
    system resources."""
    
    return choice(tbl(filename))


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
    except KeyError:
        return out.upper()


def ngen_f(filename, number=0):
    """n(ame)gen_f(ile) - Returns a string with a generated name or a list containing # names."""
    
    # Pull file contents into list using tbl(), return "" and print warning if empty
    namelist = tbl(filename)
    if len(namelist) == 0:
        return ""
        print("ngen_f() pulled '' from empty file")
    
    if not number: # If number was left as 0, return a single choice
        # LIST-headed files are not generators, but just a list of names...
        if namelist[0] == "LIST":
            # ...so pop off that LIST and choice() accordingly
            namelist.remove("LIST")
            return choice(namelist)
        # Otherwise, ngen_l() the list made from the file
        else:
            return ngen_l(namelist)
    elif number > 0: # If num > 0, drop num of choices into the output list and return it
        output = []
        if namelist[0] == "LIST": # As above
            namelist.remove("LIST")
            for i in range(number):
                output.append(choice(namelist))
            return output
        else: # As above
            for i in range(number):
                output.append(ngen_l(namelist))
            return output


def ngen_fkeys(path, *args):
    """ngen_f(), but passed path .../ and terms from a list instead of an explicit filename."""
    """E.g., 'fantasy', 'dwarf', 'male' for fantasy_dwarf_male.txt. path MUST end in /"""
    
    fullpath = path
    
    for arg in args: # For each non-positional argument
        fullpath += arg # Append it to the file path
        if not args[-1] == arg: # And unless it's the last argument
            fullpath += "_" # Append an underscore
        else: # But if it is
            fullpath += ".txt" # Just append the extension

    # And run ngen_f() on that full path .../termx_termy_termz.txt
    return ngen_f(fullpath)


class Character:
    """A class for RPG characters. Can generate PCs or NPCs with names &c."""

    # Initialize with any number of customized kwargs including skills, inventory, or stats.
    def __init__(self, *, setting="fantasy", race="human", gender="male", system="dnd",
                    chartype="npc", prof="fighter", skills={}, inv={}, stats={}):

        # Import each named var above as a local var for the instance
        self.__dict__.update((k, v) for k,v in vars().items() if k != 'self')

        # Generate name and surname from value provided
        self.name = ngen_fkeys("tbls/names/", setting, race, gender)
        self.surname = ngen_fkeys("tbls/names/", setting, race, "surnames")


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

