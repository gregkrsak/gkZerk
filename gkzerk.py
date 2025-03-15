#!/usr/bin/env python3
# Filename: gkzerk.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# gkZerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. gkZerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the main game logic.
#

import io
import sys
import json
import os.path

from zerk_state import ZerkGameState

from zerk_mvc.ZerkModel import ZerkModel
from zerk_mvc.ZerkView import ZerkView
from zerk_mvc.ZerkController import ZerkController
from zerk_mvc.ZerkUser import ZerkUser


def main(mapFile):
    """
    Main program block for gkZerk
    """
    if fileExists(mapFile):
        map = loadMap(mapFile)
        play(map)
    else:
        usage()


def fileExists(filename):
    """
    Returns True if a filename exists
    """
    result = True
    if os.path.isfile(filename) == False:
        result = False
    return result


def loadMap(filename):
    """
    Loads JSON from a gkZerk map and returns the data
    """
    jsonString = open(filename).read()
    result = json.loads(jsonString)
    return result


def play(map):
    """
    The main game logic for gkZerk
    """
    # Define the local console
    localInput = sys.stdin
    localOutput = sys.stdout
    # Create a model instance (shared by all users)
    model = ZerkModel(map)
    # Create a user instance (containing a local view and controller)
    localUser = ZerkUser(ZerkView(localOutput, model), ZerkController(localInput, model))
    
    # Connect the user instance to the shared model (via the controller)
    localUser.connect()
    # User wants to play
    localUser.stillWantsToPlay = True
    # Set game state to Starting
    localUser.gameState = ZerkGameState.Starting

    # Main game loop
    while localUser.stillWantsToPlay:
        # Starting
        if localUser.gameState == ZerkGameState.Starting:
            localUser.transmit()
            localUser.gameState = ZerkGameState.Started
        # Started
        elif localUser.gameState == ZerkGameState.Started:
            localUser.transmit()
            localUser.gameState = ZerkGameState.Playing
        # Playing (primary gameplay)
        elif localUser.gameState == ZerkGameState.Playing:
            # Run before_each_turn noun scripts
            localUser.processBeforeTurnTriggers()
            # Transmit the user's view
            localUser.transmit()
            # Receive input from the user
            input = localUser.receive()
            # Process the input
            localUser.controller.parseCommandFromNounWithId(input, localUser.data['id'])
            # Run after_each_turn noun scripts
            localUser.processAfterTurnTriggers()
        # Finished / Won
        elif localUser.gameState == ZerkGameState.FinishedWon:
            # Transmit victory notification to all nouns
            for noun in localUser.controller.model.nouns:
                localUser.controller.model.sendNotificationToNoun(noun['id'] + ' has won the game.', noun)
                # And if any playable nouns aren't this user, they've lost
                if (noun['playable'] == 'true') and (noun['id'] != localUser.data['id']):
                    noun['id']['game_state'] = 'finished_lost'
                    localUser.controller.model.sendNotificationToNoun('Due to the sudden horror of this realization, you immediately drop dead of a heart attack.', noun)
            # Transmit the user's view
            localUser.transmit()
            localUser.gameState = ZerkGameState.Quitting
        # Finished / Lost
        elif localUser.gameState == ZerkGameState.FinishedLost:
            localUser.transmit()
            localUser.gameState = ZerkGameState.Quitting
        # Quitting
        elif localUser.gameState == ZerkGameState.Quitting:
            localUser.transmit()
            localUser.stillWantsToPlay = False
    
    # Set game state to Quit
    localUser.gameState = ZerkGameState.Quit
    # Disconnect the user instance from the shared model
    localUser.disconnect()


def usage():
    """
    Displays usage information
    """
    print('gkZerk, an iteractive fiction interpreter')
    print('Copyright (c) 2013, 2025 Greg M. Krsak (greg.krsak@gmail.com)')
    print('Provided under the MIT License: http://opensource.org/licenses/MIT')
    print()
    print('Usage: gkzerk.py <json_filename>')
    print()
    print('Where <json_filename> is the filename of a JSON-formatted gkZerk map.')
    print('Please report any bugs to greg.krsak@gmail.com')


if __name__ == '__main__':
    argv = ''
    try:
        argv = sys.argv[1]
    except:
        pass
    main(argv)
