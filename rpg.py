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

# print(c_tbl("README"))
