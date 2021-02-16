import os
from http import client
from typing import List, Optional

import feedparser
from dataclasses import dataclass

@dataclass
class Cve:
    title: str
    url: str
    description: str


class RssCollector:
    whitelist: List[Optional[str]]  #

    WHITELIST_DIR = os.getcwd() + "/resource/whitelist.txt"
    RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"
    SLACK_INCOMING_WEBHOOK_URL_PATH: str

    def __init__(self):
        self.set_whitelist(self.WHITELIST_DIR)
        # TODO change Env to Arg
        self.SLACK_INCOMING_WEBHOOK_URL_PATH = ""
        #self.SLACK_INCOMING_WEBHOOK_URL_PATH = os.environ.get("INCOMING_WEBHOOK_PATH")  # Do not include domain.
        #if self.SLACK_INCOMING_WEBHOOK_URL_PATH is None:
        #    raise Exception("Environment variable ( 'INCOMING_WEBHOOK_PATH' )  is not set.")

    def set_whitelist(self, whitelist_dir: str) -> None:
        def __filter_duplicate_and_invalid_value(wl: List[str]) -> List[str]:
            filtered_invalid_list: List[str] = list(filter(lambda target: target != "", wl))
            return list(sorted(set(filtered_invalid_list), key=filtered_invalid_list.index))  # filter duplicate value

        with open(whitelist_dir) as f:
            file_content = f.read()
            self.whitelist = __filter_duplicate_and_invalid_value(file_content.split("\n"))


    def exist_in_filter_list(self, summary: str, whitelists: List[Optional[str]]) -> bool:
        lower_summary = summary.lower()
        for wl in whitelists:
            if wl.lower() in lower_summary:
                return True
        return False

    def push_cve_to_slack(self, cves: List[Cve]) -> int:
        SLACK_DOMAIN = "hooks.slack.com"
        WEB_HOOK_PATH = self.SLACK_INCOMING_WEBHOOK_URL_PATH
        WEB_HOOK_METHOD = "POST"
        httpclient = client.HTTPSConnection(SLACK_DOMAIN)
        headers = {"Content-type": "application/json"}

        for cve in cves:
            text_body = f"<{cve.url}|{cve.title}>\n{cve.description}"
            body = '{"text": "' + text_body + '"}'
            httpclient.request(method=WEB_HOOK_METHOD, url=WEB_HOOK_PATH, headers=headers, body=body)
            httpclient.close()
        return 200 # response_status

    def main(self):
        full_cve_list = feedparser.parse(self.RSS_URL).entries
        cve_list: List[Cve] = list(map(lambda cve: Cve(title=cve.title, url=cve.id, description=cve.summary), full_cve_list))
        filtered_cve_list: List[Cve] = list(filter(lambda cve: not self.exist_in_filter_list(cve.description, self.whitelist), cve_list))
        self.push_cve_to_slack(filtered_cve_list)


if __name__ == '__main__':
    r = RssCollector()
    r.main()
