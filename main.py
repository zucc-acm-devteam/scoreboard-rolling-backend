import json
import math
from datetime import datetime, timedelta
import base64
from spider_http import SpiderHttp

spider_http = SpiderHttp()


def strptimedelta(time_str: str, format_str: str) -> timedelta:
    temp = datetime.strptime(time_str, format_str)
    return temp - datetime(1900, 1, 1)


def get_data(full_file_name, address, username, password, contest_id):
    code = base64.b64encode('{}:{}'.format(username, password).encode('utf-8')).decode('utf-8')
    spider_http.headers.update({
        'Authorization': 'Basic {}'.format(code)
    })
    result = {
        'success': False,
        'data': {}
    }
    try:
        url = '{}/api/v4/contests/{}/problems'.format(address, contest_id)
        res = spider_http.get(url=url).json()
        problems = {
            problem['id']: problem['label']
            for problem in res
        }
        url = '{}/api/v4/contests/{}'.format(address, contest_id)
        res = spider_http.get(url=url).json()
        start_time = datetime.strptime(res['start_time'], "%Y-%m-%dT%H:%M:%S%z")
        end_time = datetime.strptime(res['end_time'], "%Y-%m-%dT%H:%M:%S%z")
        freeze_time = end_time - strptimedelta(res['scoreboard_freeze_duration'], "%H:%M:%S.%f")
        contest_meta = {
            'name': res['name'],
            'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'freeze_time': freeze_time.strftime("%Y-%m-%d %H:%M:%S"),
            'penalty': res['penalty_time'],
            'problems': [j for i, j in problems.items()],
            'teams': []
        }
        url = '{}/api/v4/contests/{}/teams?public=true'.format(address, contest_id)
        res = spider_http.get(url=url).json()
        teams = {
            team['id']: {
                'name': team['name'],
                'submissions': []
            }
            for team in res
        }
        for team in res:
            contest_meta['teams'].append(team['id'])
        url = '{}/api/v4/contests/{}/judgement-types'.format(address, contest_id)
        res = spider_http.get(url=url).json()
        judgement_types_filter = {
            judgement_type['id']: judgement_type['solved'] or judgement_type['penalty']
            for judgement_type in res
        }
        url = '{}/api/v4/contests/{}/judgements'.format(address, contest_id)
        res = spider_http.get(url=url).json()
        judgements = {
            judgement['submission_id']: judgement['judgement_type_id']
            for judgement in res if judgement['valid'] and judgement_types_filter[judgement['judgement_type_id']]
        }

        url = '{}/api/v4/contests/{}/submissions'.format(address, contest_id)
        res = spider_http.get(url=url).json()
        for submission in res:
            time = datetime.strptime(submission['time'], "%Y-%m-%dT%H:%M:%S.%f%z")
            if submission['team_id'] in teams.keys():
                teams[submission['team_id']]['submissions'].append({
                    'problem': problems[submission['problem_id']],
                    'pending': time > freeze_time,
                    'result': judgements[submission['id']],
                    'time': math.floor((time - start_time).total_seconds() / 60)
                })
        result['data'] = {
            'contest_meta': contest_meta,
            'teams': teams
        }
        result['success'] = True
    except Exception as e:
        result['data'] = {
            'error': str(e)
        }
        print(str(e))
    with open(full_file_name, 'w') as fp:
        json.dump(result, fp)


if __name__ == '__main__':
    from secure import username, password, address

    get_data('data.json', address, username, password, 5)
