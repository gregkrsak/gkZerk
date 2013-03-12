# Filename: ZerkModelTests.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# Zerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. Zerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the tests for the MVC model.
#

import unittest
import json

# Ref: http://stackoverflow.com/questions/1054271/how-to-import-a-python-class-that-is-in-a-directory-above
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from zerk_mvc.ZerkModel import ZerkModel
from zerk_state import ZerkGameState


class ZerkModelTests(unittest.TestCase):
  
    """
    Tests for the MVC model.
    """
  
    def setUp(self):
        mapFilename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test-map.json'))
        jsonString = open(mapFilename).read()
        map = json.loads(jsonString)
        self.model = ZerkModel(map)
  
  
    def test_CanAccessMapZerkTag(self):
        """
        Can access the zerk identification tag.
        """
        self.assertEqual(self.model.idString, 'map')
  
  
    def test_CanAccessMapAbout(self):
        """
        Can access the map about object.
        """
        self.assertEqual(self.model.about['author'], 'Greg M. Krsak')
  
  
    def test_CanAccessMapVersion(self):
        """
        Can access the zerk version string.
        """
        self.assertEqual(self.model.version, '1')

  
    def test_CanAccessRoomType(self):
        """
        Can access a room_type object.
        """
        self.assertEqual(self.model.roomTypes[0]['id'], 'OutsideEntry')

  
    def test_CanAccessRoom(self):
        """
        Can access a room object.
        """
        self.assertEqual(self.model.rooms[0]['id'], 'outside_001')

  
    def test_CanAccessNoun(self):
        """
        Can access a noun object.
        """
        self.assertEqual(self.model.nouns[0]['id'], 'light_001')

  
    def test_CanAccessVerb(self):
        """
        Can access a verb object.
        """
        self.assertEqual(self.model.verbs[0]['id'], 'north')
  
  
    def test_CanFindRoomById(self):
        """
        Can search for a room object by its id.
        """
        self.assertEqual(self.model.roomWithId('room_001')['id'], 'room_001')
  
  
    def test_CanFindRoomTypeById(self):
        """
        Can return the room_type object with the specified id.
        """
        self.assertEqual(self.model.roomTypeWithId('OutsideEntry')['id'], 'OutsideEntry')
  
    
    def test_CanIndirectlyAccessRoomTypeFromRoom(self):
        """
        Can access the room_type object pointed to by a room.
        """
        room = self.model.rooms[0]
        typeId = room['type']
        roomType = self.model.roomTypeWithId(typeId)
        self.assertEqual(roomType['short_desc'], 'Front Porch')

  
    def test_CanIndirectlyAccessRoomFromRoom(self):
        """
        Can access the room object pointed to by another room's exit.
        """
        # The 'd' (down) exit of room_001...
        room = self.model.roomWithId('room_001')
        nextRoomId = room['exit_d']
        nextRoom = self.model.roomWithId(nextRoomId)
        # Should point to room_002
        self.assertEqual(nextRoom['id'], 'room_002')

  
    def test_CanFindNounById(self):
        """
        Can search for a noun object by its id.
        """
        # The short description of light_001 should be 'lantern'
        noun = self.model.nounWithId('light_001')
        self.assertEqual(noun['short_desc'], 'lantern')

  
    def test_CanFindNounIdByShortDesc(self):
        """
        Can search for a noun object by its short description.
        """
        # The id of the noun with the short description 'lantern' should
        # be 'light_001' 
        nounId = self.model.nounIdWithShortDesc('lantern')
        self.assertEqual('light_001', nounId)
  
  
    def test_CanExpandSpecialVariablesInString(self):
        """
        Can detect and expand special variables:
          ${SOURCE_NOUN_ID}
          ${VERB_ID}
          ${TARGET_NOUN_ID}
          ${TARGET_NOUN_STRING}
        """
        pythonString = self.model.expandSpecialVariablesInString('${SOURCE_NOUN_ID}${VERB_ID}${TARGET_NOUN_ID}${TARGET_NOUN_STRING}', 'player_001', self.model.verbs[6]['id'], 'light_001', 'light_001')
        self.assertEqual('player_001' + self.model.verbs[6]['id'] + 'light_001' + 'light_001', pythonString)
  
  
    def test_CanExecPythonString(self):
        """
        Can detect success when executing valid Python.
        """
        pythonString = 'x = 3'
        success = self.model.execPythonString(pythonString)
        self.assertTrue(success)

  
    def test_CanExecPythonString_Negative(self):
        """
        Can detect failure when executing invalid Python.
        """
        pythonString = 'blah'
        success = self.model.execPythonString(pythonString)
        self.assertFalse(success)

          
    def test_CanFindAllRoomsContainingNounWithId(self):
        """
        Can return a list of rooms containing a specific noun.
        """
        # Search for the lantern 
        nounId = 'light_001'
        roomsWithLantern = self.model.roomsContainingNounWithId(nounId)
        # It should only be in room_003
        for room in (roomsWithLantern):
            self.assertEqual(room['id'], 'room_003')


    def test_CanAdjustLightingInRoomWithId(self):
        """
        Can force the lighting in a room from 'lit' to 'unlit'.
        """
        roomId = 'room_001'
        # Room is lit
        self.assertEqual(self.model.roomWithId(roomId)['lit'], 'true')
        # Force lights to off
        self.model.setLitInRoomWithId(roomId, False)
        # Room should be dark
        self.assertEqual(self.model.roomWithId(roomId)['lit'], 'false')

  
    def test_CanScriptLightingInRoom(self):
        """
        Can use a light to change a room from 'unlit' to 'lit'.
        """
        self.model.roomWithId('room_003')['always_lit'] = 'false'
        # Lights are on
        self.assertEqual(self.model.roomWithId('room_003')['lit'], 'true')
        # Run lantern script (the lantern used in this script is switched off)
        pythonString = self.model.nounWithId('light_001')['before_each_turn']
        noExceptionThrown = self.model.execPythonString(pythonString)
        self.assertTrue(noExceptionThrown)
        # Lights are off
        self.assertEqual(self.model.roomWithId('room_003')['lit'], 'false')

  
    def test_CanGetAvailablePlayableNounId(self):
        """
        Can search for the first noun id that's associated with a noun
        which has (1) its 'playable' key set to 'true', and (2) is not
        already associated with a connected user.
        """
        playableNounId = self.model.nextPlayableNounId
        self.assertEqual(playableNounId, 'player_001')

  
    def test_CanSetGameStateForNounWithId(self):
        """
        Can set the game state for a playable noun.
        """
        nounId = 'player_001'
        self.model.setGameStateForNounWithId(ZerkGameState.Starting, nounId)
        self.assertEqual(self.model.gameStateForNounWithId(nounId), ZerkGameState.Starting)

  
    def test_CanMoveNounWithIdThroughExitWithRequiredItem_Negative(self):
        """
        A noun can NOT move through an exit unless carrying all required
        items.
        """
        # Setup: Remove the player from the bedroom; add the player to
        # the entry hall (inside of the locked door).
        nounId = 'player_001'
        self.model.removeNounWithIdFromRoomWithId(nounId, 'room_001')
        self.model.addNounWithIdToRoomWithId(nounId, 'room_005')
        # Setup: Player is going to attempt to move 'n' (north) through
        # a locked door.
        exitDir = 'n'
        # Player should be in the entry hall
        self.assertEqual(self.model.roomsContainingNounWithId(nounId)[0]['id'], 'room_005')
        # Attempt to move through the locked door, without the key
        self.model.moveNounWithIdThroughExit(nounId, exitDir)
        # Player should still be in the entry hall
        self.assertEqual(self.model.roomsContainingNounWithId(nounId)[0]['id'], 'room_005')

  
    def test_CanRemoveNounWithIdFromRoomWithId(self):
        """
        Can remove a noun from a room.
        """
        nounId = 'player_001'
        roomId = 'room_001'
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 1)
        self.model.removeNounWithIdFromRoomWithId(nounId, roomId)
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 0)


    def test_CanAddNounWithIdToRoomWithId(self):
        """
        Can add a noun to a room.
        """
        nounId = 'player_001'
        roomId = 'room_002'
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 1)
        self.model.addNounWithIdToRoomWithId(nounId, roomId)
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 2)

          
    def test_CanSendNotificationToNoun(self):
        """
        Can send a message to a connected, playable noun.
        """
        message = 'test message'
        # Setup: Simulate the player is connected
        noun = self.model.nounWithId('player_001')
        noun['connected'] = 'true'
        # Send the notification and verify it didn't immediately fail
        success = self.model.sendNotificationToNoun(message, noun)
        self.assertTrue(success)
        # Player should now have this message in their notifications
        self.assertEqual(noun['notifications'][0], message)

          
    def test_CanAddNounWithIdToInventoryOfNounWithId(self):
        """
        Can add a noun to the inventory of another noun.
        """
        # Setup: Prepare to give the player the lantern
        sourceNounId = 'light_001'
        targetNounId = 'player_001'
        targetNoun = self.model.nounWithId(targetNounId)
        # Player should not yet have the lantern
        self.assertFalse(sourceNounId in targetNoun['inventory'])
        # Give the player the lantern
        self.model.addNounWithIdToInventoryOfNounWithId(sourceNounId, targetNounId)
        # Player should now have the lantern
        self.assertTrue(sourceNounId in targetNoun['inventory'])

  
    def test_CanRemoveNounWithIdFromInventoryOfNounWithId(self):
        """
        Can remove a noun from the inventory of another noun.
        """
        sourceNounId = 'light_001'
        targetNounId = 'player_001'
        targetNoun = self.model.nounWithId(targetNounId)
        self.model.addNounWithIdToInventoryOfNounWithId(sourceNounId, targetNounId)
        self.assertTrue(sourceNounId in targetNoun['inventory'])
        self.model.removeNounWithIdFromInventoryOfNounWithId(sourceNounId, targetNounId)
        self.assertFalse(sourceNounId in targetNoun['inventory'])

  
    def test_CanSwitchNounWithId(self):
        """
        When given an 'off' noun, player can switch it to 'on'.
        """
        # Setup: Player needs a lantern
        sourceNounId = 'light_001'
        targetNounId = 'player_001'
        self.model.addNounWithIdToInventoryOfNounWithId(sourceNounId, targetNounId)
        # Lantern should be off
        self.assertEqual(self.model.nounWithId('light_001')['on'], 'false')
        # Use lantern
        self.model.switchNounWithId('light_001')
        # Lantern should now be on
        self.assertEqual(self.model.nounWithId('light_001')['on'], 'true')

  
    def test_CanLookAtNounStringFromNounId(self):
        """
        Player can look at a noun.
        """
        # Player looks at the bedroom pillow
        sourceNounId = 'player_001'
        targetNounString = 'pillow'
        success = self.model.lookAtNounStringFromNounWithId(targetNounString, sourceNounId)
        self.assertTrue(success)

  
    def test_CanAttackNounStringFromNounWithId(self):
        """
        When given a weapon, player can attack and kill a mortal noun.
        """
        # Setup: player needs a weapon 
        self.model.addNounWithIdToInventoryOfNounWithId('weapon_001', 'player_001')
        # Player attacks the thief 
        sourceNounId = 'player_001'
        targetNounString = 'thief'
        self.model.attackNounStringFromNounWithId(targetNounString, sourceNounId)
        # Thief should be dead
        self.assertEqual('false', self.model.nounWithId('player_002')['alive'])

  
    def test_CanGenerateRandomObviousExitForRoom(self):
        """
        Can select a valid and obvious exit for a room, randomly.
        """
        # room_001 should only return 'd' (down) as a valid exit
        room = self.model.roomWithId('room_001')
        exitDir = self.model.randomObviousExitForRoom(room)
        self.assertEqual('d', exitDir)
  

    def test_CanMoveNounWithIdRandomly(self):
        """
        Can move a noun randomly, through a valid exit.
        """
        # Move the thief randomly
        nounId = 'player_002'
        success = self.model.moveNounWithIdRandomly(nounId)
        self.assertTrue(success)
