### **Installation:**

```jql
pip install ttlstore
```

### **Getting started:**

```jql
import time

from ttlstore import TTLStore


d = TTLStore(ttl=1) # use d like a python dictionary
d['a'] = 'b'
time.sleep(2)
# 'a' is not present any more in the memory
print(d)

def call_me(key, value):
   print(key, value)

d = TTLStore(ttl=1, callback=call_me)
d['a'] = 'b'
time.sleep(2)
# 'a' is not present any more in the memory and call_me is called.
print(d)
```

### **To run example script:**
```jql
➜  python example.py
INFO:root:-------- executing example 1 ----------
DEBUG:root:contents of dict: {}
INFO:root:-------- end of example 1 ---------
INFO:root:-------- executing example 2 ----------
DEBUG:root:executing call back for deleted k: 1, v: 3
DEBUG:root:executing call back for deleted k: 2, v: 4
DEBUG:root:contents of dict: {}
INFO:root:-------- end of example 2 ---------
INFO:root:-------- executing example 3 ------
DEBUG:root:done inserting 1000 elements in a tight loop, time taken: 0.0015082359313964844
DEBUG:root:length of dict: 0
DEBUG:root:done inserting 10000 elements sporadically, time taken: 3.6316630840301514
DEBUG:root:length of dict: 0
INFO:root:-------- end of example 3 ----
```

### **To run tests:**

```jql
python -m unittest -v tests/ttlstore_test.py
```

### **Unittest results:**

```jql
 ➜ python -m unittest -v tests/ttlstore_test.py
test_basics (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_create (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_get (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_iter (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_not_implemented (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_pop (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_reset_of_key_no_trim (tests.ttlstore_test.TTLStoreTestCases)
Re-setting an existing key should not cause a non-expired key to be dropped ... ok
test_set (tests.ttlstore_test.TTLStoreTestCases) ... ok
test_setdefault (tests.ttlstore_test.TTLStoreTestCases) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.089s

OK
```