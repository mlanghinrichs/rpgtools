from random import choice
import os

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
        self.r = {}

        # For each list in goh, pull a str choice or list of choices to put into raw
        for key in list(goh):
            try:
                if key == "hours" or key == "story_elements":
                    self.r[key] = [choice(goh[key]) for x in range(3)]
                else:
                    self.r[key] = choice(goh[key])
            except IndexError:
                print("No content in file %s.txt!" % key)
                self.r[key] = "Error"

        # Finally, set a title for the adventure
        self.r['title'] = "THE " + self.r['story_elements'][0].upper() + " OF " + self.r['locales'].upper()
        
    
    def desc(self):
        """Return a formatted str containing the adventure details written out."""

        # For shorter code
        r = self.r

        # A block of messy code that creates the description layout and populates it
        out = r['title']
        out += "\nIn {}, in {};".format(r['locales'], r['sub_locales'])
        out += "\nA {}, to {}.".format(r['plot'], r['objective'])
        out += "\n"
        # Generalizable to any # of hours
        for n in range(len(r['hours'])):
            out += "\nIn hour {}, {}.".format(n+1, r['hours'][n])
        out += "\n\nRandom elements:"
        # Generalizable to any # of elements
        for n in range(len(r['story_elements'])):
            out += "\n{}. {}".format(n+1, r['story_elements'][n])

        # Return the description string
        return out

    def write(self, direc):
        """Write adventure details to a txt file in ./direc/ named after the title."""
        
        # Str containing path to save file to
        path = direc + "/" + self.r['title'].replace(" ", "") + ".txt"
        path = path.lower() # fix dramatic title capitalization
        if not os.path.isfile(path): # make sure the filename doesn't exist yet
            with open(path, "w") as f:
                f.write(self.desc())
            print("Wrote to " + path)

for i in range(100):
    x = Adventure()
    x.write("goh_advs")
    print(i)
