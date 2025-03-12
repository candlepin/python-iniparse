import unittest
try:
    from multiprocessing import Process, Queue, Pipe, get_start_method, get_context
    disabled = False
except ImportError:
    Process = None
    Queue = None
    Pipe = None
    disabled = True

from iniparse import ini


class TestIni(unittest.TestCase):
    """Test sending INIConfig objects."""

    # Since Python 3.14 on non-macOS POSIX systems
    # the default method has been changed to forkserver.
    # The code in this module does not work with it,
    # hence the explicit change to 'fork'
    # See https://github.com/python/cpython/issues/125714
    if get_start_method() == "forkserver":
        _mp_context = get_context(method="fork")
    else:
        _mp_context = get_context()

    def test_queue(self):
        def getxy(_q, _w):
            _cfg = _q.get_nowait()
            _w.put(_cfg.x.y)
        cfg = ini.INIConfig()
        cfg.x.y = '42'
        q = Queue()
        w = Queue()
        q.put(cfg)
        p = self._mp_context.Process(target=getxy, args=(q, w))
        p.start()
        self.assertEqual(w.get(timeout=1), '42')
