import heapq
import logging
import threading
import time

from threading import Event


class TTLStore(dict):
    """
    This library:
      - creates a dictionary that automatically deletes keys upon reaching ttl value.
      - provides a callback upon deletion.

    Assumptions:
      - When a key is reinserted/updated, the ttl value is reset.
      - Callback exceptions are ignored. Callbacks need to handle their exceptions.

    Behaviors:
      - Get operation: O(1)
      - Set operation:
         - new element: O(log n)
         - reinsert/update (worst case): O(n)
      - Delete operation: O(n)
    """

    def __init__(self, *args, **kwargs):
        self.heap = []
        # ttl in secs
        if 'ttl' in kwargs:
            self.ttl = kwargs['ttl']
            kwargs.pop('ttl')
        else:
            raise Exception("ttl value not provided")
        self.callback = None
        if 'callback' in kwargs:
            self.callback = kwargs['callback']
            kwargs.pop('callback')

        self.debug = False
        if 'debug' in kwargs:
            self.debug = bool(kwargs['debug'])
            kwargs.pop('debug')

        self.wake_event = Event()
        # every element takes the following form: (time, k) in heap
        super().__init__(*args, **kwargs)
        ttl_t = threading.Thread(target=self.remove_on_ttl)
        ttl_t.daemon = True
        ttl_t.start()

    def __setitem__(self, key, value):
        # worst case O(n) happens when element is reinserted
        # best case O(log n) when the new element is inserted
        self.find_remove_reheapify(key)
        heapq.heappush(self.heap, (time.time(), key))
        ret = super().__setitem__(key, value)
        # getting the length of dictionary if O(1) operation
        if len(self) == 1:
            # wake up the ttl thread that could be sleeping
            self.wake_event.set()
            self.log("length of dict is 1, wake up the ttl book keeper...")
        return ret

    def __getitem__(self, key):
        # get is a O(1) operation
        return super().__getitem__(key)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def _setdefault(self, key, default):
        self.find_remove_reheapify(key)
        heapq.heappush(self.heap, (time.time(), key))
        ret = super().setdefault(key, default)
        # getting the length of dictionary if O(1) operation
        if len(self) == 1:
            # wake up the ttl thread that could be sleeping
            self.wake_event.set()
            self.log("length of dict is 1, wake up the ttl book keeper...")
        return ret

    def setdefault(self, key, default=None):
        # Returns the value of the specified key.
        # If the key does not exist: insert the key, with the specified value
        if key in self:
            return self.__getitem__(key)

        return self._setdefault(key, default)

    def update(self, k_v_pairs, default=None):
        # this is not implemented, but can be in the future
        raise NotImplementedError

    def popitem(self):
        # this is not implemented, but can be in the future
        raise NotImplementedError

    def copy(self):
        # this is not implemented, but can be in the future
        raise NotImplementedError

    def clear(self):
        # this is not implemented, but can be in the future
        raise NotImplementedError

    def __delitem__(self, key):
        value = self[key]
        # worst case: o(n) when the full heap needs to be traversed
        del_index = self.find_remove_reheapify(key)
        ret = super().__delitem__(key)
        if self.callback:
            try:
                self.callback(key, value)
            except:
                # for now if there's an exception in the callback we ignore and move on
                pass
        # notify if the ttl thread is sleeping to wake up if the key it is sleeping on is deleted
        if del_index == 0:
            self.log("wake up ttl book keeper, it is sleeping on deleted key: {}".format(key))
            self.wake_event.set()
        return ret

    def log(self, message):
        if self.debug:
            logging.debug(message)

    def pop(self, key):
        value = self[key]
        # worst case: o(n) when the full heap needs to be traversed
        del_index = self.find_remove_reheapify(key)
        ret = super().pop(key)
        if self.callback:
            try:
                self.callback(key, value)
            except:
                # for now if there's an exception in the callback we ignore and move on
                pass
        # notify if the ttl thread is sleeping to wake up if the key it is sleeping on is deleted
        if del_index == 0:
            self.log("wake up ttl book keeper, it is sleeping on deleted key: {}".format(key))
            self.wake_event.set()
        return ret

    def find_remove_reheapify(self, key):
        del_index = -1
        if key in self:
            # find it, remove it and reheapify
            for i in range(0, len(self.heap)):
                if key == self.heap[i][1]:
                    del_index = i
                    self.heap[i] = self.heap[-1]
                    self.heap.pop()
                    if i < len(self.heap):
                        heapq._siftup(self.heap, i)
                        heapq._siftdown(self.heap, 0, i)
                    break
        return del_index

    def remove_on_ttl(self):
        while True:
            if len(self.heap) > 0:
                if time.time() - self.heap[0][0] >= self.ttl:
                    e = heapq.heappop(self.heap)
                    self.log("deleting element, ttl expired for key: {}".format(e[1]))
                    try:
                        del self[e[1]]
                    except:
                        self.log("element deleted before expiry kicked in: {}".format(e[1]))
                else:
                    # sleep until a delete event of the key happens
                    self.log("sleeping for {}s to hit ttl timout for key: {}".format(
                        self.ttl - (time.time() - self.heap[0][0]),
                        self.heap[0][1]))
                    self.wake_event.wait(timeout=self.ttl - (time.time() - self.heap[0][0]))
                    self.wake_event.clear()
            else:
                # heap is empty, wait until the first element is added
                # logging.debug("no elements in dict, sleep until an element gets added")
                self.wake_event.wait(timeout=10)
                self.wake_event.clear()
