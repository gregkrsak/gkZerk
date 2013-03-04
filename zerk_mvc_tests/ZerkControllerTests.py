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


class ZerkControllerTests(unittest.TestCase):
    
    def setUp(self):
        # Define a mock input
        self.mockInput = io.StringIO('mock input')
        # Create a mock model instance
        self.mockModel = ZerkModel({})
        # Create a controller instance
        self.controller = ZerkController(self.mockInput, self.mockModel)


    def test_CanReceiveInputFromStream(self):
        self.assertEqual('mock input', self.controller.waitForInput())
