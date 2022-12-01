import subprocess
import warnings
warnings.filterwarnings("ignore")
runtime=15
seed=450
def run():
    guesserlist = ["players.guesser_glove.AIGuesser","players.guesser_w2v.AIGuesser"
                    ,"players.guesser_w2vglove.AIGuesser","players.guesser_transformer.AIGuesser"]
    cmlist= ["players.codemaster_transformer.AICodemaster","players.codemaster_glove_03.AICodemaster",
            "players.codemaster_glove_05.AICodemaster","players.codemaster_glove_07.AICodemaster",
            "players.codemaster_w2v_03.AICodemaster", "players.codemaster_w2v_05.AICodemaster",
             "players.codemaster_w2v_07.AICodemaster","players.codemaster_w2vglove_03.AICodemaster",
             "players.codemaster_w2vglove_05.AICodemaster","players.codemaster_w2vglove_07.AICodemaster"]
    counter=seed
    for i in range(runtime):
        for guesser in guesserlist:
            gamerun("players.codemaster_transformer.AICodemaster", guesser,counter)
        for codemaster in cmlist:
            gamerun(codemaster,"players.guesser_transformer.AIGuesser", counter)
        counter += 50

def gamerun(codemaster, guesser, seed):
    builder=["python", "run_game.py", codemaster, guesser]
    if "w2v" in codemaster or "w2v" in guesser:
        builder.append("--w2v")
        builder.append("players/GoogleNews-vectors-negative300.bin")
    if "glove" in codemaster or "glove" in guesser:
        builder.append("--glove")
        builder.append("players/glove/glove.6B.300d.txt")
    builder.append("--no_print")
    builder.append("--seed")
    builder.append(str(seed))
    print(builder)

    subprocess.run(builder)

run()