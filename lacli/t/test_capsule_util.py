# -*- coding: utf-8 -*-

from testtools import TestCase


class CapsuleUtilTest(TestCase):
    def setUp(self):
        super(CapsuleUtilTest, self).setUp()

    def tearDown(self):
        super(CapsuleUtilTest, self).tearDown()

    def test_archive_capsule(self):
        from lacli.capsule import archive_capsule
        from lacore.adf.elements import Links
        self.assertEqual(None, archive_capsule({}))
        self.assertEqual(None, archive_capsule(
            {'links': Links()}))
        self.assertEqual(None, archive_capsule(
            {'links': Links(upload='foo')}))
        self.assertEqual(None, archive_capsule(
            {'links': Links(upload='http://foo')}))
        self.assertEqual(None, archive_capsule(
            {'links': Links(upload='http://foo#whateva')}))
        self.assertEqual('bar', archive_capsule(
            {'links': Links(upload='http://foo#C:bar:')}))
        self.assertEqual('bar bar', archive_capsule(
            {'links': Links(upload='http://foo#C:bar%20bar:')}))

    def test_archive_uri(self):
        from lacli.capsule import archive_uri

        self.assertEqual('bar', archive_uri('bar'))
        self.assertEqual('bar#C:lol:', archive_uri('bar', 'lol'))
        self.assertEqual('bar#C:lol%20fof:', archive_uri('bar', 'lol fof'))
        self.assertEqual('bar#C:lol%3Afof:', archive_uri('bar', 'lol:fof'))
        self.assertEqual('bar#C:%CE%B3%CE%BA:', archive_uri('bar', u'γκ'))
        self.assertRaises(AssertionError, archive_uri, 'bar#foo', 'lol')
