import unittest
import json

# Ref: http://stackoverflow.com/questions/1054271/how-to-import-a-python-class-that-is-in-a-directory-above
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from zerk_mvc.ZerkModel import ZerkModel
from zerk_state import ZerkGameState


class ZerkModelTests(unittest.TestCase):
    
    def setUp(self):
        mapFilename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testmap.json'))
        jsonString = open(mapFilename).read()
        map = json.loads(jsonString)
        self.model = ZerkModel(map)
    
    def test_CanAccessMapZerkTag(self):
        self.assertEqual(self.model.idString, 'map')
    
    def test_CanAccessMapAbout(self):
        self.assertEqual(self.model.about['author'], 'Greg M. Krsak')
    
    def test_CanAccessMapVersion(self):
        self.assertEqual(self.model.version, '1')

    def test_CanAccessMapRoomType(self):
        self.assertEqual(self.model.roomTypes[0]['id'], 'BasicRoom')

    def test_CanAccessMapRoom(self):
        self.assertEqual(self.model.rooms[0]['id'], 'room_001')

    def test_CanAccessMapNoun(self):
        self.assertEqual(self.model.nouns[0]['id'], 'light_001')

    def test_CanAccessMapVerb(self):
        self.assertEqual(self.model.verbs[0]['id'], 'north')
    
    def test_CanFindMapRoomById(self):
        self.assertEqual(self.model.roomWithId('room_001')['id'], 'room_001')
    
    def test_CanFindMapRoomTypeById(self):
        self.assertEqual(self.model.roomTypeWithId('BasicRoom')['id'], 'BasicRoom')
    
    def test_CanIndirectlyAccessMapRoomTypeFromRoom(self):
        room = self.model.rooms[0]
        typeId = room['type']
        roomType = self.model.roomTypeWithId(typeId)
        self.assertEqual(roomType['short_desc'], 'Simple room')

    def test_CanIndirectlyAccessMapRoomFromRoom(self):
        room = self.model.roomWithId('room_001')
        nextRoomId = room['exit_n']
        nextRoom = self.model.roomWithId(nextRoomId)
        self.assertEqual(nextRoom['id'], 'room_002')

    def test_CanFindMapNounById(self):
        noun = self.model.nounWithId('light_001')
        self.assertEqual(noun['short_desc'], 'lantern')

    def test_CanFindMapNounIdByShortDesc(self):
        nounId = self.model.nounIdWithShortDesc('lantern')
        self.assertEqual('light_001', nounId)
    
    def test_CanExpandSpecialVariablesInString(self):
        pythonString = self.model.expandSpecialVariablesInString('sourceNounId=\'${SOURCE_NOUN_ID}\' verbId=\'${VERB_ID}\' targetNounId=\'${TARGET_NOUN_ID}\' targetNounString=\'${TARGET_NOUN_STRING}\'', 'player_001', self.model.verbs[6]['id'], 'light_001', 'light_001')
        #success = self.model.execPythonString(pythonString)
        #self.assertTrue(success)
        print(pythonString)
    
    def test_CanExecPythonString(self):
        pythonString = 'print(\'Hello, World!\')'
        success = self.model.execPythonString(pythonString)
        self.assertTrue(success)

    def test_CanExecPythonString_Negative(self):
        pythonString = 'blah'
        success = self.model.execPythonString(pythonString)
        self.assertFalse(success)

    def test_CanFindAllRoomsContainingNounWithId(self):
        nounId = 'light_001'
        roomsWithKey = self.model.roomsContainingNounWithId(nounId)
        for room in (roomsWithKey):
            self.assertEqual(room['id'], 'room_001')

    def test_CanAdjustLightingInRoomWithId(self):
        roomId = 'room_001'
        self.assertEqual(self.model.roomWithId(roomId)['lit'], 'true')
        self.model.setLitInRoomWithId(roomId, False)
        self.assertEqual(self.model.roomWithId(roomId)['lit'], 'false')

    def test_CanScriptLightingInRoom(self):
        self.model.roomWithId('room_001')['always_lit'] = 'false'
        # Lights are on
        self.assertEqual(self.model.roomWithId('room_001')['lit'], 'true')
        # Run lantern script (the lantern used in this script is switched off)
        pythonString = self.model.nounWithId('light_001')['before_each_turn']
        noExceptionThrown = self.model.execPythonString(pythonString)
        self.assertTrue(noExceptionThrown)
        # Lights are off
        self.assertEqual(self.model.roomWithId('room_001')['lit'], 'false')

    def test_CanGetAvailablePlayableNounId(self):
        playableNounId = self.model.nextPlayableNounId
        self.assertEqual(playableNounId, 'player_001')

    def test_CanSetGameStateForNounWithId(self):
        nounId = 'player_001'
        self.model.setGameStateForNounWithId(ZerkGameState.Starting, nounId)
        self.assertEqual(self.model.gameStateForNounWithId(nounId), ZerkGameState.Starting)

    def test_CanMoveNounWithIdThroughExitWithRequiredItem_Negative(self):
        nounId = 'player_001'
        exitDir = 'n'
        self.assertEqual(self.model.roomsContainingNounWithId(nounId)[0]['id'], 'room_001')
        self.model.moveNounWithIdThroughExit(nounId, exitDir)
        self.assertEqual(self.model.roomsContainingNounWithId(nounId)[0]['id'], 'room_001')

    def test_CanRemoveNounWithIdFromRoomWithId(self):
        nounId = 'player_001'
        roomId = 'room_001'
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 1)
        self.model.removeNounWithIdFromRoomWithId(nounId, roomId)
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 0)

    def test_CanAddNounWithIdToRoomWithId(self):
        nounId = 'player_001'
        roomId = 'room_002'
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 1)
        self.model.addNounWithIdToRoomWithId(nounId, roomId)
        self.assertEqual(len(self.model.roomsContainingNounWithId('player_001')), 2)

    def test_CanSendNotificationToNoun(self):
        message = 'test message'
        noun = self.model.nounWithId('player_001')
        noun['connected'] = 'true'
        success = self.model.sendNotificationToNoun(message, noun)
        self.assertTrue(success)
        self.assertEqual(noun['notifications'][0], message)

    def test_CanAddNounWithIdToInventoryOfNounWithId(self):
        sourceNounId = 'light_001'
        targetNounId = 'player_001'
        targetNoun = self.model.nounWithId(targetNounId)
        self.assertFalse(sourceNounId in targetNoun['inventory'])
        self.model.addNounWithIdToInventoryOfNounWithId(sourceNounId, targetNounId)
        self.assertTrue(sourceNounId in targetNoun['inventory'])

    def test_CanRemoveNounWithIdFromInventoryOfNounWithId(self):
        sourceNounId = 'light_001'
        targetNounId = 'player_001'
        targetNoun = self.model.nounWithId(targetNounId)
        self.model.addNounWithIdToInventoryOfNounWithId(sourceNounId, targetNounId)
        self.assertTrue(sourceNounId in targetNoun['inventory'])
        self.model.removeNounWithIdFromInventoryOfNounWithId(sourceNounId, targetNounId)
        self.assertFalse(sourceNounId in targetNoun['inventory'])

    def test_CanSwitchNounWithId(self):
        sourceNounId = 'light_001'
        targetNounId = 'player_001'
        self.model.addNounWithIdToInventoryOfNounWithId(sourceNounId, targetNounId)
        self.assertEqual(self.model.nounWithId('light_001')['on'], 'false')
        self.model.switchNounWithId('light_001')
        self.assertEqual(self.model.nounWithId('light_001')['on'], 'true')

    def test_CanLookAtNounStringFromNounId(self):
        sourceNounId = 'player_001'
        targetNounString = 'key'
        success = self.model.lookAtNounStringFromNounWithId(targetNounString, sourceNounId)
        self.assertTrue(success)

    def test_CanAttackNounStringFromNounWithId(self):
        sourceNounId = 'player_001'
        targetNounString = 'thief'
        self.model.attackNounStringFromNounWithId(targetNounString, sourceNounId)
        self.assertEqual('false', self.model.nounWithId('npc_001')['alive'])

    def test_CanGenerateRandomObviousExitForRoom(self):
        room = self.model.roomWithId('room_001')
        exitDir = self.model.randomObviousExitForRoom(room)
        self.assertEqual('n', exitDir)

    def test_CanMoveNounWithIdRandomly(self):
        nounId = 'npc_001'
        success = self.model.moveNounWithIdRandomly(nounId)
        self.assertTrue(success)
