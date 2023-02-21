import subprocess
import warnings
warnings.filterwarnings("ignore")
runtime=30
seed=500
def run():
    guesserlist = ["players.guesser_glove.AIGuesser","players.guesser_w2v.AIGuesser",
                    "players.guesser_w2vglove.AIGuesser","players.guesser_transformer.AIGuesser"]

    cmlist= ["players.codemaster_glove_03.AICodemaster",
            "players.codemaster_glove_05.AICodemaster","players.codemaster_glove_07.AICodemaster",
            "players.codemaster_w2v_03.AICodemaster", "players.codemaster_w2v_05.AICodemaster",
             "players.codemaster_w2v_07.AICodemaster","players.codemaster_w2vglove_03.AICodemaster",
             "players.codemaster_w2vglove_05.AICodemaster","players.codemaster_w2vglove_07.AICodemaster"]
    for temp in range(4):
        counter=seed
        for guesser in guesserlist:
            for i in range(runtime):
                gamerun("players.codemaster_transformer.AICodemaster", guesser,counter,temp)
                counter += 50
        counter=seed
        for codemaster in cmlist:
            for i in range(runtime):
                gamerun(codemaster, "players.guesser_transformer.AIGuesser", counter,temp)
                counter += 50
    print("This Program has officially ended")

def gamerun(codemaster, guesser, seed,runnum):
    builder=["python", "run_game.py", codemaster, guesser]
    glovename=""
    if "w2v" in codemaster or "w2v" in guesser:
        builder.append("--w2v")
        builder.append("players/GoogleNews-vectors-negative300.bin")
        glovename = "w2v"
    if "glove" in codemaster or "glove" in guesser:
        builder.append("--glove")
        if runnum == 0:
            builder.append("players/glove/glove.6B.300d.txt")
            glovename="glove.6B.300d"
        elif runnum == 1:
            builder.append("players/glove/glove.6B.200d.txt")
            glovename = "glove.6B.200d"
        elif runnum == 2:
            builder.append("players/glove/glove.6B.100d.txt")
            glovename = "glove.6B.100d"
        elif runnum == 3:
            builder.append("players/glove/glove.6B.50d.txt")
            glovename = "glove.6B.50d"

    builder.append("--no_print")
    builder.append("--seed")
    builder.append(str(seed))
    builder.append("--game_name")
    namestr= glovename
    builder.append(namestr)

    print(builder)

    subprocess.run(builder)

run()