import os
import glob
import re

files = glob.glob('templates/*.html') + glob.glob('templates/**/*.html')

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Target <h1 style="font-size:...">
    content = re.sub(r'<h1\s+style="(?![^"]*color:\s*white)font-size:', r'<h1 style="color: white; font-size:', content)
    
    # Target <h1 style="color: var(--primary)...">
    content = re.sub(r'<h1\s+style="color:\s*var\(--primary\)', r'<h1 style="color: white', content)

    # Target <p style="font-size:... opacity:...">
    content = re.sub(r'<p\s+style="(?![^"]*color:\s*white)font-size:([^"]*opacity)', r'<p style="color: white; font-size:\1', content)

    if content != original_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {file}')
