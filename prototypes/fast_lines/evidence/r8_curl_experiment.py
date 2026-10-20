"""Load the withdrawn i1 patch in an isolated namespace for small fixtures.

This does not install a Stack route. All other modules come from the checkout;
only the three source-bound edited consumers are replayed from the archived diff.
"""
import importlib
import re
import sys
import types
from pathlib import Path


def consumers(directory):
    root=Path(__file__).resolve().parents[1]
    lines=(Path(__file__).with_name('curl03_i1_withdrawn.patch')).read_text().splitlines(True)
    n=0
    while n<len(lines):
        if not lines[n].startswith('+++ b/'):
            n+=1;continue
        relative=lines[n][6:].strip();path=Path(relative).relative_to('prototypes/fast_lines')
        old=(root/path).read_text().splitlines(True);out=[];cursor=0;n+=1
        while n<len(lines) and not lines[n].startswith('diff --git'):
            match=re.match(r'@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@',lines[n])
            if not match:n+=1;continue
            at=int(match[1])-1;out.extend(old[cursor:at]);cursor=at;n+=1
            while n<len(lines) and lines[n][:1] in (' ','+','-'):
                operation=lines[n][0];value=lines[n][1:]
                if operation in (' ','-'):
                    assert old[cursor]==value,(path,cursor,'patch base changed')
                    cursor+=1
                if operation in (' ','+'):out.append(value)
                n+=1
        out.extend(old[cursor:]);target=Path(directory)/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(''.join(out))
    name='curl03_fixture_'+str(id(directory));package=types.ModuleType(name);package.__path__=[str(root)];sys.modules[name]=package
    shared=types.ModuleType(name+'.shared');shared.__path__=[str(Path(directory)/'shared'),str(root/'shared')];sys.modules[name+'.shared']=shared
    return importlib.import_module(name+'.shared.geometry_envelopes'),importlib.import_module(name+'.shared.geometry_page_field')
