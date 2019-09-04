# im-home
A Snips skill that that is designed for a user to activate when they enter a home (living_lab).

Snips will respond to the "im home" intent and then begin asking a series of questions and prepare the home for you. 
E.g. do you want the lights on or do you want the TV on? 

This skill demonstrates the use of a multi-turn dialogue as well as using API requests to the Home Assistant running on the pi.

This skill should be installed with the "im-leaving" skill which similar but asks for intents to turn devices off rather than on.
To install this/these skills follow a process like:

1. Backup the Hass configuration folder (if needed)
2. If reinstalling make sure to delete the im-home & im-leaving skills directories from /var/lib/snips/skills
3. Install the assistant from the command line using SAM (sam install assistant)
4. When asked for the key use the long lived access token e.g. (Bearer realLylOngLivEdAcCesStOOkeN) 
4. Sam will explain the files need to be executable and will also give a warning about python 2.7.
5. Go to the action files and use chmod
6. Use sam install actions again
7. Undo changes to the configuration.yaml (if any)
