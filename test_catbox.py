import requests

url = "https://catbox.moe/user/api.php"
files = {'fileToUpload': ('test.txt', 'hello world', 'text/plain')}
data = {'reqtype': 'fileupload'}
headers = {'Origin': 'https://nqbw.vercel.app'}

r = requests.post(url, files=files, data=data, headers=headers)
print(r.status_code)
print(r.text)
