# -*- coding: utf-8 -*-
import os
import crochet

from testtools import TestCase
from twisted.internet import defer
from . import makeprefs
from mock import patch, Mock


class ServerTest(TestCase):

    @classmethod
    def setup_class(cls):
        crochet.setup()

    def setUp(self):
        super(ServerTest, self).setUp()
        self.prefs = makeprefs()
        self.home = os.path.join('t', 'data', 'home')

    def tearDown(self):
        super(ServerTest, self).tearDown()

    def _makeit(self, *args, **kwargs):
        from lacli.server import LaServerCommand
        return LaServerCommand(*args, **kwargs)

    def ttypes(self):
        from lacli.server.interface.ClientInterface import ttypes
        return ttypes

    @crochet.wait_for(2.0)
    @defer.inlineCallbacks
    def test_get_latest_version(self):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        with patch('lacli.server.__version__', new='1.2.3'):
            s = self._makeit(registry)
            v = yield s.GetVersion()
            self.assertEqual(
                v, self.ttypes().VersionInfo('1.2.3'))
            with patch('treq.get') as get:
                with patch('treq.content') as content:
                    content.return_value = "{}"
                    phrase = self.getUniqueString()
                    rsp = Mock(code=400, phrase=phrase)
                    get.return_value = defer.succeed(rsp)
                    v = yield s.GetLatestVersion()
                    self.assertEqual(
                        v, self.ttypes().VersionInfo('1.2.3'))

    @crochet.wait_for(2.0)
    @defer.inlineCallbacks
    def test_get_latest_version_from_api(self):
        registry = Mock()
        registry.prefs = self.prefs
        registry.new_session.return_value.async_account = defer.succeed(
            {'email': 'foo'})
        with patch('lacli.server.__version__', new='1.2.3'):
            s = self._makeit(registry)
            with patch('treq.get') as get:
                with patch('treq.content') as content:
                    content.return_value = '{"version": "3.2.1"}'
                    rsp = Mock(code=200)
                    get.return_value = defer.succeed(rsp)
                    v = yield s.GetLatestVersion()
                    self.assertEqual(
                        v, self.ttypes().VersionInfo('3.2.1'))
