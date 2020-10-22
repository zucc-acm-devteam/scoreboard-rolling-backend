import json
import base64
from spider_http import SpiderHttp

spider_http = SpiderHttp()


def get_data(full_file_name, username, password, contest_id):
    code = base64.b64encode('{}:{}'.format(username, password).encode('utf-8')).decode('utf-8')
    spider_http.headers.update({
        'Authorization': 'Basic {}'.format(code)
    })
    result = {
        'success': False,
        'data': {}
    }
    try:
        url = 'http://10.66.28.6:12345/api/v4/contests/{}/scoreboard?public=false'.format(contest_id)
        res = spider_http.get(url=url)
        result['data']['final'] = res.json()['rows']
        url = 'http://10.66.28.6:12345/api/v4/contests/{}/scoreboard?public=true'.format(contest_id)
        res = spider_http.get(url=url)
        result['data']['pending'] = res.json()['rows']
        result['success'] = True
    except Exception as e:
        result['data']['error'] = str(e)
    with open(full_file_name, 'w') as fp:
        json.dump(result, fp)


if __name__ == '__main__':
    from secure import username, password
    get_data('data.json', username, password, 5)
