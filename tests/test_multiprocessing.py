import unittest
try:
    from multiprocessing import Process, Queue, Pipe
    disabled = False
except ImportError:
    disabled = True

from iniparse import compat, ini

class test_ini(unittest.TestCase):
    """Test sending INIConfig objects."""

    def test_queue(self):
        def getxy(q, w):
            cfg = q.get_nowait()
            w.put(cfg.x.y)
        cfg = ini.INIConfig()
        cfg.x.y = '42'
        q = Queue()
        w = Queue()
        q.put(cfg)
        p = Process(target=getxy, args=(q, w))
        p.start()
        self.assertEqual(w.get(timeout=1), '42')

class suite(unittest.TestSuite):
    def __init__(self):
        if disabled:
            unittest.TestSuite.__init__(self, [])
        else:
            unittest.TestSuite.__init__(self, [
                    unittest.makeSuite(test_ini, 'test'),
            ])
