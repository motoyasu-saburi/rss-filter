from typing import List, Optional

import feedparser
from dataclasses import dataclass

@dataclass
class Cve:
    url: str
    description: str


class RssCollector:
    whitelist: List[Optional[str]]  #
    WHITELIST_DIR = ""  # TODO
    RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"

    def __init__(self):
        self.set_whitelist("")  # TODO

    def set_whitelist(self, whitelist_dir: str) -> None:
        with open(whitelist_dir) as f:
            file_content = f.read()
            self.whitelist = file_content.split("\n")

    def exist_in_filter_list(self, summary: str, whitelists: List[Optional[str]]) -> bool:
        for wl in whitelists:
            if summary in wl:
                return True
        return False

    def push_slack(self):
        pass  # TODO

    def main(self):
        full_cve_list = feedparser.parse(self.RSS_URL).entries
        cve_list: List[Cve] = list(map(lambda cve: Cve(url=cve.id, description=cve.summary), full_cve_list))
        filtered_cve_list: List[Cve] = list(filter(lambda cve: self.exist_in_filter_list(cve.description, self.whitelist), cve_list))
        print(filtered_cve_list)


if __name__ == '__main__':
    r = RssCollector()
    r.main()
