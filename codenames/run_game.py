import sys
import importlib
import argparse
import time
import os

from game import Game
from players.guesser import *
from players.codemaster import *

class GameRun:
    """Class that builds and runs a Game based on command line arguments"""

    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Run the Codenames AI competition game.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("red_codemaster", help="import string of form A.B.C.MyClass or 'human' or 'pass'")
        parser.add_argument("red_guesser", help="import string of form A.B.C.MyClass or 'human' or 'pass'")
        parser.add_argument("blue_codemaster", help="import string of form A.B.C.MyClass or 'human' or 'pass'")
        parser.add_argument("blue_guesser", help="import string of form A.B.C.MyClass or 'human' or 'pass'")
        parser.add_argument("--seed", help="Random seed value for board state -- integer or 'time'", default='time')

        parser.add_argument("--w2v", help="Path to w2v file or None", default=None)
        parser.add_argument("--glove", help="Path to glove file or None", default=None)
        parser.add_argument("--wordnet", help="Name of wordnet file or None, most like ic-brown.dat", default=None)
        parser.add_argument("--glove_cm", help="Path to glove file or None", default=None)
        parser.add_argument("--glove_guesser", help="Path to glove file or None", default=None)

        parser.add_argument("--red_w2v", help="Path to w2v file or None", default=None)
        parser.add_argument("--red_glove", help="Path to glove file or None", default=None)
        parser.add_argument("--red_wordnet", help="Name of wordnet file or None, most like ic-brown.dat", default=None)
        parser.add_argument("--red_glove_cm", help="Path to glove file or None", default=None)
        parser.add_argument("--red_glove_guesser", help="Path to glove file or None", default=None)

        parser.add_argument("--blue_w2v", help="Path to w2v file or None", default=None)
        parser.add_argument("--blue_glove", help="Path to glove file or None", default=None)
        parser.add_argument("--blue_wordnet", help="Name of wordnet file or None, most like ic-brown.dat", default=None)
        parser.add_argument("--blue_glove_cm", help="Path to glove file or None", default=None)
        parser.add_argument("--blue_glove_guesser", help="Path to glove file or None", default=None)

        parser.add_argument("--no_log", help="Supress logging", action='store_true', default=False)
        parser.add_argument("--no_print", help="Supress printing", action='store_true', default=False)
        parser.add_argument("--game_name", help="Name of game in log", default="default")

        args = parser.parse_args()

        self.do_log = not args.no_log
        self.do_print = not args.no_print
        if not self.do_print:
            self._save_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        self.game_name = args.game_name

        self.red_g_kwargs = {}
        self.red_cm_kwargs = {}
        self.blue_g_kwargs = {}
        self.blue_cm_kwargs = {}

        # load codemaster class
        print("\nLOADING RED TEAM")
        if args.red_codemaster == "human":
            self.red_codemaster = HumanCodemaster
        elif args.red_codemaster == "pass":
            self.red_codemaster = PassCodemaster
        else:
            self.red_codemaster = self.import_string_to_class(args.red_codemaster)
        print('loaded red codemaster class:',args.red_codemaster)

        # load guesser class
        if args.red_guesser == "human":
            self.red_guesser = HumanGuesser
        elif args.red_guesser == "pass":
            self.red_guesser = PassGuesser
        else:
            self.red_guesser = self.import_string_to_class(args.red_guesser)
        print('loaded red guesser class:',args.red_guesser)

        print("\nLOADING BLUE TEAM")
        if args.blue_codemaster == "human":
            self.blue_codemaster = HumanCodemaster
        elif args.blue_codemaster == "pass":
            self.blue_codemaster = PassCodemaster
        else:
            self.blue_codemaster = self.import_string_to_class(args.blue_codemaster)
        print('loaded blue codemaster class:',args.blue_codemaster)

        # load guesser class
        if args.blue_guesser == "human":
            self.blue_guesser = HumanGuesser
        elif args.blue_guesser == "pass":
            self.blue_guesser = PassCodemaster
        else:
            self.blue_guesser = self.import_string_to_class(args.blue_guesser)
        print('loaded blue guesser class:', args.blue_guesser)

        # if the game is going to have an ai, load up word vectors
        if sys.argv[1] != "human" or sys.argv[2] != "human" or sys.argv[3] != "human" or sys.argv[4] != "human":
            if args.wordnet is not None:
                brown_ic = Game.load_wordnet(args.wordnet)
                self.red_g_kwargs["brown_ic"] = brown_ic
                self.red_cm_kwargs["brown_ic"] = brown_ic
                self.blue_g_kwargs["brown_ic"] = brown_ic
                self.blue_cm_kwargs["brown_ic"] = brown_ic
                print('loaded red and blue wordnet')

            if args.glove is not None:
                glove_vectors = Game.load_glove_vecs(args.glove)
                self.red_g_kwargs["glove_vecs"] = glove_vectors
                self.red_cm_kwargs["glove_vecs"] = glove_vectors
                self.blue_g_kwargs["glove_vecs"] = glove_vectors
                self.blue_cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded red and blue glove vectors')

            if args.w2v is not None:
                w2v_vectors = Game.load_w2v(args.w2v)
                self.red_g_kwargs["word_vectors"] = w2v_vectors
                self.red_cm_kwargs["word_vectors"] = w2v_vectors
                self.blue_g_kwargs["word_vectors"] = w2v_vectors
                self.blue_cm_kwargs["word_vectors"] = w2v_vectors
                print('loaded red and blue word vectors')

            if args.glove_cm is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_cm)
                self.red_cm_kwargs["glove_vecs"] = glove_vectors
                self.blue_cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded red and blue glove vectors')

            if args.glove_guesser is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_guesser)
                self.red_g_kwargs["glove_vecs"] = glove_vectors
                self.blue_g_kwargs["glove_vecs"] = glove_vectors
                print('loaded red and blue  glove vectors')


            if args.red_wordnet is not None:
                brown_ic = Game.load_wordnet(args.wordnet)
                self.red_g_kwargs["brown_ic"] = brown_ic
                self.red_cm_kwargs["brown_ic"] = brown_ic
                print('loaded red wordnet')

            if args.red_glove is not None:
                glove_vectors = Game.load_glove_vecs(args.glove)
                self.red_g_kwargs["glove_vecs"] = glove_vectors
                self.red_cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded red glove vectors')

            if args.red_w2v is not None:
                w2v_vectors = Game.load_w2v(args.w2v)
                self.red_g_kwargs["word_vectors"] = w2v_vectors
                self.red_cm_kwargs["word_vectors"] = w2v_vectors
                print('loaded red word vectors')

            if args.red_glove_cm is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_cm)
                self.red_cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded red glove vectors')

            if args.red_glove_guesser is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_guesser)
                self.red_g_kwargs["glove_vecs"] = glove_vectors
                print('loaded red glove vectors')


            if args.blue_wordnet is not None:
                brown_ic = Game.load_wordnet(args.wordnet)
                self.blue_g_kwargs["brown_ic"] = brown_ic
                self.blue_cm_kwargs["brown_ic"] = brown_ic
                print('loaded blue wordnet')

            if args.blue_glove is not None:
                glove_vectors = Game.load_glove_vecs(args.glove)
                self.blue_g_kwargs["glove_vecs"] = glove_vectors
                self.blue_cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded blue glove vectors')

            if args.blue_w2v is not None:
                w2v_vectors = Game.load_w2v(args.w2v)
                self.blue_g_kwargs["word_vectors"] = w2v_vectors
                self.blue_cm_kwargs["word_vectors"] = w2v_vectors
                print('loaded blue word vectors')

            if args.blue_glove_cm is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_cm)
                self.blue_cm_kwargs["glove_vecs"] = glove_vectors
                print('loaded blue glove vectors')

            if args.blue_glove_guesser is not None:
                glove_vectors = Game.load_glove_vecs(args.glove_guesser)
                self.blue_g_kwargs["glove_vecs"] = glove_vectors
                print('loaded blue glove vectors')

        # set seed so that board/keygrid can be reloaded later
        if args.seed == 'time':
            self.seed = time.time()
        else:
            self.seed = int(args.seed)

    def __del__(self):
        """reset stdout if using the do_print==False option"""
        if not self.do_print:
            sys.stdout.close()
            sys.stdout = self._save_stdout

    def import_string_to_class(self, import_string):
        """Parse an import string and return the class"""
        parts = import_string.split('.')
        module_name = '.'.join(parts[:len(parts) - 1])
        class_name = parts[-1]

        module = importlib.import_module(module_name)
        my_class = getattr(module, class_name)

        return my_class


if __name__ == "__main__":
    game_setup = GameRun()

    game = Game(red_codemaster=game_setup.red_codemaster,red_guesser=game_setup.red_guesser,
                blue_codemaster=game_setup.blue_codemaster, blue_guesser=game_setup.blue_guesser,
                seed=game_setup.seed,
                do_print=game_setup.do_print,
                do_log=game_setup.do_log,
                game_name=game_setup.game_name,
                red_cm_kwargs=game_setup.red_cm_kwargs,
                red_g_kwargs=game_setup.red_g_kwargs,
                blue_cm_kwargs = game_setup.blue_cm_kwargs,
                blue_g_kwargs = game_setup.blue_g_kwargs)

    game.run()
