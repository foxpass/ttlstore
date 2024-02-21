import logging
import time

from ttlstore import TTLStore

# debug level is required to trace the events happening in a TTLStore
logging.basicConfig(level=logging.DEBUG)

# example 1:
logging.info("-------- executing example 1 ----------")
# Initialize the dict
# - TTL for every element inserted into the store is 0.5s
d = TTLStore(ttl=0.5)

# start adding
d["1"] = 3
d["2"] = 4
# delete operation
del d["1"]

# sleep for 0.6 seconds, "2" shouldn't be present anymore after
time.sleep(0.6)

logging.debug("contents of dict: {}".format(d))
logging.info("-------- end of example 1 ---------")

# example 2:

logging.info("-------- executing example 2 ----------")


# Example to show how we can have a callback on delete operation
def call_me(key, value):
    logging.debug("executing call back for deleted k: {}, v: {}".format(key, value))


d = TTLStore(ttl=0.5, callback=call_me)

# start adding
d["1"] = 3

d["2"] = 4
# delete operation
del d["1"]  # pop operation is supported as well

# sleep for 0.6 seconds, "2" shouldn't be present anymore
time.sleep(0.6)

logging.debug("contents of dict: {}".format(d))
logging.info("-------- end of example 2 ---------")

logging.info("-------- executing example 3 ------")
d = TTLStore(ttl=0.5)

logging.debug("inserting 1000 elements in a tight loop...")
t1 = time.time()
for i in range(0, 1000):
    d[i] = i + 1

logging.debug("done inserting 1000 elements in a tight loop, time taken: {}".format(time.time() - t1))
time.sleep(0.6)
logging.debug("length of dict: {}".format(len(d)))

logging.debug("inserting 10000 elements sporadically...")
t1 = time.time()
for i in range(0, 10000):
    time.sleep(0.0002)
    d[i] = i + 1

logging.debug("done inserting 10000 elements sporadically, time taken: {}".format(time.time() - t1))

time.sleep(0.5)
logging.debug("length of dict: {}".format(len(d)))
logging.info("-------- end of example 3 ----")
