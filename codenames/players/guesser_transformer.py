import torch
import os
import json
from sentence_transformers import SentenceTransformer, util
from players.guesser import Guesser

class AIGuesser(Guesser):
    def __init__(self, brown_ic=None, glove_vecs=None, word_vectors=None):
        super().__init__()
        self.name = "AIGuesser.transformer"
        self.numclue=0

    def get_name(self):
        return self.name

    def set_board(self, words_on_board):
        self.words = words_on_board

    def set_clue(self, clue, num):
        self.clue = clue
        self.num = num
        print("The clue is:", clue, num)
        li = [clue, num]
        return li

    def keep_guessing(self): 
        return self.num > 0

    def get_answer(self):
        sorted_words = self.compute_distance(self.clue, self.words)
        print(f'guesses: {sorted_words}')
        self.num -= 1
        return sorted_words[0][1]

    def compute_distance(self, clue, board):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        guesses = []
        setboard = set(board)
        playfeild = model.encode(board, convert_to_tensor=True)

        guesses_embeded = model.encode(clue, convert_to_tensor=True)
        cosine_scores = util.cos_sim(guesses_embeded, playfeild)[0]
        top_results = torch.topk(cosine_scores, k=len(board))
        for score, idx in zip(top_results[0], top_results[1]):
            if board[idx][0]=="*":
                continue
            guesses.append((score, board[idx]))
        guesses.sort(reverse=True)
        return guesses