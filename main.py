from typing import List

import feedparser
from dataclasses import dataclass

@dataclass
class Cve:
    url: str
    description: str

class RssCollector:

    whitelist: List[str] #

    # TODO any url from url list files
    RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"

    def exist_in_filter_list(self, summary: str) -> bool:
        # TODO
        # read whitelist
        return "whitelist" in summary

    def main(self):
        full_cve_list = feedparser.parse(self.RSS_URL).entries
        cve_list: List[Cve] = list(map(lambda cve: Cve(url=cve.id, description=cve.summary), full_cve_list))
        list(filter(lambda cve: cve, cve_list))


if __name__ == '__main__':
    r = RssCollector()
    r.main()
