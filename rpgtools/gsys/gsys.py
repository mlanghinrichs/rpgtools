"""This submodule contains data for the Genesys role-playing game published by Fantasy Flight Games, LLC."""

import random

FACES = {
    "b": ["", "", "s", "sa", "aa", "a"],  # Boost die faces
    "s": ["", "", "f", "f", "d", "d"],  # Setback die faces
    "a": ["", "s", "s", "ss", "a", "a", "sa", "aa"],  # Ability die faces
    "d": ["", "f", "ff", "d", "d", "d", "dd", "fd"],  # Difficulty die faces
    "p": ["", "s", "s", "ss", "ss", "a", "sa", "sa", "sa", "aa", "aa", "T"],  # Proficiency die faces
    "c": ["", "f", "f", "ff", "ff", "d", "d", "fd", "fd", "dd", "dd", "D"]  # Challenge die faces
}


class Roll():
    """Take a passed string, roll dice and save the result to self.pool."""

    def __init__(self, string):
        self.string = Roll.standardize_input(string)
        pool = []
        for let in self.string:
            pool.append(random.choice(FACES[let]))
        self.raw_pool = pool
        # Join all results, as some are multiple letters, then resplit
        self.symbols = list("".join(pool))

        # For each triumph, add a success
        for n in range(self.symbols.count("T")):
            self.symbols.append("s")
        # For each despair, add a failure
        for n in range(self.symbols.count("D")):
            self.symbols.append("f")

        def cancel(*args):
            for x in args:
                pool.remove(x)
        while True:
            if "s" in pool and "f" in pool:
                cancel("s", "f")
            elif "a" in pool and "d" in pool:
                cancel("a", "d")
            else:
                break
        self.pool = pool

    def __str__(self):
        """Describe the pool in terms of success, failure, and special symbols."""
        output = ""
        # Check for special case where everything cancels out
        if len(self.pool) == 0:
            return "You failed with an empty pool."

        # Check for success/failure
        if self.pool.count("s") > 1:
            output += "You succeeded with %d successes" % self.pool.count("s")
        elif "s" in self.pool:
            output += "You succeeded with 1 success"
        elif self.pool.count("d") > 1:
            output += "You failed with %d failures" % self.pool.count("f")
        elif "f" in self.pool:
            output += "You failed with 1 failure"
        else:
            output += "You failed with 0 successes"

        # Check for adv/disadv and complete sentence
        if "a" in self.pool:
            output += " and %d advantage." % self.pool.count("a")
        elif "d" in self.pool:
            output += " and %d threat." % self.pool.count("d")
        else:
            output += "."

        # Check for triumph and despair
        if "T" in self.pool and "D" in self.pool:
            td = (self.pool.count("T"), self.pool.count("D"))
            output += " You got {0} Triumph and {1} Despair.".format(td[0], td[1])
        elif "T" in self.pool:
            output += " You got %d Triumph." % self.pool.count("T")
        elif "D" in self.pool:
            output += " You got %d Despair." % self.pool.count("D")

        return output

    @staticmethod
    def standardize_input(string):
        """Replace alternate letter inputs with standard versions and return the altered string."""
        replacements = [("y", "p"), ("g", "a"), ("r", "c"), ("u", "d")]
        for tup in replacements:
            string = string.replace(*tup)
        string = ''.join(char for char in string if char in 'pacdsb')
        return string

    @staticmethod
    def probability(string):
        """Given a string of dice to roll, return the % probability of a successful result on that check."""

        # Standardize the input string
        string = Roll.standardize_input(string)

        # Confirm string length 0<x<9
        if not (0 < len(string) < 9):
            print("String is too short or too long! Must be 0 < length <= 8.")
            return

        # Empty list of possible pools given string
        possible_pools = []
        temp_f = {
            "b": [0, 0, 1],  # Boost die faces
            "s": [0, 0, -1],  # Setback die faces
            "a": [0, 0, 0, 0, 1, 1, 1, 11],  # Ability die faces
            "d": [0, 0, 0, 0, 0, -1, -1, -2],  # Difficulty die faces
            "p": [0, 0, 1, 1, 1, 2],  # Proficiency die faces
            "c": [0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -2, -2]  # Challenge die faces
        }

        # For each letter in the string...
        i = 1
        for let in string:
            if len(possible_pools) > 0:    # If there are already sample pools in the list,
                temp_list = []      # 1. Create a holding list
                print("Entering new processing level: " + str(i) + f"/{len(string)-1}")
                i += 1
                for s in possible_pools:   # 2. Then for each pre-existing sample pool,
                    for f in temp_f[let]:    # 3. For each possible roll,
                        temp_list.append(s + f)     # 4. Add one new pool to the holding list
                possible_pools = temp_list     # 4. Then set the full pool list to equal the holding list
            else:
                for f in temp_f[let]:
                    possible_pools.append(f)

        # Tally of successful pools
        success = 0

        # For each pool in possible_pools, check if it's successful and increment success tally if it is
        for r in possible_pools:
           if r > 0:
               success += 1

        # Calculate % of pools which are successful and return a rounded percentage
        prob = success/len(possible_pools)
        return round(100*prob, 2)
