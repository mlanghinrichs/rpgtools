from random import choice

def tbl(filename):
    """Return list with \\n stripped from lines in filename, making a 'table' to roll."""
    with open(filename, "r") as f:

        output = []

        for line in f.readlines():
            line = line[:-1] # Strip last char (probably newline)
            if len(line): # Check for empty line before appending
                output.append(line)

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
    if len(out) > 1:
        return out[0].upper() + out[1:].lower()
    elif len(out) == 1:
        return out[0].upper()
    else:
        return "No name..."

def ngen_f(filename):
    """n(ame)gen_f(ile) - Pass a file, return a string with generated name."""
    namelist = tbl(filename)
    if namelist[0] == "LIST":
        return choice(namelist)
    else:
        ngen_l(namelist)

print(ngen_f("tbls/names/fantasy_dwarf_male.txt"))
