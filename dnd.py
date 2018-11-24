from random import choice, randint, sample
import math

class Roll():

    def __init__(self, num=1, die=20, mod=0, *args, **kwargs):
        # Save num, die, and mod to object's dict
        self.__dict__.update((k, v) for k,v in vars().items() if k in ("num", "die", "mod"))
        out = 0
        for i in range(num):
            out += randint(1, die)
        self.result = out + mod
        if "result" in kwargs.keys():
            self.result = kwargs['result']

    def __str__(self):
        return str(self.result)

    def __lt__(self, other):
        return self.result < other.result

    def __gt__(self, other):
        return self.result > other.result

    def __int__(self):
        return int(self.result)

    def __add__(self, other):
        return self.result + other

    def __sub__(self, other):
        return self.result - other

    def __radd__(self, other):
        return other + self.result

    def __rsub__(self, other):
        return other - self.result


    @classmethod
    def string(cls, string):
        mod = 0
        # Check if + or - is in the string and log its location
        ind = max(string.find('+'), string.find('-'))
        # If it is in the string,
        if ind != -1:
            # set mod to everything after its position in the string
            mod = int(string[ind:])
            # and set the string to the preceding
            string = string[:ind]
        num, die = int(string.split('d')[0]), int(string.split('d')[1])
        return cls(num, die, mod)

    @classmethod
    def advantage(cls, num=1, die=20, mod=0):
        """Return the highest of two rolls."""
        a, b = cls(num, die, mod), cls(num, die, mod)
        return max(a, b)

    @classmethod
    def disadvantage(cls, num=1, die=20, mod=0):
        """Return the lowest of two rolls."""
        a, b = cls(num, die, mod), cls(num, die, mod)
        return min(a, b)

    @classmethod
    def dropleast(cls, num=4, die=6, mod=0):
        """Return a multi-die Roll with the lowest result among the dice dropped."""
        # Make a list of individual die rolls
        results = [randint(1, die) for roll in range(num)]
        results.remove(min(results))
        result = sum(results) + mod
        # Return an object with a pre-set result
        return cls(num=num, die=die, mod=mod, result=result)


class Poly():

    def __init__(self, args):
        pass

class Char():

    def __init__(self, stats = {}):
        self.stats = stats
        if len(stats) == 0:
            for stat in ("str", "dex", "con", "int", "wis", "cha"):
                self.stats[stat] = int(Roll.dropleast())
        self.mods = {}
        for stat in self.stats.keys():
            self.mods[stat] =(self.stats[stat]-10)//2
if __name__ == "__main__":    
    x = Char()
    print(x.stats, x.mods)

