import requests

client_id = '9cpeh3x1xtijcq33ew3908v6o8uvqz'
client_secret = 'sihgy6vmaabs3m5nkownsqjw2shzpj'

url = 'https://id.twitch.tv/oauth2/token'
params = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'client_credentials'
}

response = requests.post(url, params=params)
access_token = response.json()['access_token']
print("OAuth Token:", access_token)
