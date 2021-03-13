import json

from main import RssCollector


def lambda_handler(event, context):
    rsscon = RssCollector()
    result = rsscon.main()

    if result == False:
        return {
            'statusCode': 500,
            'body': json.dumps('Server Error')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
