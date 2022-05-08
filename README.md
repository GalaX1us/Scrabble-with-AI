# Scrabble with AI
This is a complete Scrabble game with AI and GUI

This project was originally a school project that I developed on my own. That's why you won't find any class or data structures in the code because they were not allowed.
The school project itself required very little in the way of rules. But I didn't like the idea of making a half-finished game, so I preferred to respect the rules in their entirety and even add some cool features.

This Scrabble game can be played in two different ways: 
  - in the terminal (part of the school projet)
  - with a GUI (on my own)

This program respects 100% of the rules of scrabble including :
  - the way in which the players' turn is managed
  - verification of the validity of the word placement on the board
  - the way points are counted and bonuses

NB : Here I use the French dictionary

# Additional features :
In addition to the basic rules and functionalities of Scrabble I personally added some options that I found useful.

  - The ability to save games along the way to a save file so you can pick up the game later where it left off
  - You can activate on each player (human) the "developer mode" which allows to have access to additional features during the games :
    - to forcefully end the game
    - change your hand at will
    - force the placement of a word even if it is not considered valid
  - I have added the possibility to add up to 4 AI to fill the 4 available places (2 human 2 AI for example).
  - At the beginning of the game each AI can be set on 2 different difficulties (Normal, Extreme). it's quite funny to be able to watch a game with 4 AI.
  - At each turn, the players (human) can ask for help from the game. You can ask for two different types of help: 
    - a random word that you can put from the words in your hand and from the words on the board.
    - the best word that can be put (the one that gives the most points).

# How to play
  - Lauch main.py to play in the terminal
  - Lauch AffichageGraphique.py to play with the GUI

# Ways to improve
Here are the things to do to have a better game and a better code :
  - create classes to have a cleaner and more readable code (I wish i could ^^)
  - use more advanced data structures to improve the overall complexity of the program. Priority queues for the ranking of the highest scoring words for example.
  - partitioning of possible word searches to improve AI speed and word placement assistance ()
  - improve the update of the game board in GUI mode to avoid flickering
  - make an executable file

# Screenshots of the game
**Main menu:**

![image](https://user-images.githubusercontent.com/75265945/167265180-f13690ec-2fd1-4ffe-814b-10b9d5912f4e.png)

**Players selection menu:**

![image](https://user-images.githubusercontent.com/75265945/167265198-6c30b822-445f-4b01-9aa2-ee296aed3c26.png)

**In-game menu (here I asked for help to see the best possible word):**

![image](https://user-images.githubusercontent.com/75265945/167265750-11b1f4de-ecc4-4941-a4e3-3fc5e79fe379.png)

**Endgame screen:**

![image](https://user-images.githubusercontent.com/75265945/167265785-744fb831-eeed-4fb2-8eee-44d818cacf8c.png)




