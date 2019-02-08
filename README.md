## RPGTools ##
This project is a nascent python module for tabletop rpg generation and statistical analysis. The primary module includes utility methods and all-purpose generators, and sub-modules contain system-specific utilities and objects.
* * * * *
### rpgtools - Container Module ###
rpg.py contains Character and Adventure superclasses, as well as a handful of internal utility functions.

### rpgtools.dnd - Dungeons and Dragons ###
The dnd sub-module contains Roll and DndCharacter classes specific to 5th ed. Dungeons and Dragons. It will eventually contain D&D-specific adventures as well.

### rpgtools.gsys - Genesys ###
The gsys sub-module contains the Roll class for Fantasy Flight's Genesys RPG, including a static method for determining success probabilities in dice pools.
