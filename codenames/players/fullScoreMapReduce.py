import statistics
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
        result.append(0)
        result.append(temp)
        for line in guesses:
            y, value = line
            if y == assassin:
                removal = []
                for item in result[2]:
                    if result[2][item]<value+0.1:
                        removal.append(item)
                for x in removal:
                    result[2].pop(x)
                break
            if y in red:
                result[2][y] = value
            else:
                removal = []

                for item in result[2]:
                    if result[2][item] < value + 0.05:
                        removal.append(item)
                for x in removal:
                    result[2].pop(x)
                break
        result[1] = len(result[2])
        additive=0
        for item in result[2]:
            additive += result[2][item]
        std=0
        if len(result[2])>1:
            std=statistics.stdev(list(result[2].values()))
        # result.append(0.6*additive+0.3*std+0.1*result[1])
        result.append(additive+std)
        if len(result[2].keys()) > 0:  # and guesses[vallen-1][0] == result[vallen]:
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