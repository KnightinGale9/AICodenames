import torch
import os
import json
from sentence_transformers import SentenceTransformer, util
from players.fullScoreMapReduce import fullScore
from players.codemaster import Codemaster

os.environ["TOKENIZERS_PARALLELISM"] = "false"
class AICodemaster(Codemaster):
    def __init__(self, brown_ic=None, glove_vecs=None, word_vectors=None):
        super().__init__()
        self.name = "AICodemaster.transformer"
        self.cm_wordlist = []
        self.call = 0
        # self.given_clue={}
        with open('players/cm_wordlist.txt') as infile:
            for line in infile:
                self.cm_wordlist.append(line.rstrip())
        # with open('players/cm_wordlist.txt') as infile:
        #     for line in infile:
        #         self.cm_wordlist.append(line.rstrip())
        # y = json.dumps(self.cm_wordlist)
        # f = open("cm_wordlist.json", "w")
        # f.write(y)
        # f.close()

    def get_name(self):
        return self.name

    def set_game_state(self, words_on_board, key_grid):
        self.words = words_on_board
        self.maps = key_grid
        if self.call ==0:
            self.map_reduce()
        self.call+=1


    def get_clue(self):
        self.create_boardtransfer()
        mr_job = fullScore(args=['-r', 'local', 'players/full_score.csv', '--files', 'players/boardTransfer.json'])
        finalguess = []
        with mr_job.make_runner() as runner:
            runner.run()  # ... etc
            for _, value in mr_job.parse_output(runner.cat_output()):
                finalguess.append(value)
                # print(value)

        finalguess.sort(key=lambda x: x[1], reverse=True)
        prediction_list = []
        for key, value, valuelist, score in finalguess:
            # prediction_list.append([key, value, score,valuelist])
            prediction_list.append([key, value, score / value + score,valuelist])
        prediction_list.sort(key=lambda x: x[2], reverse=True)
        print(prediction_list[:5])
        bestclue = prediction_list[0]
        # if bestclue[0] not in self.given_clue:
        #     self.given_clue[bestclue[0]] ==0
        # else:
        #     self.given_clue[bestclue[0]] +=1
        return bestclue[0], bestclue[1]

    def create_boardtransfer(self):
        board_location = [[], [], []]
        for i, x in enumerate(self.maps):
            board_location[0].append(self.words[i])
            if x == "Red" and self.words[i] != "*Red*":
                board_location[1].append(self.words[i])
            if x == "Blue" and self.words[i] != "*Blue*":
                board_location[2].append(self.words[i])
            if x == "Assassin":
                board_location.append(self.words[i])
        z = json.dumps(board_location)
        f = open("players/boardTransfer.json", 'w')
        f.write(z)
        f.close()
        self.red = set(board_location[1])

    def map_reduce(self):
        # calculating all the scores for the initial guess
        model = SentenceTransformer('all-MiniLM-L6-v2')
        # Two lists of sentences
        f = open("players/full_score.csv", "w")
        # Compute embedding for both lists
        full_score = []
        playfeild = model.encode(self.words, convert_to_tensor=True)

        # Compute cosine-similarities
        for i, guesses in enumerate(self.cm_wordlist):
            guesses_embeded = model.encode(guesses, convert_to_tensor=True)
            cosine_scores = util.cos_sim(guesses_embeded, playfeild)[0]
            top_results = torch.topk(cosine_scores, k=9)
            for score, idx in zip(top_results[0], top_results[1]):
                if self.words[idx] in guesses.upper() or guesses.upper() in self.words[idx]:
                    # print(f"removed {self.words[idx]} from {guesses}.")
                    continue
                f.write(f"{guesses},{self.words[idx]},{round(float(score), 4)}\n")
        f.close()