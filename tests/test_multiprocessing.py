"""
:component: python-iniparse
:requirement: RHSS-291606
:polarion-project-id: RHELSS
:polarion-include-skipped: false
:polarion-lookup-method: id
:poolteam: rhel-sst-csi-client-tools
:caseautomation: Automated
:upstream: No
"""

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
        """
        :id: 14f275ae-3bcb-45d7-9999-0ce942b7c47f
        :title: INIConfig object can be sent between processes using multiprocessing.Queue
        :description:
            Verifies that an INIConfig object can be serialized, passed through a multiprocessing queue,
            and deserialized in another process while retaining access to nested values.
        :tags: Tier 1
        :steps:
            1. Create an empty INIConfig object and assign a nested value (`cfg.x.y = '42'`).
            2. Create two multiprocessing queues (`q` and `w`).
            3. Put the INIConfig object into queue `q`.
            4. Start a new process which pulls the config from `q`, reads `x.y`, and puts it into queue `w`.
            5. Wait for a result from queue `w` with a timeout.
            6. Assert that the value returned is the original nested value.
        :expectedresults:
            1. INIConfig object is created and contains nested key-value structure.
            2. Multiprocessing queues are initialized successfully.
            3. Config is successfully placed into the first queue.
            4. New process starts and retrieves the config object from the queue.
            5. The nested value is accessed without error and placed into the second queue.
            6. The main process retrieves the correct value from queue `w` and matches it against expected result.
        """
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
