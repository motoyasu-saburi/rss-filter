from unittest import TestCase

from main import RssCollector


class TestRssCollector(TestCase):
    def test_exist_in_filter_list(self):
        rc = RssCollector()
        rc.exist_in_filter_list()
