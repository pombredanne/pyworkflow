import unittest

from ...test import WorkflowBackendTestCase
from ...process import *
from ...task import *
from ...activity import *
from ...decision import *

from pyworkflow.backend.memory import MemoryBackend
from . import BlinkerBackend

class BlinkerBackendTestCase(WorkflowBackendTestCase):
    def setUp(self):
        super(BlinkerBackendTestCase, self).setUp()
        self.backend = BlinkerBackend(MemoryBackend())

    def tearDown(self):
        super(BlinkerBackendTestCase, self).tearDown()

    def construct_backend(self):
        return self.backend

    def test_basic(self):
        signals = dict( s for s in BlinkerBackend.__dict__.items() if s[0][0:3] == 'on_' )

        received = []
        def make_logger(type):
            def log(sender, **kwargs):
                received.append((type, kwargs.keys()))
            return log

        loggers = dict( (name, make_logger(name)) for name in signals.keys() )
        for name, signal in signals.items():
            signal.connect(loggers[name])

        self.subtest_basic()
        
        # signal name, kwargs keys
        assert received == [
            ('on_process_started', ['process']), 
            ('on_process_started', ['process']), 
            ('on_process_canceled', ['process', 'reason', 'details']), 
            ('on_complete_decision_task', ['task', 'decisions']), 
            ('on_activity_scheduled', ['category', 'input', 'process', 'id', 'activity']),
            ('on_process_signaled', ['process', 'signal', 'data']), 
            ('on_complete_activity_task', ['task', 'result']), 
            ('on_activity_failed', ['reason','details','activity']), 
            ('on_complete_decision_task', ['task', 'decisions']), 
            ('on_activity_scheduled', ['category', 'input', 'process', 'id', 'activity']), 
            ('on_complete_activity_task', ['task', 'result']), 
            ('on_activity_aborted', ['details','activity']), 
            ('on_complete_decision_task', ['task', 'decisions']), 
            ('on_activity_scheduled', ['category', 'input', 'process', 'id', 'activity']), 
            ('on_complete_activity_task', ['task', 'result']), 
            ('on_activity_completed', ['result','activity']), 
            ('on_complete_decision_task', ['task', 'decisions']),
            ('on_process_completed', ['process', 'result']), 
        ]

        