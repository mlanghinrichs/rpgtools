## RPGTools ##
This project is a nascent python module for tabletop rpg generation and statistical analysis. The primary module includes utility methods and all-purpose generators, and sub-modules contain system-specific utilities and objects.
* * * * *
### rpgtools - Container Module ###
rpg.py contains generalized Character and Adventure superclasses.

### rpgtools.dnd - Dungeons and Dragons ###
The dnd sub-module contains Roll and DndCharacter classes specific to 5th ed. _Dungeons and Dragons_. It will eventually contain D&D-specific adventures as well.

### rpgtools.gsys - Genesys ###
The gsys sub-module contains the Roll class for Fantasy Flight's _Genesys_ RPG, including a static method for determining success probabilities in narrative dice pools.
