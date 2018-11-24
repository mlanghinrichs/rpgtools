import random, itertools, time
from debug import time_me

faces = {
    "b": ["", "", "s", "sa", "aa", "a"],  # Boost die faces
    "s": ["", "", "f", "f", "d", "d"],  # Setback die faces
    "a": ["", "s", "s", "ss", "a", "a", "sa", "aa"],  # Ability die faces
    "d": ["", "f", "ff", "d", "d", "d", "dd", "fd"],  # Difficulty die faces
    "p": ["", "s", "s", "ss", "ss", "a", "sa", "sa", "sa", "aa", "aa", "T"],  # Proficiency die faces
    "c": ["", "f", "f", "ff", "ff", "d", "d", "fd", "fd", "dd", "dd", "D"]  # Challenge die faces
}


def std_inp(string):
    """
    Replaces alternate letter inputs with standard versions.
    """
    # Replacement values a -> b
    repls = [("y", "p"), ("g", "a"), ("r", "c"), ("u", "d")]

    # For each letter-pair tuple, replace all of a in input with b
    for tup in repls:
        string = string.replace(*tup)

    # Filter bad letters
    string = ''.join(c for c in string if c in 'pacdsb')

    # Return the fixed string
    return string


def roll(string):
    """
    Take a passed string, roll dice and return list of results.
    """

    # Clean up input to avoid bad letters
    string = std_inp(string)

    # Define list for roll results to be dumped into
    results = []

    # Append a random face for each die letter in string
    for let in string:
        if let in faces:
            results.append(random.choice(faces[let]))
        else:
            print("Passed bad face letters!")
            return

    # Join all results, as some are multiple letters, then resplit
    n = "".join(results)
    symbols = list(n)

    # For each triumph, add a success
    for n in range(symbols.count("T")):
        symbols.append("s")

    # For each despair, add a failure
    for n in range(symbols.count("D")):
        symbols.append("f")

# Utility func to remove one each of 1 or 2 values from arg list
    def cancel(*args):
        for x in args:
            symbols.remove(x)

    # Iterate results until all opp symbol pairs are cancelled
    while True:
        if "s" in symbols and "f" in symbols:
            cancel("s", "f")
        elif "a" in symbols and "d" in symbols:
            cancel("a", "d")
        else:
            break

    # Return results list
    return symbols


def describe(pool):
    """
    Given a clean pool, return a string helpfully describing the roll results.
    """

    # Initiate output string
    output = ""

    # Check for special case where everything cancels out
    if len(pool) == 0:
        return "You failed with an empty pool."

    # Check for success/failure
    if "s" in pool and pool.count("s") > 1:
        output += "You succeeded with %d successes" % pool.count("s")
    elif "s" in pool:
        output += "You succeeded with 1 success"
    elif "f" in pool and pool.count("d") > 1:
        output += "You failed with %d failures" % pool.count("f")
    elif "f" in pool:
        output += "You failed with 1 failure"
    else:
        output += "You failed with 0 successes"

    # Check for adv/disadv and complete sentence
    if "a" in pool:
        output += " and %d advantage." % pool.count("a")
    elif "d" in pool:
        output += " and %d threat." % pool.count("d")
    else:
        output += "."

    if "T" in pool and "D" in pool:
        td = (pool.count("T"), pool.count("D"))
        output += " You got {0} Triumph and {1} Despair.".format(td[0], td[1])
    elif "T" in pool:
        output += " You got %d Triumph." % pool.count("T")
    elif "D" in pool:
        output += " You got %d Despair." % pool.count("D")

    # Return finished sentence
    return output


@time_me
def sprob(string):
    """
    Given a string of dice to roll, return the probability of a successful result on that check using integers.
    """

    # Standardize the input string
    string = std_inp(string)

    # Confirm string length 0<x<9
    if not (len(string) > 0 and len(string) < 9):
        print('String is too short or too long! Length: {}'.format(len(string)))
        return

    # Empty list of possible pools given string
    p_pools = []
    temp_f = {
        "b": [0, 0, 1],  # Boost die faces
        "s": [0, 0, -1],  # Setback die faces
        "a": [0, 0, 0, 0, 1, 1, 1, 11],  # Ability die faces
        "d": [0, 0, 0, 0, 0, -1, -1, -2],  # Difficulty die faces
        "p": [0, 0, 1, 1, 1, 2],  # Proficiency die faces
        "c": [0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -2, -2]  # Challenge die faces
    }

    # For each letter in the string...
    for let in string:
        if len(p_pools) > 0:    # If there are already sample pools in the list,
            temp_list = []      # 1. Create a holding list
            for s in p_pools:   # 2. Then for each pre-existing sample pool,
                for f in temp_f[let]:    # 3. For each possible roll,
                    temp_list.append(s + f)     # 4. Add one new pool to the holding list
            p_pools = temp_list     # 4. Then set the full pool list to equal the holding list
        else:
            for f in temp_f[let]:
                p_pools.append(f)

    # Tally of successful pools
    success = 0

    # For each pool in p_pools, check if it's successful and increment success tally if it is
    for r in p_pools:
       if r > 0:
           success += 1

    # Calculate % of pools which are successful and return a rounded percentage
    prob = success/len(p_pools)
    return round(100*prob, 2)
    

# UI loop for when running file
if __name__ == "__main__":
    while True:
        inp = input("String to roll? > ").split()
        if inp[0] == "quit" or inp[0] == "q":
            break
        elif inp[0] == "prob":
            print(str(sprob(inp[1])) + "%")
        elif inp[0] == "roll":
            print(describe(roll(inp[1])))

