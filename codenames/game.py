import random
import time
import json
import enum
import os
import shutil
import sys

import colorama
import gensim.models.keyedvectors as word2vec
import numpy as np
from nltk.corpus import wordnet_ic

class GameCondition(enum.Enum):
    """Enumeration that represents the different states of the game"""
    HIT_RED = 0
    HIT_BLUE = 1
    HIT_ASSASSIN = 2
    WIN_RED = 3
    WIN_BLUE = 4
    CONTINUE = 5


class Game:
    """Class that setups up game details and calls Guesser/Codemaster pair to play the game
    """

    def __init__(self, red_codemaster,red_guesser,blue_codemaster,blue_guesser,
                 seed="time", do_print=True, do_log=True, game_name="default",
                 red_cm_kwargs={}, red_g_kwargs={},blue_cm_kwargs={}, blue_g_kwargs={}):
        """ Setup Game details

        Args:
            codemaster (:class:`Codemaster`):
                Codemaster (spymaster in Codenames' rules) class that provides a clue.
            guesser (:class:`Guesser`):
                Guesser (field operative in Codenames' rules) class that guesses based on clue.
            seed (int or str, optional): 
                Value used to init random, "time" for time.time(). 
                Defaults to "time".
            do_print (bool, optional): 
                Whether to keep on sys.stdout or turn off. 
                Defaults to True.
            do_log (bool, optional): 
                Whether to append to log file or not. 
                Defaults to True.
            game_name (str, optional): 
                game name used in log file. Defaults to "default".
            cm_kwargs (dict, optional): 
                kwargs passed to Codemaster.
            g_kwargs (dict, optional): 
                kwargs passed to Guesser.
        """

        self.game_start_time = time.time()
        colorama.init()

        self.do_print = do_print
        if not self.do_print:
            self._save_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        self.team = ({"color": GameCondition.HIT_RED, "codemaster": red_codemaster(**red_cm_kwargs),
                      "guesser": red_guesser(**red_g_kwargs),
                      "cm_kwargs": red_cm_kwargs, "g_kwargs": red_g_kwargs},
                     {"color": GameCondition.HIT_BLUE, "codemaster": blue_codemaster(**blue_cm_kwargs),
                      "guesser": blue_guesser(**blue_g_kwargs),
                      "cm_kwargs": blue_cm_kwargs, "g_kwargs": blue_g_kwargs})
        print(self.team)
        self.do_log = do_log
        self.game_name = game_name

        # set seed so that board/keygrid can be reloaded later
        if seed == 'time':
            self.seed = time.time()
            random.seed(self.seed)
        else:
            self.seed = seed
            random.seed(int(seed))

        print("seed:", self.seed)

        # load board words
        with open("game_wordpool.txt", "r") as f:
            temp = f.read().splitlines()
            assert len(temp) == len(set(temp)), "game_wordpool.txt should not have duplicates"
            random.shuffle(temp)
            self.words_on_board = temp[:25]

        # set grid key for codemaster (spymaster)
        self.key_grid = ["Red"] * 8 + ["Blue"] * 7 + ["Civilian"] * 9 + ["Assassin"]
        random.shuffle(self.key_grid)

    def __del__(self):
        """reset stdout if using the do_print==False option"""
        if not self.do_print:
            sys.stdout.close()
            sys.stdout = self._save_stdout

    @staticmethod
    def load_glove_vecs(glove_file_path):
        """Load stanford nlp glove vectors
        Original source that matches the function: https://nlp.stanford.edu/data/glove.6B.zip
        """
        with open(glove_file_path, encoding="utf-8") as infile:
            glove_vecs = {}
            for line in infile:
                line = line.rstrip().split(' ')
                glove_vecs[line[0]] = np.array([float(n) for n in line[1:]])
            return glove_vecs

    @staticmethod
    def load_wordnet(wordnet_file):
        """Function that loads wordnet from nltk.corpus"""
        return wordnet_ic.ic(wordnet_file)

    @staticmethod
    def load_w2v(w2v_file_path):
        """Function to initalize gensim w2v object from Google News w2v Vectors
        Vectors Source: https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit
        """
        return word2vec.KeyedVectors.load_word2vec_format(w2v_file_path, binary=True, unicode_errors='ignore')

    def _display_board_codemaster(self):
        """prints out board with color-paired words, only for codemaster, color && stylistic"""
        print(str.center("___________________________BOARD___________________________\n", 60))
        counter = 0
        for i in range(len(self.words_on_board)):
            if counter >= 1 and i % 5 == 0:
                print("\n")
            if self.key_grid[i] is 'Red':
                print(str.center(colorama.Fore.RED + self.words_on_board[i], 15), " ", end='')
                counter += 1
            elif self.key_grid[i] is 'Blue':
                print(str.center(colorama.Fore.BLUE + self.words_on_board[i], 15), " ", end='')
                counter += 1
            elif self.key_grid[i] is 'Civilian':
                print(str.center(colorama.Fore.RESET + self.words_on_board[i], 15), " ", end='')
                counter += 1
            else:
                print(str.center(colorama.Fore.MAGENTA + self.words_on_board[i], 15), " ", end='')
                counter += 1
        print(str.center(colorama.Fore.RESET +
                         "\n___________________________________________________________", 60))
        print("\n")

    def _display_board(self):
        """prints the list of words in a board like fashion (5x5)"""
        print(colorama.Style.RESET_ALL)
        print(str.center("___________________________BOARD___________________________", 60))
        for i in range(len(self.words_on_board)):
            if i % 5 == 0:
                print("\n")
            print(str.center(self.words_on_board[i], 10), " ", end='')

        print(str.center("\n___________________________________________________________", 60))
        print("\n")

    def _display_key_grid(self):
        # """ Print the key grid to stdout  """
        print("\n")
        print(str.center(colorama.Fore.RESET +
                         "____________________________KEY____________________________\n", 55))
        counter = 0
        for i in range(len(self.key_grid)):
            if counter >= 1 and i % 5 == 0:
                print("\n")
            if self.key_grid[i] is 'Red':
                print(str.center(colorama.Fore.RED + self.key_grid[i], 15), " ", end='')
                counter += 1
            elif self.key_grid[i] is 'Blue':
                print(str.center(colorama.Fore.BLUE + self.key_grid[i], 15), " ", end='')
                counter += 1
            elif self.key_grid[i] is 'Civilian':
                print(str.center(colorama.Fore.RESET + self.key_grid[i], 15), " ", end='')
                counter += 1
            else:
                print(str.center(colorama.Fore.MAGENTA + self.key_grid[i], 15), " ", end='')
                counter += 1
        print(str.center(colorama.Fore.RESET +
                         "\n___________________________________________________________", 55))
        print("\n")

    def get_words_on_board(self):
        """Return the list of words that represent the board state"""
        return self.words_on_board

    def get_key_grid(self):
        """Return the codemaster's key"""
        return self.key_grid

    def _accept_guess(self, guess_index):
        """Function that takes in an int index called guess to compare with the key grid
        CodeMaster will always win with Red and lose if Blue =/= 7 or Assassin == 1
        """
        if guess_index is None:
            return GameCondition.CONTINUE
        if self.key_grid[guess_index] == "Red":
            self.words_on_board[guess_index] = "*Red*"
            if self.words_on_board.count("*Red*") >= 8:
                return GameCondition.WIN_RED
            return GameCondition.HIT_RED

        elif self.key_grid[guess_index] == "Blue":
            self.words_on_board[guess_index] = "*Blue*"
            if self.words_on_board.count("*Blue*") >= 7:
                return GameCondition.WIN_BLUE
            else:
                return GameCondition.HIT_BLUE

        elif self.key_grid[guess_index] == "Assassin":
            self.words_on_board[guess_index] = "*Assassin*"
            return GameCondition.HIT_ASSASSIN

        else:
            self.words_on_board[guess_index] = "*Civilian*"
            return GameCondition.CONTINUE

    def write_results(self, game_condition,num_of_turns):
        """Logging function
        writes in both the original and a more detailed new style
        """
        red_result = 0
        blue_result = 0
        civ_result = 0
        assa_result = 0

        for i in range(len(self.words_on_board)):
            if self.words_on_board[i] == "*Red*":
                red_result += 1
            elif self.words_on_board[i] == "*Blue*":
                blue_result += 1
            elif self.words_on_board[i] == "*Civilian*":
                civ_result += 1
            elif self.words_on_board[i] == "*Assassin*":
                assa_result += 1
        total = red_result + blue_result + civ_result + assa_result

        if game_condition==GameCondition.HIT_BLUE or game_condition==GameCondition.WIN_RED:
            winner="RED"
        else:
            winner="BLUE"

        if not os.path.exists("results"):
            os.mkdir("results")

        with open("results/bot_results.txt", "a") as f:
            f.write(
                f'TOTAL:{num_of_turns} WINNER:{winner} SEED:{self.seed} '
                f'R:{red_result}B:{blue_result} C:{civ_result} A:{assa_result}'
                f' RED_CM:{self.team[0]["codemaster"].get_name()} RED_GUESSER:{self.team[0]["guesser"].get_name()} '
                f' BLUE_CM:{self.team[1]["codemaster"].get_name()} BLUE_GUESSER:{self.team[1]["guesser"].get_name()} \n'
            )

        with open("results/bot_results_new_style.txt", "a") as f:
            results = {"game_name": self.game_name,
                       "total_turns": num_of_turns,
                       "winner": winner,
                       "seed": self.seed,
                       "time_s": (self.game_end_time - self.game_start_time),
                       "R": red_result, "B": blue_result, "C": civ_result, "A": assa_result,
                       "RED_codemaster": self.team[0]["codemaster"].get_name(),
                       "RED_guesser": self.team[0]["guesser"].get_name(),
                       "RED_cm_kwargs": {k: v if isinstance(v, float) or isinstance(v, int) or isinstance(v, str) else None
                                     for k, v in self.team[0]["cm_kwargs"].items()},
                       "RED_g_kwargs": {k: v if isinstance(v, float) or isinstance(v, int) or isinstance(v, str) else None
                                    for k, v in self.team[0]["g_kwargs"].items()},
                       "BLUE_codemaster": self.team[1]["codemaster"].get_name(),
                       "BLUE_guesser": self.team[1]["guesser"].get_name(),
                       "BLUE_cm_kwargs": {
                           k: v if isinstance(v, float) or isinstance(v, int) or isinstance(v, str) else None
                           for k, v in self.team[1]["cm_kwargs"].items()},
                       "BLUE_g_kwargs": {
                           k: v if isinstance(v, float) or isinstance(v, int) or isinstance(v, str) else None
                           for k, v in self.team[1]["g_kwargs"].items()}
                       }
            f.write(json.dumps(results))
            f.write('\n')

    @staticmethod
    def clear_results():
        """Delete results folder"""
        if os.path.exists("results") and os.path.isdir("results"):
            shutil.rmtree("results")

    def run(self):
        """Function that runs the codenames game between codemaster and guesser"""
        game_condition = GameCondition.HIT_RED
        game_counter = -1
        while game_condition != GameCondition.HIT_ASSASSIN and game_condition != GameCondition.WIN_RED and game_condition != GameCondition.WIN_BLUE:
            # board setup and display
            print('\n' * 2)
            game_counter += 1
            game_condition = self.team[game_counter % 2]["color"]
            if self.team[game_counter % 2]["codemaster"].get_name() == "PassCodemaster":
                continue
            words_in_play = self.get_words_on_board()
            current_key_grid = self.get_key_grid()
            self.team[game_counter%2]["codemaster"].set_game_state(words_in_play, current_key_grid)
            # self._display_key_grid()
            self._display_board_codemaster()
            print("It is", "RED" if game_condition == GameCondition.HIT_RED else "BLUE", "Codemaster's turn.")
            # codemaster gives clue & number here
            clue, clue_num = self.team[game_counter%2]["codemaster"].get_clue()
            keep_guessing = True
            guess_num = 0
            clue_num = int(clue_num)

            print('\n' * 2)
            print("It is", "RED" if game_condition == GameCondition.HIT_RED else "BLUE","Guesser's turn." )
            if self.team[game_counter % 2]["guesser"].get_name() == "HumanGuesser":
                self._display_board()
            else:
                self._display_board_codemaster()
            self.team[game_counter % 2]["guesser"].set_clue(clue, clue_num)
            while guess_num <= clue_num and keep_guessing and game_condition == self.team[game_counter%2]["color"]:
                self.team[game_counter%2]["guesser"].set_board(words_in_play)
                guess_answer = self.team[game_counter%2]["guesser"].get_answer()

                # if no comparisons were made/found than retry input from codemaster
                if guess_answer is None or guess_answer == "no comparisons":
                    break
                if guess_answer == "":
                    guess_answer_index = None
                else:
                    guess_answer_index = words_in_play.index(guess_answer.upper().strip())
                game_condition = self._accept_guess(guess_answer_index)

                if game_condition == self.team[game_counter%2]["color"]:
                    print('\n' * 2)
                    if self.team[game_counter % 2]["guesser"].get_name() == "HumanGuesser":
                        self._display_board()
                    else:
                        self._display_board_codemaster()
                    guess_num += 1
                    print("Keep Guessing? the clue is ", clue, clue_num)
                    keep_guessing = self.team[game_counter%2]["guesser"].keep_guessing()
                elif game_condition == GameCondition.HIT_ASSASSIN:
                    self.game_end_time = time.time()
                    self._display_board_codemaster()
                    if self.do_log:
                        self.write_results(self.team[game_counter % 2]["color"],game_counter)
                    if self.team[game_counter % 2]["color"] == GameCondition.HIT_RED:
                        print("BLUE Team Won")
                    elif self.team[game_counter % 2]["color"] == GameCondition.HIT_BLUE:
                        print("RED Team Won")
                    print("Game Counter:", game_counter)

                elif game_condition == GameCondition.WIN_RED or game_condition == GameCondition.WIN_BLUE:
                    self.game_end_time = time.time()
                    self._display_board_codemaster()
                    if self.do_log:
                        self.write_results(game_condition,game_counter)
                    print("RED Team Won") if game_condition == GameCondition.WIN_RED else print("BLUE Team Won")
                    print("Game Counter:", game_counter)
                else:
                    break