from mmtimer import mmtimer
import time

def tick():
    print("{0:.2f}".format(time.perf_counter() * 1000))

t1 = mmtimer(10, tick)
time.perf_counter()
t1.start(True)
time.sleep(0.1)
t1.stop()