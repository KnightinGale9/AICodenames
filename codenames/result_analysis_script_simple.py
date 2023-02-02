import subprocess
#run in terminal:
#python3 result_analysis_script_simple.py
results=[]
# for everything else but glove vs glove
def run():
    # w2v_thresholds vs w2vglove300
    counter = 1650
    cm="players.codemaster_transformer.AICodemaster"
    guess="players.guesser_glove.AIGuesser"
    # ["players.guesser_glove.AIGuesser", "players.guesser_w2v.AIGuesser",
    #  "players.guesser_w2vglove.AIGuesser", "players.guesser_transformer.AIGuesser"]
    str_counter = str(int(counter))
    subprocess.run(["python", "run_game.py", cm, guess,
                    "--no_log","--glove", "players/glove/glove.6B.300d.txt","--seed", str_counter])

# "--glove", "players/glove/glove.6B.300d.txt",
#"--w2v","players/GoogleNews-vectors-negative300.bin",
run()
