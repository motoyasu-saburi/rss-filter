import tempfile
from datetime import datetime
from typing import List
from unittest import TestCase

from main import RssCollector


class TestRssCollector(TestCase):
    def test_exist_in_filter_list(self):
        temp_whitelist = tempfile.NamedTemporaryFile()
        temp_whitelist.write(b"")
        temp_whitelist.seek(0)
        rc = RssCollector(whitelist_dir=temp_whitelist.name)

        whitelist: List[str] = ["0000", "0000", "ABCDEF"]
        self.assertTrue(rc.exists_in_filter_list("test abcdefg test", whitelist))
        self.assertTrue(rc.exists_in_filter_list("ABCDEFG", whitelist))
        self.assertTrue(rc.exists_in_filter_list("ABCDEFGHI", whitelist))
        self.assertTrue(rc.exists_in_filter_list("123ABCDEFGHI", whitelist))

        self.assertFalse(rc.exists_in_filter_list("", whitelist))
        self.assertFalse(rc.exists_in_filter_list("123456", whitelist))

    def test_set_whitelist(self):
        temp_whitelist = tempfile.NamedTemporaryFile()
        temp_whitelist.write(b"ABCDEFG\n1234567")
        temp_whitelist.seek(0)

        whitelist_dir = temp_whitelist.name
        rc = RssCollector()
        rc.set_whitelist(whitelist_dir)
        self.assertEqual(rc.whitelist, ["ABCDEFG", "1234567"])

    def test_push_slack(self):
        pass
        # Comment out, because it includes side effect (write slack channel)
        # rc = RssCollector()
        # rc.push_slack()
        # self.assertEqual(rc.push_slack(), 200)

    def test_is_after_criteria_date(self):
        rc = RssCollector()

        before_date = datetime(2020, 12, 31, 12, 30, 30)
        after_date = datetime(2020, 12, 31, 12, 30, 31)

        self.assertTrue(rc.is_after_criteria_date(before_date, after_date))
        self.assertFalse(rc.is_after_criteria_date(after_date, before_date))

