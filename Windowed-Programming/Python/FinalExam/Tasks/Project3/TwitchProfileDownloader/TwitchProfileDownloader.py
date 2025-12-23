import requests
import os

client_id = '9cpeh3x1xtijcq33ew3908v6o8uvqz'
access_token = 'irzkl3ti13la3wismsiki71h6akjw9'
username = 'tenz'

headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {access_token}'
}

def get_user_info(username):
    url = 'https://api.twitch.tv/helix/users'
    params = {'login': username}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    data = res.json()['data'][0]
    return data['profile_image_url'], data['offline_image_url'], data['display_name']

def download_image(url, filename):
    res = requests.get(url)
    res.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(res.content)
    print(f"Saved: {filename}")

avatar_url, banner_url, display_name = get_user_info(username)
os.makedirs(f"./{username}", exist_ok=True)
download_image(avatar_url, f"./{username}/avatar.jpg")
download_image(banner_url, f"./{username}/banner.jpg")
