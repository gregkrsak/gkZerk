# Filename: ZerkView.py
# Author: Greg M. Krsak
# License: MIT
# Contact: greg.krsak@gmail.com
#
# gkZerk is an Interactive Fiction (IF) style interpreter, inspired by Infocom's
# Zork series. gkZerk allows the use of custom maps, which are JSON-formatted.
#
# This file contains the MVC "view" code.
#

import io

from zerk_state import ZerkGameState


class ZerkView:
    
    def __init__(self, outputStream, model):
        self.buffer = io.StringIO()
        self.output = outputStream
        self.model = model

    
    @property
    def dictionaryForNewUser(self):
        """
        Returns a dictionary representing a new user.
        """
        newUserId = self.model.nextPlayableNounId
        if newUserId is None:
            raise ValueError("No playable noun found in the map.")
        return self.model.nounWithId(newUserId)


    def indefiniteArticleForWord(self, word):
        result = 'a'
        if word[0] == 'a':
            result = 'an'
        if word[0] == 'e':
            result = 'an'
        if word[0] == 'i':
            result = 'an'
        if word[0] == 'o':
            result = 'an'
        if word[0] == 'u':
            result = 'an'
        return result

    
    def renderWelcomeBanner(self):
        endl = '\n'
        self.buffer.write('gkZerk, an iteractive fiction interpreter' + endl)
        self.buffer.write('Copyright (c) 2013 Greg M. Krsak (greg.krsak@gmail.com)' + endl)
        self.buffer.write('Provided under the MIT License: http://opensource.org/licenses/MIT' + endl)
        self.buffer.write(endl)
        self.buffer.write('Entering map \'' + self.model.about['title'] + '\' (' + self.model.about['version'] + ') by ' + self.model.about['author'] + ' . . .' + endl)
        self.buffer.write(endl)
    
    
    def renderRoom(self, room):
        endl = '\n'
        roomType = self.model.roomTypeWithId(room['type'])
        # Is it dark?
        if room['lit'] == 'true':
            # Short description
            self.buffer.write(roomType['short_desc'] + endl)
            # Long description
            self.buffer.write(roomType['long_desc'] + endl)
            # Obvious nouns
            for nounId in (room['obvious_nouns']):
                noun = self.model.nounWithId(nounId)
                friendlyNoun = noun['short_desc']
                indefiniteArticle = self.indefiniteArticleForWord(friendlyNoun)
                self.buffer.write(indefiniteArticle + ' ' + friendlyNoun + ' is here')
                # Is this noun mortal?
                if noun['mortal'] == 'true':
                    # Is it dead?
                    if noun['alive'] == 'false':
                        self.buffer.write(' (dead)')
                self.buffer.write(endl)
            # Obvious exits
            exitsString = 'Obvious exits:'
            obviousExits = room['obvious_exits']
            if len(obviousExits) != 0:
                # Re-list and re-comma the list of obvious exits
                for exit in (obviousExits.split(',')):
                    friendlyExit = exit.strip()
                    exitsString += ' ' + friendlyExit + ','
            lastChar = exitsString[-1]
            if lastChar == ':':
                # No obvious exits exist
                exitsString += ' (none)'
            elif lastChar == ',':
                # Obvious exits exist; remove trailing comma from list of exits
                exitsString = exitsString[:-1]
            self.buffer.write(exitsString)
        else:
            # Oh, it's dark
            self.buffer.write('It is very dark. You are likely to be eaten by a grue.')
        self.buffer.write(endl)

                
    def renderInputPromptForNounId(self, nounId):
        sep = ' '
        self.buffer.write('[')
        noun = self.model.nounWithId(nounId)
        self.buffer.write(nounId)
        self.buffer.write(sep)
        self.buffer.write('score:')
        self.buffer.write(noun['score'])
        self.buffer.write(sep)
        self.buffer.write('turn:')
        self.buffer.write(noun['turns_taken'])
        self.buffer.write(']')
        self.buffer.write(sep)
    
    
    def renderVictoryMessageForNounId(self, nounId):
        endl = '\n'
        self.buffer.write(endl + endl + '*** YOU HAVE WON ***' + endl + endl)
        self.buffer.write('Through courage, heroism, thick and thin, and also perhaps a touch of sheer boredom, you (and only you) have emerged victorious. Congratulations.' + endl)
        self.buffer.write('By the way, your final score was ' + self.model.nounWithId(nounId)['score'] + '.' + endl)
        self.buffer.write(endl + 'Thanks for playing!' + endl)
    
    
    def renderDefeatMessageForNounId(self, nounId):
        endl = '\n'
        self.buffer.write(endl + endl + '*** YOU HAVE DIED ***' + endl + endl)
        self.buffer.write('Few adventurers have come this far. And, actually, many more will probably go further.' + endl)
        self.buffer.write('By the way, your final score was ' + self.model.nounWithId(nounId)['score'] + '.' + endl)
        self.buffer.write(endl + 'Thanks for playing!' + endl)
    
    
    def renderNotificationsForNounId(self, nounId):
        endl = '\n'
        noun = self.model.nounWithId(nounId)
        for message in (noun['notifications']):
            self.buffer.write(message + endl)
        noun['notifications'] = [ ]
        self.buffer.write(endl)
    

    def waitingOutput(self):
        result = self.buffer.getvalue()
        self.buffer.truncate(0)
        return result