import unittest
import logbook
import time
from concert.tests import VisitChecker
from concert.base import wait
from concert.events.dispatcher import Dispatcher
from concert.devices.dummy import DummyDevice

SLEEP_TIME = 0.005


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = Dispatcher()
        self.checker = VisitChecker()
        self.handler = logbook.TestHandler()
        self.handler.push_thread()

    def tearDown(self):
        self.handler.pop_thread()

    def test_subscription(self):
        self.dispatcher.subscribe(self, 'foo', self.checker.visit)
        self.dispatcher.send(self, 'foo')
        time.sleep(SLEEP_TIME)
        self.assertTrue(self.checker.visited)

    def test_unsubscription(self):
        self.dispatcher.subscribe(self, 'foo', self.checker.visit)
        self.dispatcher.unsubscribe(self, 'foo', self.checker.visit)
        self.dispatcher.send(self, 'foo')
        time.sleep(SLEEP_TIME)
        self.assertFalse(self.checker.visited)
