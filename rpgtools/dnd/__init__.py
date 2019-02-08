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

CLASS_SKILLS = {"barbarian": (
                    "Animal Handling",
                    "Athletics",
                    "Intimidation",
                    "Nature",
                    "Perception",
                    "Survival"
                ),
                "bard": tuple(SKILLS),
                "cleric": (
                    "History",
                    "Insight",
                    "Medicine",
                    "Persuasion",
                    "Religion"
                ),
                "druid": (

                ),
                "fighter": (

                ),
                "monk": (

                ),
                "paladin": (

                ),
                "ranger": (

                ),
                "rogue": (

                ),
                "sorcerer": (

                ),
                "warlock": (

                ),
                "wizard": (

                )}

CLASS_NUMBER_PROFICIENCIES = {"barbarian": 2,
                              "bard": 3,
                              "cleric": 2,
                              "druid": 0,
                              "fighter": 0,
                              "monk": 0,
                              "paladin": 0,
                              "ranger": 0,
                              "rogue": 0,
                              "sorcerer": 0,
                              "warlock": 0,
                              "wizard": 0}

STATS = ("str", "dex", "con", "int", "wis", "cha")
STATS_FULL_NAMES = ("strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma")


class Roll:

    def __init__(self, num=1, die=20, mod=0, *, dropleast=False, **kwargs):
        self.num = num
        self.die = die
        self.mod = mod

        self.rolls = []
        for i in range(num):
            self.rolls.append(randint(1, die))
        if dropleast:
            self.rolls.remove(min(self.rolls))
        if "result" not in kwargs:
            self.result = sum(self.rolls) + mod
        else:
            self.result = kwargs['result']

    def __str__(self):
        return str(self.result)

    def __lt__(self, other):
        if isinstance(other, Roll):
            return self.result < other.result
        elif isinstance(other, int) or isinstance(other, float):
            return self.result < other
        else:
            raise TypeError(f"Can't compare {type(other)} with a Roll!")

    def __gt__(self, other):
        if isinstance(other, Roll):
            return self.result > other.result
        elif isinstance(other, int) or isinstance(other, float):
            return self.result > other
        else:
            raise TypeError(f"Can't compare {type(other)} with a Roll!")

    def __int__(self):
        return int(self.result)

    def __float__(self):
        return float(self.results)

    def __add__(self, other):
        if isinstance(other, Roll):
            return self.result + other.result
        elif isinstance(other, int) or isinstance(other, float):
            return self.result + other
        else:
            raise TypeError(f"Can't add {type(other)} to a Roll!")

    def __sub__(self, other):
        if isinstance(other, Roll):
            return self.result - other.result
        elif isinstance(other, int) or isinstance(other, float):
            return self.result - other
        else:
            raise TypeError(f"Can't subtract {type(other)} from a Roll!")

    def __radd__(self, other):
        if isinstance(other, Roll):
            return other.result + self.result
        elif isinstance(other, int) or isinstance(other, float):
            return other + self.result
        else:
            raise TypeError(f"Can't add a Roll to {type(other)}!")

    def __rsub__(self, other):
        if isinstance(other, Roll):
            return other.result - self.result
        elif isinstance(other, int) or isinstance(other, float):
            return other - self.result
        else:
            raise TypeError(f"Can't subtract a Roll from {type(other)}!")

    @classmethod
    def from_string(cls, string):
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
        """Return a multi-die Roll with the lowest die roll dropped."""
        return cls(num, die, mod, dropleast=True)


class DndCharacter(rpgtools.Character):

    def __init__(self, **kwargs):
        super().__init__(setting="fantasy", **kwargs)

        self.stats = {}
        self.mods = {}
        self.skill_mods = {}
        for item in ("stats",
                     "level",
                     "dnd_class",
                     "proficiencies"):
            if item in kwargs and item != "stats":
                self.__dict__[item] = kwargs[item]
            elif item in kwargs and item == "stats":
                self.set_stats(*kwargs["stats"])
            else:
                if item == "stats":
                    self.roll_stats()
                elif item == "level":
                    self.level = 1
                elif item == "dnd_class":
                    self.dnd_class = "npc"
                elif self.dnd_class == "npc" and item == "proficiencies":
                    self.proficiencies = sample(list(SKILLS), 5)
                elif self.dnd_class != "npc" and item == "proficiencies":
                    c = self.dnd_class
                    self.proficiencies = sample(CLASS_SKILLS[c],
                                                CLASS_NUMBER_PROFICIENCIES[c])
        self.update_mods()
        self.update_skill_mods()

    def roll_stats(self):
        for stat in ("str", "dex", "con", "int", "wis", "cha"):
            self.stats[stat] = int(Roll.drop_least())

    def set_stats(self, *args):
        # Check input type
        for item in args:
            if not isinstance(item, int):
                raise KeyError(f"set_stats() requires integer inputs!")
        try:
            for i in range(6):
                self.stats[STATS[i]] = args[i]
            self.update_mods()
        except IndexError:
            raise IndexError("set_stats() requires 6 inputs!")

    def update_mods(self):
        for stat in self.stats.keys():
            self.mods[stat] = (self.stats[stat]-10)//2
        # 5e proficiency mod scales with this formula (2 @ 1-4, 3 @ 5-8, etc)
        self.prof_mod = (self.level - 1) // 4 + 2

    def update_skill_mods(self):
        for key in SKILLS:
            skill = self.mods[SKILLS[key]]
            if key in self.proficiencies:
                skill += self.prof_mod
            self.skill_mods[key] = skill
