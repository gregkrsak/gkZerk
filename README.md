gkZerk: The Great Work-in-Progress
==============


[![Python](https://img.shields.io/badge/language-python-blue.svg)](https://github.com/gregkrsak/gkZerk/blob/master/gkzerk.py)


This is an interactive fiction (IF) interpreter that I wrote for a class project. It was inspired by Infocom's IF adventure games (especially the Zork series). Traditionally, IF games are all-text, and gkZerk is no exception. It's like reading a book, only it's a game.

Try it out
----------

You'll need a Python 3 interpreter.

* [Download Python]

Once you have that, it's pretty simple:

```
gkzerk.py tutorial-map.json
```

Make your own maps
------------------

gkZerk is just a framework, and that means your actual experience isn't tied to my code. The levels (or "maps") in the game are actually loaded from a text file that's in JSON format.

Here's the basic structure of a gkZerk map (For those of you familiar with IF, these map files are not the traditional Z-code structure of most IF games):

```javascript
{
  "zerk": "map",
  "version": "1",
  "about": {
    "title": "Your map's title",
    "author": "Your name",
    "version": "your-maps-version-string"
  },
  "rooms": [ . . . ],
  "room_types": [ . . . ],
  "nouns": [ . . . ],
  "verbs": [ . . . ]
}
``` 

Where the keys "rooms", "room_types", "nouns", and "verbs" each contain a list of objects.

An example of a verb object:

```javascript
{
    "id": "take",
    "immediately": "self.addNounWithIdToInventoryOfNounWithId('${TARGET_NOUN_ID}', '${SOURCE_NOUN_ID}'); self.removeNounWithIdFromRoomWithId('${TARGET_NOUN_ID}', self.roomsContainingNounWithId('${SOURCE_NOUN_ID}')[0]['id']) if self.nounWithId('${TARGET_NOUN_ID}')['big'] == 'false' else self.sendNotificationToNoun('You can\\'t pick that up!', self.nounWithId('${SOURCE_NOUN_ID}'))",
    "synonyms": [
        "get",
        "grab",
        "acquire",
        "hold"
    ]
}
```

An example of a noun object:

```javascript
{
    "id": "light_001",
    "active": "true",
    "playable": "false",
    "switchable": "true",
    "mortal": "false",
    "big": "false",
    "weapon": "false",
    "on": "false",
    "short_desc": "lantern",
    "long_desc": "This 12 volt Eveready is always ready.",
    "before_each_turn": "for room in (self.roomsContainingNounWithId('light_001')): self.setLitInRoomWithId(room['id'], False) if (self.nounWithId('light_001')['on'] == 'false') and (room['always_lit'] == 'false') else self.setLitInRoomWithId(room['id'], True)",
    "after_each_turn": "",
    "on_take": "self.nounWithId('${SOURCE_NOUN_ID}')['score'] = str(int(self.nounWithId('${SOURCE_NOUN_ID}')['score']) + 5)",
    "on_drop": "",
    "inventory": [],
    "allowed_verbs": [
        "take",
        "drop",
        "use"
    ]
}
```

An example of a room_type object:

```javascript
{
    "id": "OutsideEntry",
    "short_desc": "Front Porch",
    "long_desc": "Blowing snow assaults your morale as you attempt to stay warm on the front porch of a large building. It looks as if the residence was constructed methodically, in the middle of an evergreen forest, with no obvious roads in sight. Well, at least you don't feel trapped inside of that silly house anymore. That silly, warm house. Ah, what fun it was."
}
```

An example of a room object:

```javascript
{
    "id": "outside_001",
    "type": "OutsideEntry",
    "always_lit": "true",
    "lit": "true",
    "obvious_exits": "s",
    "exit_s": "room_005",
    "on_entry": "self.nounWithId('${SOURCE_NOUN_ID}')['score'] = str(int(self.nounWithId('${SOURCE_NOUN_ID}')['score']) + 10); self.nounWithId('${SOURCE_NOUN_ID}')['game_state'] = 'finished_won'",
    "obvious_nouns": [],
    "requires_nouns": [
        "key_001"
    ]
}
```

You've probably noticed that there's some scripting allowed; in-fact, it's required for a reasonably-functioning map! All scripts are Python 3, executed within a server-side instance (shared among all users) of the ZerkModel class. Note that, as of right now, the program is hard-coded to only connect a single, local user. So, you'll be playing by yourself!

To learn more about the map design, go ahead and dive into the file tutorial-map.json!

Additional resources
--------------------

* [How do I use Git?]

* [Download GitHub Desktop for Windows or Mac]

* [Download Git for Linux]

* http://en.wikipedia.org/wiki/Interactive_fiction

* http://en.wikipedia.org/wiki/Test-driven_development

* http://en.wikipedia.org/wiki/Git_(software)

* http://en.wikipedia.org/wiki/JSON

  [Download Python]: https://www.python.org/downloads/
  [How do I use Git?]: http://git-scm.com/documentation
  [Download GitHub Desktop for Windows or Mac]: https://desktop.github.com/
  [Download Git for Linux]: http://git-scm.com/download/linux

