import cProfile
import main

cProfile.run("main.main()", sort="cumtime")
