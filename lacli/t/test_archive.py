# -*- coding: utf-8 -*-
from testtools import TestCase


class ArchiveTest(TestCase):
    def setUp(self):
        super(ArchiveTest, self).setUp()

    def tearDown(self):
        super(ArchiveTest, self).tearDown()

    def test_archive_handle(self):
        from lacli.archive import archive_handle
        self.assertEqual('ff612b0d511eaf22c4b50c2ba1e98260',
                         archive_handle(['foo', 'bar']))
