from random import randint, sample
import rpgtools

SKILLS = {"Acrobatics": "dex",
          "Animal Handling": "wis",
          "Arcana": "int",
          "Athletics": "str",
          "Deception": "cha",
          "History": "int",
          "Insight": "wis",
          "Intimidation": "cha",
          "Investigation": "int",
          "Medicine": "wis",
          "Nature": "int",
          "Perception": "wis",
          "Performance": "cha",
          "Persuasion": "cha",
          "Religion": "int",
          "Sleight of Hand": "dex",
          "Stealth": "dex",
          "Survival": "wis"
          }

STATS = ("str", "dex", "con", "int", "wis", "cha")
STATS_FULL_NAMES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


class Roll:

    def __init__(self, num=1, die=20, mod=0, *, dropleast=False, **kwargs):
        # Save num, die, and mod to object's dict
        self.__dict__.update((k, v) for k, v in vars().items() if k in ("num", "die", "mod"))
        self.rolls = []
        for i in range(num):
            self.rolls.append(randint(1, die))
        if dropleast:
            self.rolls.remove(min(self.rolls))
        self.result = sum(self.rolls) + mod
        if "result" in kwargs.keys():
            self.result = kwargs['result']

    def __str__(self):
        return str(self.result)

    def __lt__(self, other):
        if isinstance(other, Roll):
            return self.result < other.result
        elif isinstance(other, int):
            return self.result < other
        else:
            raise TypeError(f"Can't compare {type(other)} with a Roll!")

    def __gt__(self, other):
        if isinstance(other, Roll):
            return self.result > other.result
        elif isinstance(other, int):
            return self.result > other
        else:
            raise TypeError(f"Can't compare {type(other)} with a Roll!")

    def __int__(self):
        return int(self.result)

    def __add__(self, other):
        if isinstance(other, Roll):
            return self.result + other.result
        elif isinstance(other, int):
            return self.result + other
        else:
            raise TypeError(f"Can't add {type(other)} to a Roll!")

    def __sub__(self, other):
        if isinstance(other, Roll):
            return self.result - other.result
        elif isinstance(other, int):
            return self.result - other
        else:
            raise TypeError(f"Can't subtract {type(other)} from a Roll!")

    def __radd__(self, other):
        if isinstance(other, Roll):
            return other.result + self.result
        elif isinstance(other, int):
            return other + self.result
        else:
            raise TypeError(f"Can't add a Roll to {type(other)}!")

    def __rsub__(self, other):
        if isinstance(other, Roll):
            return other.result - self.result
        elif isinstance(other, int):
            return other - self.result
        else:
            raise TypeError(f"Can't subtract a Roll from {type(other)}!")

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
    def drop_least(cls, num=4, die=6, mod=0):
        """Return a multi-die Roll with the lowest result among the dice dropped."""
        return cls(num, die, mod, dropleast=True)


class DndCharacter(rpgtools.Character):

    def __init__(self, *, dnd_class="fighter", race="human", gender="female", level=1, proficiencies=(), stats=()):
        super().__init__(setting="fantasy",race=race, gender=gender)
        self.stats = {}
        if stats and isinstance(stats, tuple):
            self.set_stats(*stats)
        else:
            self.roll_stats()
        self.mods = {}
        self.update_mods()
        self.level = level
        self.proficiencies = proficiencies

    def roll_stats(self):
        for stat in ("str", "dex", "con", "int", "wis", "cha"):
            self.stats[stat] = int(Roll.drop_least())

    def set_stats(self, *args):
        all_ints = True
        for item in args:
            if not isinstance(item, int):
                all_ints = False
        if len(args) == 6 and all_ints:
            for i in range(6):
                self.stats[STATS[i]] = args[i]
            self.update_mods()
        else:
            raise KeyError("Set_stats requires six integer inputs!")

    def update_mods(self):
        for stat in self.stats.keys():
            self.mods[stat] = (self.stats[stat]-10)//2
        # 5e proficiency mod scales with this formula (2 @ 1-4, 3 @ 5-8, etc)
        self.prof_mod = (self.level - 1) // 4 + 2

    # def __str__(self):
    #     # Hidden functions to shorten code below
    #     def pad(num, amount=3):
    #         return str(num).rjust(amount, " ")
    #     def padmod(num, amount=3):
    #         """Pad & format modifier"""
    #         if num < 0:
    #             return pad(num, amount)
    #         else:
    #             return pad("+" + str(num), amount)
    #
    #     with open("src/dnd_ascii_charsheet.txt", "r") as f:
    #         ascii_sheet = f.read()
    #     pretty_print_skill_mods = []
    #     for s in dnd.SKILLS:
    #         mod = padmod(self.skills[s], 3)
    #         # Mark proficient skills but make prof and non-prof the same length
    #         # to fit charsheet
    #         if s in self.proficiencies:
    #             mod += "*"
    #         else:
    #             mod += " "
    #         pretty_print_skill_mods.append(mod)
    #     out = ascii_sheet.format(
    #         self.name.ljust(18, " "),
    #         self.surname.ljust(18, " "),
    #         self.prof.ljust(18, " "),
    #         *[pad(self.stats[s], 3) for s in ('str', 'dex', 'con',
    #                                           'int', 'wis', 'cha')],
    #         *[padmod(self.mods[s], 3) for s in ('str', 'dex', 'con',
    #                                             'int', 'wis', 'cha')],
    #         padmod(self.prof_mod, 4),
    #         padmod(self.mods['dex'], 4),
    #         *pretty_print_skill_mods
    #         )
    #     return out

    # TODO - Complete this method
    @classmethod
    def random(cls):
        self.proficiencies = sample(list(SKILLS), 5)
        for p in self.proficiencies:
            self.skills[p] += self.prof_mod
    # proficiencies and level not used by Character so don't bother passing
