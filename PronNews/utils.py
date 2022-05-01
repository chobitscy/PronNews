import re

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


def figure_from_str(text: str):
    try:
        return int(''.join(re.findall(r"\d+", text)))
    except ValueError:
        return 0


def size_to_MIB(size: str):
    number = float(re.findall(r"\d+\.?\d*", size)[0])
    if size.find('GiB') != -1:
        return number * 1024
    elif size.find('MiB') != -1:
        return number
