import unittest
try:
    from multiprocessing import Process, Queue, Pipe
    disabled = False
except ImportError:
    Process = None
    Queue = None
    Pipe = None
    disabled = True

from iniparse import ini


class TestIni(unittest.TestCase):
    """Test sending INIConfig objects."""

    def test_queue(self):
        def getxy(_q, _w):
            _cfg = _q.get_nowait()
            _w.put(_cfg.x.y)
        cfg = ini.INIConfig()
        cfg.x.y = '42'
        q = Queue()
        w = Queue()
        q.put(cfg)
        p = Process(target=getxy, args=(q, w))
        p.start()
        self.assertEqual(w.get(timeout=1), '42')


class Suite(unittest.TestSuite):
    def __init__(self):
        if disabled:
            unittest.TestSuite.__init__(self, [])
        else:
            unittest.TestSuite.__init__(self, [
                    unittest.makeSuite(TestIni, 'test'),
            ])
