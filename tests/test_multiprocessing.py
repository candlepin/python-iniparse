import unittest
try:
    from multiprocessing import Process, Queue, Pipe
    disabled = False
except ImportError:
    disabled = True

from iniparse import compat, ini

def get_x_dot_y(readfn, writefn):
    cfg = readfn(timeout=3)
    writefn(cfg.x.y)

class test_ini(unittest.TestCase):
    """Test sending INIConfig objects."""

    def test_queue(self):
        cfg = ini.INIConfig()
        cfg.x.y = 42
        q1 = Queue()
        q2 = Queue()
        p = Process(target=get_x_dot_y, args=(q1.get, q2.put))
        q1.put(cfg)
        self.assertEqual(q2.get(timeout=3), 42)

    def test_pipe(self):
        cfg = ini.INIConfig()
        cfg.x.y = 42
        c1, c2 = Pipe()
        p = Process(target=get_x_dot_y, args=(c1.recv ,c2.send))
        c1.send(cfg)
        self.assertEqual(c2.recv(timeout=3), 42)

class suite(unittest.TestSuite):
    def __init__(self):
        if disabled:
            unittest.TestSuite.__init__(self, [])
        else:
            unittest.TestSuite.__init__(self, [
                    unittest.makeSuite(test_ini, 'test'),
            ])
