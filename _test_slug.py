import re

def _cwd_to_session_slug(cwd):
    stripped = re.sub(r'^[/\\]', '', cwd)
    safe = re.sub(r'[/\\:]', '-', stripped)
    return f'--{safe}--'

cwd = r'C:\Projects\github\pi-mono'
result = _cwd_to_session_slug(cwd)
expected = '--C--Projects-github-pi-mono--'
print(f'result:   {result}')
print(f'expected: {expected}')
print(f'match: {result == expected}')
