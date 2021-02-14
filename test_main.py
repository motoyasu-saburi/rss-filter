import os
from typing import List
from unittest import TestCase

from main import RssCollector


class TestRssCollector(TestCase):
    def test_exist_in_filter_list(self):
        rc = RssCollector()

        whitelist: List[str] = ["0000", "0000", "ABCDEF"]
        self.assertTrue(rc.exist_in_filter_list("test abcdefg test", whitelist))
        self.assertTrue(rc.exist_in_filter_list("ABCDEFG", whitelist))
        self.assertTrue(rc.exist_in_filter_list("ABCDEFGHI", whitelist))
        self.assertTrue(rc.exist_in_filter_list("123ABCDEFGHI", whitelist))

        self.assertFalse(rc.exist_in_filter_list("", whitelist))
        self.assertFalse(rc.exist_in_filter_list("123456", whitelist))

    def test_set_whitelist(self):
        rc = RssCollector()
        whitelist_dir = os.getcwd() + "/test/test_whitelist.txt"
        rc.set_whitelist(whitelist_dir)

        expect: List[str] = ["ABCDEFG", "1234567"]
        self.assertEqual(rc.whitelist, expect)

    def test_push_slack(self):
        pass
        # Comment out, because it includes side effect (write slack channel)
        # rc = RssCollector()
        # rc.push_slack()
        # self.assertEqual(rc.push_slack(), 200)
