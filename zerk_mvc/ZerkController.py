# Filename: ZerkController.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# gkZerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. gkZerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the MVC "controller" code.
#

import os

from zerk_state import ZerkGameState


class ZerkController:
    
    def __init__(self, inputStream, model):
        self.input = inputStream
        self.model = model

    
    def gameStateForUserWithId(self, userId):
        return self.model.gameStateForNounWithId(userId)


    def setGameStateForUserWithId(self, gameState, userId):
        self.model.setGameStateForNounWithId(gameState, userId)


    def connectUser(self, user):
        self.model.connectUser(user)


    def disconnectUser(self, user):
        self.model.disconnectUserWithId(user.data['id'])

    
    def waitForInput(self):
        return self.input.readline()


    def preprocessedBeforeTurnTriggerForNoun(self, noun):
        return self.model.preprocessedTriggerForNoun('before_each_turn', noun)


    def preprocessedAfterTurnTriggerForNoun(self, noun):
        return self.model.preprocessedTriggerForNoun('after_each_turn', noun)


    def parseCommandFromNounWithId(self, commandString, sourceNounId):
        # Cleanup the input
        commandString = commandString.strip().lower()
        
        # Abort gracefully if the command is empty
        if len(commandString) == 0:
            return True;
        
        # Split the command into separate words
        cmdWords = commandString.split(' ')

        # Assume the first word is a verb
        verbString = cmdWords[0]
        # Assume the second word is a noun
        try:
            nounString = cmdWords[1]
            # Wait, is this second word the word "the" or "at"?..
            if (nounString == 'the') or (nounString == 'at'):
                try:
                    # Assume the third word is a noun
                    nounString = cmdWords[2]
                except:
                    # Can't have verb+"the" or verb+"at" without a noun
                    return False;
        except:
            # No noun, no problem
            nounString = None

        # Playing
        # TODO: Support initial word 'go' (as in the command string 'go north')
        if self.model.gameStateForNounWithId(sourceNounId) == ZerkGameState.Playing:
            
            # Search known verbs
            match = None
            for knownVerb in (self.model.verbs):
                if verbString == knownVerb['id']: # TODO: Support abbreviations
                    match = knownVerb
                    break
                else:
                    # Search known synonyms
                    for knownSynonym in knownVerb['synonyms']:
                        if verbString == knownSynonym: # TODO: Support abbreviations
                            match = knownVerb
                            verbString = match['id']
                            break

            # Was there a match?
            if match != None:
                try:
                    targetNounId = self.model.nounIdWithShortDesc(nounString)
                except:
                    targetNounId = ''
                pythonString = self.model.expandSpecialVariablesInString(match['immediately'], sourceNounId, verbString, targetNounId, nounString)
                # DEBUG
                #print('[DEBUG] running script: ' + pythonString)
                self.model.execPythonString(pythonString)
                # Increment user's turns_taken
                turn = int(self.model.nounWithId(sourceNounId)['turns_taken'])
                self.model.nounWithId(sourceNounId)['turns_taken'] = str(turn + 1)
            else:
                print('\nI don\'t know how to ' + verbString + '.')


    def runScript(self, script):
        self.model.execPythonString(script)
  