import subprocess

results=[]
# for everything else but glove vs glove
def run():
    # w2v_thresholds vs w2vglove300
    counter = 500
    cm="players.codemaster_transformer.AICodemaster"
    guess="players.guesser_glove.AIGuesser"

    str_counter = str(int(counter))
    subprocess.run(["python", "run_game.py", cm, guess, "--glove", "players/glove/glove.6B.300d.txt",
                    "--no_log","--seed", str_counter])

# "--glove", "players/glove/glove.6B.300d.txt",
#"--w2v","players/GoogleNews-vectors-negative300.bin",
run()
