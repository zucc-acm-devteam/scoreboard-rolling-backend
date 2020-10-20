import re
import base64
from spider_http import SpiderHttp

spider_http = SpiderHttp()


def login(username, password, contest_id):
    code = base64.b64encode('{}:{}'.format(username, password).encode('utf-8')).decode('utf-8')
    spider_http.headers.update({
        'Authorization': 'Basic {}'.format(code)
    })
    url = 'http://10.66.28.6:12345/api/v4/contests/{}/scoreboard?public=false'.format(contest_id)
    res = spider_http.get(url=url)
    print(res.json())
    url = 'http://10.66.28.6:12345/api/v4/contests/{}/scoreboard?public=true'.format(contest_id)
    res = spider_http.get(url=url)
    print(res.json())


if __name__ == '__main__':
    login('smz', 'smzsmzsmz', 5)
