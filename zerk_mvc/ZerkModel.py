# Filename: ZerkModel.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# gkZerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. gkZerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the MVC "model" code. In gkZerk, the model is the only way
# to directly modify the global mutable state.
#

import random

from zerk_state import ZerkGameState


class ZerkModel:
    
    def __init__(self, mapJson):
        random.seed()
        self._map = mapJson
        self._map['users'] = []

    
    @property
    def idString(self):
        return self._map['zerk']
    
    @property
    def about(self):
        return self._map['about']
    
    @property
    def version(self):
        return self._map['version']
    
    @property
    def roomTypes(self):
        return self._map['room_types']

    @property
    def rooms(self):
        return self._map['rooms']

    @property
    def nouns(self):
        return self._map['nouns']
    
    @property
    def verbs(self):
        return self._map['verbs']
    
    @property
    def scripts(self):
        return self._map.get('scripts', [])
    
    @property
    def nextPlayableNounId(self):
        result = None
        for noun in self.nouns:
            if noun['playable'] == 'true':
                result = noun['id']
        return result
    
            
    def connectUser(self, newUser):
        self.nounWithId(newUser.data['id'])['active'] = 'true'
        self.nounWithId(newUser.data['id'])['connected'] = 'true'


    def disconnectUserWithId(self, userId):
        self.nounWithId(userId)['active'] = 'false'
        self.nounWithId(userId)['connected'] = 'false'
    
    
    def childObjectOfParentArrayKeyWithChildId(self, parentArrayKey, objectId):
        result = None
        for childObj in self._map[parentArrayKey]:
            if childObj['id'] == objectId:
                result = childObj
        return result

    
    def roomWithId(self, roomId):
        return self.childObjectOfParentArrayKeyWithChildId('rooms', roomId)

    
    def roomTypeWithId(self, roomTypeId):
        return self.childObjectOfParentArrayKeyWithChildId('room_types', roomTypeId)

    
    def nounWithId(self, nounId):
        return self.childObjectOfParentArrayKeyWithChildId('nouns', nounId)

    
    def nounIdWithShortDesc(self, shortDesc):
        """
        Returns the ID of a noun that matches the given short description (partial or full).
        """
        result = None
        for noun in self.nouns:
            # Check if the input is a substring of the noun's short description
            if shortDesc.lower() in noun['short_desc'].lower():
                result = noun['id']
                break
        return result
    
    
    def grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys(self, greatGrandparentArrayKey, parentArrayKey, childString):
        result = []
        for grandparentObj in self._map[greatGrandparentArrayKey]:
            for childStr in grandparentObj[parentArrayKey]:
                if childStr == childString:
                    result.append(grandparentObj)
        return result

    
    def roomsContainingNounWithId(self, nounId):
        result = []
        result = self.grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys('rooms', 'obvious_nouns', nounId)
        if len(result) == 0:
            # If the noun is found in another noun's inventory, return the room of that noun
            result = self.grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys('nouns', 'inventory', nounId)
            if len(result) != 0:
                result = self.roomsContainingNounWithId(result[0]['id'])
        return result

    
    def setLitInRoomWithId(self, roomId, isLit):
        room = self.roomWithId(roomId)
        if isLit:
            room['lit'] = 'true'
        else:
            room['lit'] = 'false'


    def gameStateForNounWithId(self, nounId):
        result = None
        gameState = self.nounWithId(nounId)['game_state']
        if gameState == 'starting':
            result = ZerkGameState.Starting
        elif gameState == 'started':
            result = ZerkGameState.Started
        elif gameState == 'playing':
            result = ZerkGameState.Playing
        elif gameState == 'finished_won':
            result = ZerkGameState.FinishedWon
        elif gameState == 'finished_lost':
            result = ZerkGameState.FinishedLost
        elif gameState == 'quitting':
            result = ZerkGameState.Quitting
        elif gameState == 'quit':
            result = ZerkGameState.Quit
        return result


    def setGameStateForNounWithId(self, gameState, nounId):
        if gameState == ZerkGameState.Starting:
            self.nounWithId(nounId)['game_state'] = 'starting'
        elif gameState == ZerkGameState.Started:
            self.nounWithId(nounId)['game_state'] = 'started'
        elif gameState == ZerkGameState.Playing:
            self.nounWithId(nounId)['game_state'] = 'playing'
        elif gameState == ZerkGameState.FinishedWon:
            self.nounWithId(nounId)['game_state'] = 'finished_won'
        elif gameState == ZerkGameState.FinishedLost:
            self.nounWithId(nounId)['game_state'] = 'finished_lost'
        elif gameState == ZerkGameState.Quitting:
            self.nounWithId(nounId)['game_state'] = 'quitting'
        elif gameState == ZerkGameState.Quit:
            self.nounWithId(nounId)['game_state'] = 'quit'


    def expandSpecialVariablesInString(self, theString, sourceNounId, verbId, targetNounId, nounString):
        """
        Expands special variables in a string (e.g., ${SOURCE_NOUN_ID}, ${TARGET_NOUN_ID}).
        """
        if theString is None:
            return None  # Return None if the input string is None
        if sourceNounId is not None:
            theString = theString.replace('${SOURCE_NOUN_ID}', str(sourceNounId))
        if targetNounId is not None:
            theString = theString.replace('${TARGET_NOUN_ID}', str(targetNounId))
        if verbId is not None:
            theString = theString.replace('${VERB_ID}', str(verbId))
        if nounString is not None:
            theString = theString.replace('${TARGET_NOUN_STRING}', str(nounString))
        return theString


    def scriptWithId(self, scriptId):
        """
        Returns the script code for a given script ID.
        """
        for script in self.scripts:
            if script['id'] == scriptId:
                return script['code']
        return None


    def execPythonString(self, pythonString, sourceNounId=None, verbId=None, targetNounId=None, nounString=None):
        """
        Executes a Python script string or looks up and executes a script by ID.
        """
        if pythonString is None:
            print('[DEBUG] Script is None, skipping execution.')
            return False  # Skip execution if the script is None

        #print(f'[DEBUG] Executing script: {pythonString}')
        #print(f'[DEBUG] sourceNounId: {sourceNounId}, targetNounId: {targetNounId}, verbId: {verbId}, nounString: {nounString}')

        if pythonString.startswith('script_'):
            scriptId = pythonString
            pythonString = self.scriptWithId(scriptId)
            if pythonString is None:
                print(f'[DEBUG] Script ID {scriptId} not found.')
                return False

        # Expand special variables in the script
        pythonString = self.expandSpecialVariablesInString(pythonString, sourceNounId, verbId, targetNounId, nounString)

        if pythonString is None:
            print('[DEBUG] Expanded script is None, skipping execution.')
            return False  # Skip execution if the expanded script is None

        try:
            exec(pythonString, {'self': self})
            return True
        except Exception as e:
            print(f'[WARNING] Script failed: {pythonString}\nError: {e}')
            return False


    def preprocessedTriggerForNoun(self, trigger, noun):
        result = ''
        if noun[trigger] is not None:
            result = self.expandSpecialVariablesInString(noun[trigger], noun['id'], None, None, None)
        return result


    def moveNounWithIdThroughExit(self, nounId, exitDir):
        result = True
        currentRoom = self.roomsContainingNounWithId(nounId)[0]
        try:
            newRoomId = currentRoom['exit_' + exitDir]
            room = self.roomWithId(newRoomId)
            noun = self.nounWithId(nounId)
            allowedIn = True
            scared = False
            # Is this noun afraid of anything in its current room?
            for scaryItemId in noun['afraid_of']:
                if (scaryItemId in currentRoom['obvious_nouns']) and (self.nounWithId(scaryItemId)['alive'] == 'true'):
                    scared = True
            if not scared:
                # Are there any required items in the new room?
                if len(room['requires_nouns']) != 0:
                    # Check the noun's inventory for those items
                    for requiredItem in room['requires_nouns']:
                        if requiredItem not in noun['inventory']:
                            allowedIn = False
                if allowedIn:
                    # Attempt to move the noun
                    self.removeNounWithIdFromRoomWithId(nounId, currentRoom['id'])
                    self.addNounWithIdToRoomWithId(nounId, newRoomId)
                    # Run the on_entry script of the new room
                    pythonString = self.expandSpecialVariablesInString(room['on_entry'], nounId, exitDir, None, None)
                    self.execPythonString(pythonString)
                else:
                    # Notify the noun that it's missing required items
                    self.sendNotificationToNoun('You\'re missing an item that permits you to go that way.', noun)
            else:
                # Notify the noun that it's afraid
                self.sendNotificationToNoun('You\'re too terrified to do that!', noun)
        except:
            result = False
            # Unable to move
            noun = self.nounWithId(nounId)
            # Notify the noun of its inability to move
            self.sendNotificationToNoun('You can\'t go that way.', noun)
        return result


    def sendNotificationToNoun(self, notificationString, noun):
        result = False
        # Only send the notification if the noun is playable and connected
        if noun['playable'] == 'true':
            if noun['connected'] == 'true':
                noun['notifications'].append(notificationString)
                result = True
        return result


    def addNounWithIdToRoomWithId(self, nounId, roomId):
        result = False
        obviousNouns = self.roomWithId(roomId)['obvious_nouns']
        if nounId not in obviousNouns:
            obviousNouns.append(nounId)
            result = True
        return result
    

    def removeNounWithIdFromRoomWithId(self, nounId, roomId):
        result = False
        obviousNouns = self.roomWithId(roomId)['obvious_nouns']
        if nounId in obviousNouns:
            obviousNouns.remove(nounId)
            result = True
        return result


    def addNounWithIdToInventoryOfNounWithId(self, sourceNounId, targetNounId):
        result = False
        sourceNoun = self.nounWithId(sourceNounId)
        targetNoun = self.nounWithId(targetNounId)
        if sourceNounId not in targetNoun['inventory']:
            targetNoun['inventory'].append(sourceNounId)
            result = True
            self.sendNotificationToNoun('Taken.', self.nounWithId(targetNounId))
            # Run the on_take script
            pythonString = self.expandSpecialVariablesInString(sourceNoun['on_take'], targetNounId, 'take', sourceNounId, 'take')
            self.execPythonString(pythonString)
        return result


    def removeNounWithIdFromInventoryOfNounWithId(self, sourceNounId, targetNounId):
        result = False
        sourceNoun = self.nounWithId(sourceNounId)
        targetNoun = self.nounWithId(targetNounId)
        if sourceNounId in targetNoun['inventory']:
            targetNoun['inventory'].remove(sourceNounId)
            result = True
            self.sendNotificationToNoun('Dropped.', self.nounWithId(targetNounId))
            # Run the on_drop script
            pythonString = self.expandSpecialVariablesInString(sourceNoun['on_drop'], targetNounId, 'drop', sourceNounId, 'drop')
            self.execPythonString(pythonString)
        return result


    def switchNounWithId(self, nounId):
        result = False
        noun = self.nounWithId(nounId)
        if noun['switchable'] == 'true':
            result = True
            holders = self.grandparentObjectsOfChildStringWithGreatGrandparentAndParentArrayKeys('nouns', 'inventory', nounId)
            if noun['on'] == 'false':
                noun['on'] = 'true'
                for holdingNoun in holders:
                    self.sendNotificationToNoun('The ' + noun['short_desc'] + ' is now on.', holdingNoun)
            else:
                noun['on'] = 'false'
                for holdingNoun in holders:
                    self.sendNotificationToNoun('The ' + noun['short_desc'] + ' is now off.', holdingNoun)


    def lookAtNounStringFromNounWithId(self, targetNounString, sourceNounId):
        if targetNounString[0] != '$':
            # A noun was specified by the user
            visible = True
            targetNounId = self.nounIdWithShortDesc(targetNounString)
            if targetNounId != None:
                # Target noun exists
                if self.roomsContainingNounWithId(sourceNounId)[0] in self.roomsContainingNounWithId(targetNounId):
                    # And is in the same room as the source noun
                    pass
                else:
                    visible = False
            else:
                # Target noun does not exist
                visible = False
            if visible:
                self.sendNotificationToNoun(self.nounWithId(targetNounId)['long_desc'], self.nounWithId(sourceNounId))
            else:
                self.sendNotificationToNoun('You don\'t see a ' + targetNounString + ' here.', self.nounWithId(sourceNounId))
            result = visible
        else:
            # The user just typed "look"
            self.sendNotificationToNoun(self.roomTypeWithId(self.roomsContainingNounWithId(sourceNounId)[0]['type'])['long_desc'], self.nounWithId(sourceNounId))
            result = True
        return result


    def attackNounStringFromNounWithId(self, defenderNounString, attackerNounId):
        if defenderNounString[0] != '$':
            # A noun was specified by the user
            visible = True
            defenderNounId = self.nounIdWithShortDesc(defenderNounString)
            if defenderNounId != None:
                # Target noun exists
                if self.roomsContainingNounWithId(attackerNounId)[0] in self.roomsContainingNounWithId(defenderNounId):
                    # And is in the same room as the source noun
                    pass
                else:
                    visible = False
            else:
                # Target noun does not exist
                visible = False
            if visible:
                # Is the target mortal?
                defenderNoun = self.nounWithId(defenderNounId)
                if defenderNoun['mortal'] == 'true':
                    # And is it alive?
                    if defenderNoun['alive'] == 'true':
                        # And does the attacker have any weapons in their inventory?
                        attackerNoun = self.nounWithId(attackerNounId)
                        attackerIsArmed = False
                        for itemId in attackerNoun['inventory']:
                            if self.nounWithId(itemId)['weapon'] == 'true':
                                attackerIsArmed = True
                        if attackerIsArmed:
                            # Ok, target is dead
                            defenderNoun['alive'] = 'false'
                            # Run the on_death script
                            pythonString = self.expandSpecialVariablesInString(defenderNoun['on_death'], attackerNounId, 'kill', defenderNounId, 'kill')
                            self.execPythonString(pythonString)
                        else:
                            # No weapons!
                            # FIXME: Right now, the attacker simply loses if it doesn't have a weapon
                            self.sendNotificationToNoun('Since you didn\'t bring a weapon to this fight... well, you got killed.', attackerNoun)
                            self.setGameStateForNounWithId(ZerkGameState.FinishedLost, attackerNounId)
            else:
                self.sendNotificationToNoun('You don\'t see a ' + defenderNounString + ' here.', self.nounWithId(attackerNounId))
            result = visible
        else:
            # The user just typed "kill"
            self.sendNotificationToNoun('Looking to fight, eh? You\'ll need to specify a target!', self.nounWithId(attackerNounId))
            result = True
        return result


    def randomObviousExitForRoom(self, room):
        exitDir = None
        obviousExits = room['obvious_exits']
        exitList = obviousExits.split(',')
        # Iterate through all obvious exits
        if len(exitList) != 0:
            stillLooking = True
            while stillLooking:
                for exit in exitList:
                    exitDir = exit.strip()
                    # If a random check passes, choose this exit
                    if random.randrange(1,4) == 2:
                        stillLooking = False
                        break
        return exitDir


    def moveNounWithIdRandomly(self, nounId):
        result = True
        try:
            oldRoom = self.roomsContainingNounWithId(nounId)[0]
            exitDir = self.randomObviousExitForRoom(oldRoom)
            if self.moveNounWithIdThroughExit(nounId, exitDir):
                newRoom = self.roomsContainingNounWithId(nounId)[0]
                # Notify nouns in the new room
                for otherNounId in newRoom['obvious_nouns']:
                    # But only if the noun was not in the previous room
                    if otherNounId not in oldRoom['obvious_nouns']:
                        shortDesc = self.nounWithId(nounId)['short_desc']
                        self.sendNotificationToNoun('a ' + shortDesc + ' unexpectedly enters the room.', self.nounWithId(otherNounId))
            else:
                print('[DEBUG] ' + nounId + ' was unable to move ' + exitDir)
                pass
        except:
            result = False
        return result