from mmtimer import mmtimer
import time

def tick():
    print("{0:.2f}".format(time.perf_counter() * 1000))

t1 = mmtimer(150, tick, periodic=False)
time.perf_counter()
t1.start(True)