import os
import glob

files = glob.glob('templates/*.html')
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to add color: white; to <h1 style="font-size: 
    if '<h1 style="font-size:' in content and 'color: white' not in content:
        content = content.replace('<h1 style="font-size:', '<h1 style="color: white; font-size:')
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {file}')
