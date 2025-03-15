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
import re

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
        """
        Parses a command string and executes the corresponding action.
        """
        # Cleanup the input
        commandString = commandString.strip().lower()
        
        # Abort gracefully if the command is empty
        if len(commandString) == 0:
            return True
        
        # Handle complex commands (e.g., "take key and open door")
        if ' and ' in commandString:
            self.parseComplexCommand(commandString, sourceNounId)
            return True
        
        # Handle prepositions (e.g., "take key with hand")
        if ' with ' in commandString or ' using ' in commandString:
            self.handlePrepositions(commandString, sourceNounId)
            return True
        
        # Handle contextual commands (e.g., "look" vs. "look at key")
        self.handleContextualCommands(commandString, sourceNounId)
        return True


    def runScript(self, script):
        """
        Executes a Python script string.
        """
        self.model.execPythonString(script)


    def parseComplexCommand(self, commandString, sourceNounId):
        """
        Parses complex commands with multiple verbs and nouns.
        """
        # Split the command into parts based on conjunctions like "and"
        parts = re.split(r'\s+and\s+', commandString)
        for part in parts:
            self.parseSimpleCommand(part, sourceNounId)


    def parseSimpleCommand(self, commandString, sourceNounId):
        """
        Parses a simple command (single verb and noun).
        """
        # Split the command into words
        cmdWords = commandString.split(' ')
        
        # Assume the first word is a verb
        verbString = cmdWords[0]
        
        # Assume the second word is a noun (skip "the" or "at")
        nounString = None
        if len(cmdWords) > 1:
            nounString = cmdWords[1]
            if nounString in ['the', 'a', 'an', 'at']:
                nounString = cmdWords[2] if len(cmdWords) > 2 else None
        
        # Search known verbs
        match = None
        for knownVerb in self.model.verbs:
            if verbString == knownVerb['id']:
                match = knownVerb
                break
            else:
                # Search known synonyms
                for knownSynonym in knownVerb['synonyms']:
                    if verbString == knownSynonym:
                        match = knownVerb
                        verbString = match['id']
                        break
        
        # Was there a match?
        if match is not None:
            try:
                targetNounId = self.model.nounIdWithShortDesc(nounString) if nounString else None
                # Pass sourceNounId and targetNounId to the script
                pythonString = self.model.expandSpecialVariablesInString(match['immediately'], sourceNounId, verbString, targetNounId, nounString)
                self.model.execPythonString(pythonString, sourceNounId, verbString, targetNounId, nounString)
                # Increment user's turns_taken
                turn = int(self.model.nounWithId(sourceNounId)['turns_taken'])
                self.model.nounWithId(sourceNounId)['turns_taken'] = str(turn + 1)
            except Exception as e:
                print(f"\nI don't understand '{commandString}'. Try something else.")
        else:
            self.suggestCommand(commandString, sourceNounId)


    def suggestCommand(self, commandString, sourceNounId):
        """
        Suggests possible commands based on the input.
        """
        # Get the current room and inventory
        currentRoom = self.model.roomsContainingNounWithId(sourceNounId)[0]
        inventory = self.model.nounWithId(sourceNounId)['inventory']
        
        # Suggest verbs based on the current context
        possibleVerbs = []
        for verb in self.model.verbs:
            if verb['id'] in ['look', 'take', 'drop', 'use', 'kill', 'flee', 'inventory']:
                possibleVerbs.append(verb['id'])
        
        # Suggest nouns based on the current room and inventory
        possibleNouns = []
        for nounId in currentRoom['obvious_nouns']:
            noun = self.model.nounWithId(nounId)
            possibleNouns.append(noun['short_desc'])
        for itemId in inventory:
            item = self.model.nounWithId(itemId)
            possibleNouns.append(item['short_desc'])
        
        # Generate suggestions
        suggestions = []
        for verb in possibleVerbs:
            for noun in possibleNouns:
                suggestions.append(f"{verb} {noun}")
        
        # Display suggestions
        print(f"\nI don't understand '{commandString}'. Did you mean one of these?")
        for suggestion in suggestions[:5]:  # Limit to 5 suggestions
            print(f"- {suggestion}")


    def handlePrepositions(self, commandString, sourceNounId):
        """
        Handles prepositions in commands (e.g., "take key with hand").
        """
        # Split the command into parts based on prepositions
        if ' with ' in commandString:
            parts = commandString.split(' with ')
        elif ' using ' in commandString:
            parts = commandString.split(' using ')
        else:
            parts = [commandString]
        
        # Parse the main command (e.g., "take key")
        mainCommand = parts[0]
        self.parseSimpleCommand(mainCommand, sourceNounId)
        
        # Handle the tool or secondary object (e.g., "with hand")
        if len(parts) > 1:
            toolCommand = parts[1]
            toolNounId = self.model.nounIdWithShortDesc(toolCommand)
            if toolNounId:
                # Check if the tool is in the player's inventory
                if toolNounId in self.model.nounWithId(sourceNounId)['inventory']:
                    print(f"\nYou use the {toolCommand} to complete the action.")
                else:
                    print(f"\nYou don't have the {toolCommand} in your inventory.")
            else:
                print(f"\nI don't see a {toolCommand} here.")


    def handleContextualCommands(self, commandString, sourceNounId):
        """
        Handles commands that change based on context (e.g., "look" vs. "look at key").
        """
        # Handle "look" command
        if commandString == 'look':
            self.model.lookAtNounStringFromNounWithId('$', sourceNounId)
            return
        
        # Handle "look at [noun]" command
        if commandString.startswith('look at '):
            nounString = commandString[8:]  # Remove "look at "
            # Strip out articles like "the," "a," or "an"
            nounString = re.sub(r'^(the|a|an)\s+', '', nounString)
            self.model.lookAtNounStringFromNounWithId(nounString, sourceNounId)
            return
        
        # Handle other contextual commands
        self.parseSimpleCommand(commandString, sourceNounId)