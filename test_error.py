import requests
s = requests.Session()
s.get('https://nqbw.vercel.app/dashboard/login/')
s.post('https://nqbw.vercel.app/dashboard/login/', data={'username':'admin', 'password':'admin2026', 'csrfmiddlewaretoken': s.cookies['csrftoken']}, headers={'Referer': 'https://nqbw.vercel.app/dashboard/login/'})
files = {'image': ('test2.jpg', b'0' * 1024 * 1024, 'image/jpeg')}
data = {'title':'Test2', 'content':'Test content', 'is_published':'on', 'csrfmiddlewaretoken': s.cookies['csrftoken']}
r = s.post('https://nqbw.vercel.app/dashboard/news/add/', files=files, data=data, headers={'Referer': 'https://nqbw.vercel.app/dashboard/news/add/'}, allow_redirects=False)
lines = r.text.split('\n')
for i, line in enumerate(lines):
    if 'alert-error' in line and '<div' in line:
        print(lines[i+1].strip())
        print(lines[i+2].strip())
