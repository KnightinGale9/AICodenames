import subprocess

results=[]
# for everything else but glove vs glove
def run():
    # w2v_thresholds vs w2vglove300
    counter = 1667802218
    cm="players.codemaster_transformer.AICodemaster"
    guess="players.guesser_transformer.AIGuesser"

    str_counter = str(int(counter))
    subprocess.run(["python", "run_game.py", cm, guess,
                    "--no_log","--seed", str_counter])

# "--glove", "players/glove/glove.6B.300d.txt",
#"--w2v","players/GoogleNews-vectors-negative300.bin",
run()
