import os
from http import client
from typing import List, Optional

import feedparser
from dataclasses import dataclass

import argparse

@dataclass
class Cve:
    url: str
    description: str


class RssCollector:
    whitelist: List[Optional[str]]

    WHITELIST_DIR = os.getcwd() + "/resource/whitelist.txt"
    RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"
    SLACK_INCOMING_WEBHOOK_URL_PATH: str

    def __init__(self):
        print("-------------------------")
        self.parse_arguments()
        print("-------------------------")

        self.set_whitelist(self.WHITELIST_DIR)
        # TODO change Env to Arg
        self.SLACK_INCOMING_WEBHOOK_URL_PATH = os.environ.get("INCOMING_WEBHOOK_PATH")  # Do not include domain.
        if self.SLACK_INCOMING_WEBHOOK_URL_PATH is None:
            raise Exception("Environment variable ( 'INCOMING_WEBHOOK_PATH' )  is not set.")

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('incoming_webhook_path',
                            type=str,
                            metavar='N',
                            help='webhook path')
        # parser.add_argument('--sum',
        #                     dest='accumulate',
        #                     action='store_const',
        #                     const=sum,
        #                     default=max,
        #                     help='sum the integers (default: find the max)')

        args = parser.parse_args()
        print(args.accumulate(args.incoming_webhook_path))

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

    def push_cve_to_slack(self, payload: List[Cve]) -> int:
        SLACK_DOMAIN = "hooks.slack.com"
        WEB_HOOK_PATH = self.SLACK_INCOMING_WEBHOOK_URL_PATH
        WEB_HOOK_METHOD = "POST"

        httpclient = client.HTTPSConnection(SLACK_DOMAIN)
        headers = {"Content-type": "application/json"}
        body = "{'text': 'python request test'}"  # TODO replace filtered cve
        httpclient.request(method=WEB_HOOK_METHOD, url=WEB_HOOK_PATH, headers=headers, body=body)
        response_status: int = httpclient.getresponse().status
        httpclient.close()
        return response_status

    def main(self):
        full_cve_list = feedparser.parse(self.RSS_URL).entries
        cve_list: List[Cve] = list(map(lambda cve: Cve(url=cve.id, description=cve.summary), full_cve_list))
        filtered_cve_list: List[Cve] = list(filter(lambda cve: self.exist_in_filter_list(cve.description, self.whitelist), cve_list))
        print(filtered_cve_list)


if __name__ == '__main__':
    r = RssCollector()
    r.main()
