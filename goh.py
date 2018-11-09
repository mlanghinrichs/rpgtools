from random import choice
import os, rstr

# Keys establish which files to pull into dict
goh = dict(locales=[], sub_locales=[], plot=[], objective=[], hours=[], story_elements=[])

# For each key in goh, pull an associated text file to pull as list
for key in list(goh):
    with open("goh/" + key + ".txt", "r") as f:
        goh[key] = list(map(lambda s: s[:-1], f.readlines()))

class Adventure:
    """A class of Adventure objects, containing data/functions for a GoH session."""

    def __init__(self):
        
        # Create (r)aw dict to contain raw adventure data
        self.raw = {}

        # For each list in goh, pull a str choice or list of choices to put into raw
        for key in list(goh):
            try:
                if key == "hours" or key == "story_elements":
                    self.raw[key] = [choice(goh[key]) for x in range(3)]
                else:
                    self.raw[key] = choice(goh[key])
            except IndexError:
                print("No content in file %s.txt!" % key)
                self.raw[key] = "Error"

        # Finally, set a title for the adventure
        self.raw['title'] = "THE " + self.raw['story_elements'][0].upper() + " OF " + self.raw['locales'].upper()
        
    
    def desc(self):
        """Return a formatted str containing the adventure details written out."""

        # For shorter code
        raw = self.raw

        # A block of messy code that creates the description layout and populates it
        out = raw['title']
        out += "\nIn {}, in {};".format(raw['locales'], raw['sub_locales'])
        out += "\nA {}, to {}.".format(raw['plot'], raw['objective'])
        out += "\n"
        # Generalizable to any # of hours; uncomment line to add modular detail lines
        for n in range(len(raw['hours'])):
            out += "\nIn hour {}, {}.".format(n+1, raw['hours'][n])
            # out += "\n\ta.\n\tb.\n\tc.\n\td.\n\te."
        out += "\n\nRandom elements:"
        # Generalizable to any # of elements
        for n in range(len(raw['story_elements'])):
            out += "\n{}. {}".format(n+1, raw['story_elements'][n])

        # Return the description string
        return out

    def write(self, direc):
        """Write adventure details to a txt file in ./direc/ named after the title."""
        
        # Str containing path to save file to
        path = direc + "/" + self.raw['title'].replace(" ", "") + ".txt"
        path = path.lower() # fix dramatic title capitalization
        if not os.path.isfile(path): # make sure the filename doesn't exist yet
            with open(path, "w") as f:
                f.write(self.desc())
            print("Wrote to " + path)

new = Adventure()
print(new.desc())

# for i in range(100):
#    x = Adventure()
#    x.write("goh_advs")
#    print(i)
