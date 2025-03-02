import requests
import os
import re
import sys
import time
from requests.exceptions import RequestException

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f'[!] File Not Found Please Enter File Patch: {file_path}')
        return None

def make_request(url, headers, cookie):
    try:
        response = requests.get(url, headers=headers, cookies={'Cookie': cookie})
        return response.text
    except RequestException as e:
        print(f'[!] Error making request: {e}')
        return None

def get_valid_cookies(cookies_data):
    valid_cookies = []
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 '
            'Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
        )
    }

    for cookie in cookies_data:
        response = make_request('https://business.facebook.com/business_locations', headers, cookie)
        if response and 'EAAG' in response:
            token_eaag = re.search(r'(EAAG\w+)', response)
            if token_eaag:
                valid_cookies.append((cookie, token_eaag.group(1)))
    return valid_cookies

def post_comment(post_id, commenter_name, comment, cookie, token_eaag):
    data = {'message': f'{commenter_name}: {comment}', 'access_token': token_eaag}
    try:
        response = requests.post(
            f'https://graph.facebook.com/{post_id}/comments/',
            data=data,
            cookies={'Cookie': cookie}
        )
        return response
    except RequestException as e:
        print(f'[!] Error posting comment: {e}')
        return None

def main():
    
    cookies_file_path = input("Enter the path to the cookies file: ").strip()
    comments_file_path = input("Enter the path to the comments file: ").strip()
    commenter_name = input("Enter the commenter's name: ").strip()
    post_id = input("Enter the Post ID: ").strip()
    delay = int(input("Enter the delay between comments (in seconds): ").strip())

    
    cookies_data = read_file(cookies_file_path)
    comments = read_file(comments_file_path)

    if not cookies_data or not comments:
        return

    valid_cookies = get_valid_cookies(cookies_data)
    if not valid_cookies:
        print('[!] No valid cookies found. Exiting...')
        return

    x, cookie_index = 0, 0

    while True:
        try:
            time.sleep(delay)
            comment = comments[x].strip()
            current_cookie, token_eaag = valid_cookies[cookie_index]

            response = post_comment(post_id, commenter_name, comment, current_cookie, token_eaag)
            if response and response.status_code == 200:
                print(f'Successfully sent comment: {commenter_name}: {comment}')
                x = (x + 1) % len(comments)
                cookie_index = (cookie_index + 1) % len(valid_cookies)
            else:
                print(f'Failed to send comment: {commenter_name}: {comment}')
                cookie_index = (cookie_index + 1) % len(valid_cookies)

        except Exception as e:
            print(f'[!] An unexpected error occurred: {e}')
            time.sleep(5.5)  

if __name__ == '__main__':
    main()