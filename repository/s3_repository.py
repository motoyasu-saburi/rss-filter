from dataclasses import dataclass
from datetime import datetime

import boto3
import json

@dataclass
class S3Repository:
    # TODO
    BUCKET_NAME = 'cve-filter'
    OBJECT_KEY_NAME = 'last-execution-time.txt'

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    obj = bucket.Object(OBJECT_KEY_NAME)

    def save_execute_datetime(self, exec_date_time: datetime) -> None:
        self.obj.put(Body=str(exec_date_time))

    def get_previous_exec_time(self) -> datetime:
        response = self.obj.get()
        body = response['Body'].read()
        return json.loads(body.decode('utf-8'))
