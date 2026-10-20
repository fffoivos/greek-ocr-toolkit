import shlex
from pathlib import Path
HERE=Path(__file__).resolve().parent
def reading_command(script, args, data, answers=None):
    # Existing reading helpers are read-only. Reuse their exact shell body,
    # redirecting only their hardcoded RU1 log root in memory. $0 stays the
    # original script path, so its sibling helper and workspace resolution hold.
    if script in (HERE/'n1w1_run_read.sh', HERE/'n1w1_limit_probe.sh'):
        body=script.read_text()
        token='D="$W/artifacts/ru1"' if script.name=='n1w1_run_read.sh' else 'A="$W/artifacts/ru1/answers"'
        if body.count(token)!=1: raise ValueError('reading helper log assignment changed')
        target=data if script.name=='n1w1_run_read.sh' else (answers or data/'answers')
        body=body.replace(token, token[:2]+shlex.quote(str(target)))
        return ['bash','-c',body,str(script),*args]
    return [str(script),*args]

