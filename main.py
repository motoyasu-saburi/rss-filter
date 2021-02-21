import os
from datetime import datetime
from http import client
from typing import List, Optional, Any

import feedparser
from dataclasses import dataclass


@dataclass
class Cve:
    title: str
    url: str
    description: str
    date: datetime


class RssCollector:
    whitelist: List[Optional[str]]
    WEBHOOK_ENV_NAME = "CVE_ALERT_WEBHOOK_PATH"
    CVE_ALERT_WEBHOOK_PATH: str
    whitelist_dir: str = os.getcwd() + "/resource/whitelist.txt"
    RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"
    SLACK_INCOMING_WEBHOOK_URL_PATH: str

    def __init__(self, whitelist_dir=f"{os.getcwd()}/resource/whitelist.txt"):
        self.whitelist_dir = whitelist_dir
        self.set_whitelist(self.whitelist_dir)
        self.SLACK_INCOMING_WEBHOOK_URL_PATH = os.environ.get(self.WEBHOOK_ENV_NAME)
        if self.SLACK_INCOMING_WEBHOOK_URL_PATH is None:
            raise Exception(f"Environment variable ( '{self.WEBHOOK_ENV_NAME}' )  is not set.")

    def set_whitelist(self, whitelist_dir: str) -> None:
        def __filter_duplicate_and_invalid_value(wl: List[str]) -> List[str]:
            filtered_invalid_list: List[str] = list(filter(lambda target: target != "", wl))
            return list(sorted(set(filtered_invalid_list), key=filtered_invalid_list.index))  # filter duplicate value

        with open(whitelist_dir) as f:
            file_content = f.read()
            self.whitelist = __filter_duplicate_and_invalid_value(file_content.split("\n"))

    def is_after_criteria_date(self, criteria_date: datetime, filter_target_date: datetime):
        return criteria_date < filter_target_date

    def exists_in_filter_list(self, summary: str, whitelists: List[Optional[str]]) -> bool:
        lower_summary = summary.lower()
        for wl in whitelists:
            if wl.lower() in lower_summary:
                return True
        return False

    def push_cve_to_slack(self, cves: List[Cve], webhook_url_path: str, host="hooks.slack.com") -> int:
        WEB_HOOK_METHOD = "POST"
        httpclient = client.HTTPSConnection(host)
        headers = {"Content-type": "application/json"}
        last_status_code: int

        for cve in cves:
            text_body = f"<{cve.url}|{cve.title}>\n{cve.description}"
            body = '{"text": "' + text_body + '"}'
            httpclient.request(method=WEB_HOOK_METHOD, url=webhook_url_path, headers=headers, body=body)
            last_status_code = httpclient.getresponse().status
            httpclient.close()

        # TODO check all status code.
        return last_status_code  # response_status

    def get_cve(self) -> List[Cve]:
        def __get_cve_feed_from_rss() -> Any:
            return feedparser.parse(self.RSS_URL).entries

        cve_list: Any = __get_cve_feed_from_rss()
        return list(
            map(lambda cve: Cve(
                title=cve.title,
                url=cve.id,
                description=cve.summary,
                date=datetime.strptime(cve.date, "%Y-%m-%dT%H:%M:%SZ")
            ), cve_list)
        )

    def main(self):
        full_cve_list = self.get_cve()
        filtered_cve_list: List[Cve] = list(
            filter(lambda cve: (
                    not self.exists_in_filter_list(cve.description, self.whitelist)
                    and self.is_after_criteria_date(datetime.now(), cve.date)
            ), full_cve_list)
        )
        self.push_cve_to_slack(cves=filtered_cve_list, webhook_url_path=self.SLACK_INCOMING_WEBHOOK_URL_PATH)


if __name__ == '__main__':
    r = RssCollector()
    r.main()
