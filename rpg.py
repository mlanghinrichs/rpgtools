from random import choice

def tbl(filename):
    """Return list with \\n stripped from lines in filename, making a 'table' to roll."""

    output = []

    try:
        with open(filename, "r") as f:

            for line in f.readlines():
                line = line[:-1] # Strip last char (probably newline)
                if len(line): # Check for empty line before appending
                    output.append(line)
    except FileNotFoundError:
        # TODO - this is not working
        output.append("Missing file!")

        return output


def c_tbl(filename):
    """Return random element from a loaded file list. Use for one-off rolls."""
    """For multiple rolls off the same table, load tbl into var and use choice to save
    system resources."""
    return choice(tbl(filename))


def ngen_l(list_):
    """n(ame)gen_l(ist) - Generate names from strings in list."""
    """Input format: 'x ' for choice of x or nul; 'x y' for choice of x or y; 'x y '
    for a choice of x or y or nul. Pass a list in the order of generation, which will be
    concatenated."""
    out = ""
    for string in list_:
        out += choice(string.split(" "))

    try:
        return out[0].upper() + out[1:].lower()
    except KeyError:
        return out.upper()

def ngen_f(filename, number=0):
    """n(ame)gen_f(ile) - Pass a file, return a string with generated name."""
    namelist = tbl(filename)
    if not number:
        if namelist[0] == "LIST":
            namelist.remove("LIST")
            return choice(namelist)
        else:
            return ngen_l(namelist)
    else:
        output = []
        if namelist[0] == "LIST":
            namelist.remove("LIST")
            for i in range(number):
                output.append(choice(namelist))
            return output
        else:
            for i in range(number):
                output.append(ngen_l(namelist))
            return output


def ngen_fkeys(path, *args):
    
    fullpath = path
    for arg in args:
        fullpath += arg
        if not args[-1] == arg:
            fullpath += "_"
    fullpath += ".txt"

    return ngen_f(fullpath)



class Character:

    def __init__(self, *, setting="fantasy", race="human", gender="male", system="dnd",
                    chartype="npc", prof="fighter", skills=[], inv=[], stats=[]):
        self.__dict__.update((k, v) for k,v in vars().items() if k != 'self')
        self.name = ngen_fkeys("tbls/names/", setting, race, gender)
        self.surname = ngen_fkeys("tbls/names/", setting, race, gender, "surnames")


# for name in ngen_f("tbls/names/fantasy_dwarf_male.txt", 40):
#     print(name)

x = Character(race="dwarf")
print(x.name)
