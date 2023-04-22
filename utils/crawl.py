import json
import re
import requests
from datetime import datetime

from core.settings import BASE_LINK


def login_into_instagram(username, password) -> bool | tuple:
    # Get the login page to extract the CSRF token
    response = requests.get(BASE_LINK + '/accounts/login/')
    # Extract the script data containing the CSRF token
    script_data = re.findall(
        r'requireLazy\(\["JSScheduler","ServerJS","ScheduledApplyEach"\],function\(JSScheduler,ServerJS,ScheduledApplyEach\){(.*?)</script>',
        response.text)[0]

    # Extract the CSRF token from the script data and load it as JSON
    nest1 = re.search(r'csrf_token', script_data)
    csrf_token = '{"' + script_data[nest1.span()[0]:nest1.span()[-1] + 39] + '}'
    csrf_token = csrf_token.replace('\\', '')
    csrf_token = json.loads(csrf_token)

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{password}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    login_header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120"
                      "Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE_LINK}/accounts/login/",
        "X-CSRFTOKEN": csrf_token['csrf_token']
    }

    # Send the login request and get the response
    login_response = requests.post(BASE_LINK + '/accounts/login/ajax/', data=payload, headers=login_header)

    try:
        if login_response.json()["authenticated"]:
            cookies = login_response.cookies
            return True, cookies.get_dict()
        else:
            return False
    except KeyError:
        return False


def get_followers_list(data):
    # Set headers with user-agent and csrf token
    login_header = {
        "User-Agent": 'Instagram 146.0.0.27.125 (iPhone12,1; iOS 13_3; en_US; en-US; scale=2.00; 1656x3584; 190542906)',
        "Referer": f"https://www.instagram.com/{data['user']['username']}/followers/",
        "X-CSRFTOKEN": data['csrftoken']
    }

    # Set cookies with user data
    cookies = {
        'csrftoken': data['csrftoken'],
        'rur': data['rur'],
        'mid': data['mid'],
        'ds_user_id': data['ds_user_id'],
        'ig_did': data['ig_did'],
        'sessionid': data['sessionid']
    }

    data = requests.get(
        f'{BASE_LINK}/api/v1/users/web_profile_info/?username={data["user"]["username"]}',
        cookies=cookies, headers=login_header)

    data.raise_for_status()
    _id = data.json()['data']['user']['id']

    # Set query hash and variables for graphql call
    params = {'query_hash': '37479f2b8209594dde7facb0d904896a', 'variables': '{"first":50}'}
    parsed_vars = json.loads(params['variables'])
    parsed_vars['id'] = _id

    followers = list()

    while True:
        params['variables'] = json.dumps(parsed_vars)

        content = requests.get(BASE_LINK + '/graphql/query', params=params,
                               headers=login_header, cookies=cookies, allow_redirects=False)

        if content.status_code != 200:
            return None

        for node in content.json()['data']['user']['edge_followed_by']['edges']:
            followers.append(node['node']['username'])

        if not content.json()['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            return followers

        parsed_vars['after'] = content.json()['data']['user']['edge_followed_by']['page_info']['end_cursor']
        # Update after variable in parsed_vars with end_cursor of current page for next page
