import requests
import snowflake.client

from PronNews import settings


def get_snowflake_uuid():
    return snowflake.client.get_guid()


def schedule(task_list):
    for task in task_list:
        scrapyd = settings.SCRAPYD
        headers = {
            'Authorization': scrapyd['auth']
        }
        data = {
            'project': task['project'],
            'spider': task['spider']
        }
        response = requests.post('http://%s:%s/schedule.json' % (scrapyd['host'], scrapyd['port']), data=data,
                                 headers=headers)
        response.raise_for_status()
