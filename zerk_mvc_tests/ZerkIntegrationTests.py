# Filename: ZerkIntegrationTests.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# Zerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. Zerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the tests that verify the Model, View, Controller,
# and User are working together.
#

import unittest
import json
import io

# Ref: http://stackoverflow.com/questions/1054271/how-to-import-a-python-class-that-is-in-a-directory-above
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from zerk_mvc.ZerkModel import ZerkModel
from zerk_mvc.ZerkView import ZerkView
from zerk_mvc.ZerkController import ZerkController
from zerk_mvc.ZerkUser import ZerkUser
from zerk_state import ZerkGameState


class ZerkIntegrationTests(unittest.TestCase):
  
    """
    Tests an integrated environment of Model, View, Controller, and User.
    """
  
    def setUp(self):
        """
        Run before each test.
        """
        # Form a filename for the Zerk map and open the file
        mapFilename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test-map.json'))
        jsonString = open(mapFilename).read()
        # Parse the JSON from the file
        map = json.loads(jsonString)
        # Define a mock input
        self.mockInput = io.StringIO('take lantern')
        # Define the local console
        self.localConsole = sys.stdout
        # Create a model instance (shared by all users)
        self.model = ZerkModel(map)
        # Create a view instance (attached to a local console and the model)
        self.view = ZerkView(self.localConsole, self.model)
        # Create a controller instance (attached to a mock input and the model)
        self.controller = ZerkController(self.mockInput, self.model)
        # Create a user instance (attached to the view and controller)
        self.user = ZerkUser(self.view, self.controller)
        # Connect the user instance to the shared model
        self.user.connect()
    
    
    def tearDown(self):
        """
        Run after each test.
        """
        # Disconnect the user instance to the shared model
        self.user.disconnect();
    

    def test_CallBySharingArchitectureCheck(self):
        """
        Verifies that a user can integrate with the MVC components.
        """
        # Get what would amount to the user's ID from model, view, and user
        modelsPerspective = self.model.nextPlayableNounId
        viewsPerspective = self.user.view.dictionaryForNewUser['id']
        usersPerspective = self.user.data['id']
        everyoneAgrees = (modelsPerspective == viewsPerspective == usersPerspective == 'player_001')
        # User's ID should be 'player_001'
        self.assertTrue(everyoneAgrees)
        # Change the user's ID to 'player_002'
        self.model.nounWithId('player_001')['id'] = 'player_002'
        # Get what would amount to the user's ID from model, view, and user
        modelsPerspective = self.model.nextPlayableNounId
        viewsPerspective = self.user.view.dictionaryForNewUser['id']
        usersPerspective = self.user.data['id']
        everyoneStillAgrees = (modelsPerspective == viewsPerspective == usersPerspective == 'player_002')
        # User's ID should now be 'player_002'
        self.assertTrue(everyoneStillAgrees)

            
    def test_ViewCanGetNewUserDictionaryFromModel(self):
        """
        Verifies that a view can retrieve data from, the model, which
        would then be passed to a new user.
        """
        userData = self.view.dictionaryForNewUser
        self.assertEqual(userData['id'], 'player_001')
    
    
    def test_ViewCanRenderWhileStarting(self):
        """
        Does the proper view show while starting?
        """
        self.user.gameState = ZerkGameState.Starting
        print('\n')
        self.user.transmit()
        print()
    
    
    def test_ViewCanRenderWhilePlaying(self):
        """
        Does the proper view show while playing?
        """
        self.user.gameState = ZerkGameState.Playing
        self.model.sendNotificationToNoun('You have received a mock notification', self.model.nounWithId(self.user.data['id']))
        print('\n')
        self.user.transmit()
        print()
    
    
    def test_ViewCanRenderWhileFinishedWon(self):
        """
        Does the proper view show when the user has won?
        """
        self.user.gameState = ZerkGameState.FinishedWon
        noun = self.model.nounWithId('player_001')
        self.model.sendNotificationToNoun(noun['id'] + ' has won the game.', noun)
        print('\n')
        self.user.transmit()
        print()
    
    
    def test_ViewCanRenderWhileFinishedLost(self):
        """
        Does the proper view show when the user has lost?
        """
        self.user.gameState = ZerkGameState.FinishedLost
        noun = self.model.nounWithId('player_001')
        self.model.sendNotificationToNoun(noun['id'] + ' has won the game.', noun)
        print('\n')
        self.user.transmit()
        print()

    
    def test_UserCanConnectToModelViaController(self):
        """
        Verifies the user can send a connect request to the controller, and from
        there to the model.
        """
        self.user.connect()
        # Verify with raw map data
        self.assertEqual('true', self.model.nounWithId('player_001')['connected'])
    
    
    def test_UserCanDisconnectFromModelViaController(self):
        """
        Verifies the user can send a disconnect request to the controller, and from
        there to the model.
        """
        self.user.disconnect()
        # Verify with raw map data
        self.assertEqual('false', self.model.nounWithId('player_001')['connected'])
    

    def test_UserCanPassGameStateToModelViaController(self):
        """
        In this test, the user's gameState property is set. This should trigger
        a handoff to the controller, and from there to the model.
        """
        # Let's say we've just started playing...
        self.user.gameState = ZerkGameState.Playing
        # The model should now contain the string 'playing' in the raw map data
        self.assertEqual('playing', self.model.nounWithId('player_001')['game_state'])
        # And the model should report ZerkGameState.Playing via the standard getter
        self.assertEqual(ZerkGameState.Playing, self.model.gameStateForNounWithId('player_001'))


    def test_ControllerCanParseCommand(self):
        """
        This test ensures the controller can take the proper game actions based
        on a user-like command.
        """
        self.controller.setGameStateForUserWithId(ZerkGameState.Playing, self.user.data['id'])
        input = self.controller.waitForInput()
        self.controller.parseCommandFromNounWithId(input, self.user.data['id'])
