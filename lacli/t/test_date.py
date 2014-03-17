# -*- coding: utf-8 -*-

from testtools import TestCase


class DateTest(TestCase):
    def setUp(self):
        super(DateTest, self).setUp()

    def tearDown(self):
        super(DateTest, self).tearDown()

    def test_epoch(self):
        from lacli.date import epoch

        self.assertEqual("1970-01-01T00:00:00+00:00", epoch().isoformat())
