import re
import sys
import json
from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol


class fullScore(MRJob):
    INTERNAL_PROTCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, _, line):
        # print(line)
        val = line.split(",")
        clue, word, num = val
        if num != 1.0 and clue not in board:
            yield clue, {"word": word, "value": float(num)}

    def reducer(self, key, values):
        guesses = []
        result = []
        temp = {}
        score = 0
        for x in values:
            guesses.append([x["word"], x["value"]])
        guesses.sort(key=lambda x: x[1], reverse=True)
        # print(guesses)
        result.append(key)
        result.append(temp)
        for line in guesses:
            y, value = line
            if y == assassin:
                break
            if y in red:
                score += value
                result[1][y] = value
            else:
                break
        # result.append(len(result))
        result.append(score)
        if len(result[1].keys()) > 0:  # and guesses[vallen-1][0] == result[vallen]:
            yield key, result


if __name__ == '__main__':
    f = open("boardTransfer.json")
    boardTransfer = json.load(f)
    board = set(boardTransfer[0])
    red = set(boardTransfer[1])
    blue = set(boardTransfer[2])
    assassin = boardTransfer[3]
    f.close()
    fullScore.run()