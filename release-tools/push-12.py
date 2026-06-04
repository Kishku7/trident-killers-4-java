import sys
sys.path.insert(0, r'<WORKSPACE>\Plugins\plugin_dave_01\scripts')
from git_push import git_push
repo = r'<WORKSPACE>\Minecraft\mods\trident-killers-4-java'
branches = ['mc/1.20.4', 'mc/1.20.6', 'mc/1.21.1', 'mc/1.21.5', 'mc/1.21.8', 'mc/1.21.11', 'main']
ok = True
for b in branches:
    r = git_push(repo, branch=b)
    print(b, 'PUSHED' if r else 'PUSH-FAILED', flush=True)
    ok = ok and bool(r)
sys.exit(0 if ok else 1)
