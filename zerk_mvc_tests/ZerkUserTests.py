# Filename: ZerkUserTests.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# Zerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. Zerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the tests for the ZerkUser.
#

import unittest
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


class ZerkUserTests(unittest.TestCase):
  
    """
    Tests for ZerkUser.
    """
  
    def setUp(self):
        # Define a mock input
        self.mockInput = io.StringIO('mock input')
        # Define the local console
        self.localOutput = sys.stdout
        # Create a mock model instance
        self.mockModel = ZerkModel({"nouns":[{
                                   "id": "player_001",
                                   "active": "false",
                                   "playable": "true",
                                   "connected": "false",
                                   "turns_taken": "0",
                                   "turns_allowed": "100",
                                   "score": "0",
                                   "switchable": "false",
                                   "short_desc": "mock short description",
                                   "long_desc": "mock long description",
                                   "before_each_turn": "print('mock before_each_turn')",
                                   "after_each_turn": "print('mock after_each_turn')",
                                   "verbs": []
                                    }]})
        # Create a user instance (containing a mock view and mock controller)
        self.user = ZerkUser(ZerkView(self.localOutput, self.mockModel), ZerkController(self.mockInput, self.mockModel))


  # (currently no tests for this unit)
