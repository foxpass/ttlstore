import time
import unittest

from ttlstore import TTLStore

# reference for test cases: https://github.com/mailgun/expiringdict/blob/master/tests/expiringdict_test.py 

class TTLStoreTestCases(unittest.TestCase):

    def test_create(self):
        with self.assertRaises(Exception):
            TTLStore()

        d = TTLStore(ttl=1)
        self.assertEqual(len(d), 0)

    def test_basics(self):
        d = TTLStore(ttl=0.01)

        with self.assertRaises(KeyError):
            d['a']

        d['a'] = 'x'
        self.assertEqual(d['a'], 'x')

        d['a'] = 'y'
        self.assertEqual(d['a'], 'y')

        self.assertEqual('b' not in d, True)
        d['b'] = 'y'
        self.assertEqual('b' in d, True)

        time.sleep(0.012)

        self.assertEqual('b' not in d, True)
        self.assertEqual('a' not in d, True)

        d['c'] = 'x'
        d['d'] = 'y'
        d['e'] = 'z'

        self.assertEqual('c' in d, True)
        self.assertEqual('d' in d, True)

        del d['e']
        self.assertEqual('e' not in d, True)

        time.sleep(0.012)
        self.assertEqual('c' not in d, True)
        self.assertEqual('d' not in d, True)

        d['c'] = 'x'
        d['d'] = 'y'
        time.sleep(0.006)
        d['e'] = 'f'
        time.sleep(0.006)
        self.assertEqual('c' not in d, True)
        self.assertEqual('d' not in d, True)
        self.assertEqual('e' in d, True)
        time.sleep(0.006)
        self.assertEqual('e' not in d, True)

    def test_pop(self):
        d = TTLStore(ttl=0.01)
        d['a'] = 'x'
        self.assertEqual('x', d.pop('a'))
        time.sleep(0.012)
        with self.assertRaises(KeyError):
            d.pop('a')

    def test_iter(self):
        d = TTLStore(ttl=0.01)
        self.assertEqual([k for k in d], [])
        d['a'] = 'x'
        d['b'] = 'y'
        d['c'] = 'z'
        self.assertEqual([k for k in d], ['a', 'b', 'c'])

        self.assertEqual([k for k in d.values()], ['x', 'y', 'z'])
        time.sleep(0.012)
        self.assertEqual([k for k in d.values()], [])

    def test_setdefault(self):
        d = TTLStore(ttl=0.01)
        self.assertEqual('x', d.setdefault('a', 'x'))
        self.assertEqual('x', d.setdefault('a', 'y'))

        time.sleep(0.012)

        self.assertEqual('y', d.setdefault('a', 'y'))

    def test_not_implemented(self):
        d = TTLStore(ttl=0.01)

        with self.assertRaises(NotImplementedError):
            d.clear()

        with self.assertRaises(NotImplementedError):
            d.popitem()

        with self.assertRaises(NotImplementedError):
            d.copy()

        with self.assertRaises(NotImplementedError):
            d.update('k', 5)

    def test_reset_of_key_no_trim(self):
        """Re-setting an existing key should not cause a non-expired key to be dropped"""
        d = TTLStore(ttl=10)
        d["a"] = "A"
        d["b"] = "B"

        d["b"] = "B"

        self.assertEqual("a" in d, True)

    def test_get(self):
        d = TTLStore(ttl=10)
        with self.assertRaises(KeyError):
            d['a']
        d['a'] = 'b'
        self.assertEqual(d.get('a'), 'b')

    def test_set(self):
        d = TTLStore(ttl=10)
        d.set('a', 'b')
        self.assertEqual(d.get('a'), 'b')


if __name__ == '__main__':
    unittest.main()
