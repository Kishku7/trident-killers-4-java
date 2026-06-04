"""Attach forge/neoforge loader jars to the v1.2 GitHub releases (TK4J)."""
import json, os, re, sys, time, urllib.request, urllib.error

REPO = 'Kishku7/trident-killers-4-java'
STAGE = r'<WORKSPACE>\Minecraft\mods\trident-killers-4-java'
CRED = r'<PATH_TO_YOUR_GITHUB_PAT_FILE>'  # plain text file containing a GitHub PAT

sys.path.insert(0, r'<WORKSPACE>\Plugins\plugin_dave_01\scripts')
from git_push import _read_pat
TOK = _read_pat()
HDR = {'Authorization': f'Bearer {TOK}', 'Accept': 'application/vnd.github+json',
       'User-Agent': 'Kishku7/trident-killers-4-java/1.2'}

# family -> loader jar filenames in the staging folder
PLAN = {
    'v1.2+1.20.4':  ['trident-killers-4-java-1.2+1.20.4-forge.jar'],
    'v1.2+1.20.6':  ['trident-killers-4-java-1.2+1.20.6-forge.jar',
                     'trident-killers-4-java-1.2+1.20.6-neoforge.jar'],
    'v1.2+1.21.1':  ['trident-killers-4-java-1.2+1.21.1-forge.jar',
                     'trident-killers-4-java-1.2+1.21.1-neoforge.jar'],
    'v1.2+1.21.5':  ['trident-killers-4-java-1.2+1.21.5-forge.jar',
                     'trident-killers-4-java-1.2+1.21.5-neoforge.jar'],
    'v1.2+1.21.8':  ['trident-killers-4-java-1.2+1.21.8-forge.jar',
                     'trident-killers-4-java-1.2+1.21.8-neoforge.jar'],
    'v1.2+1.21.11': ['trident-killers-4-java-1.2+1.21.11-neoforge.jar'],
    'v1.2+26.1.2':  ['trident-killers-4-java-1.2+26.1.2-neoforge.jar'],
}

def api(url, data=None, hdr=None):
    req = urllib.request.Request(url, data=data, headers=hdr or HDR)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

# wait for all 7 v1.2 releases (CI), up to 12 min
releases = {}
deadline = time.time() + 720
while time.time() < deadline:
    rel = api(f'https://api.github.com/repos/{REPO}/releases?per_page=30')
    releases = {r['tag_name']: r for r in rel if r['tag_name'] in PLAN}
    missing = [t for t in PLAN if t not in releases]
    if not missing:
        break
    print('waiting for CI releases:', ', '.join(missing), flush=True)
    time.sleep(30)
else:
    print('TIMEOUT waiting for releases; proceeding with what exists', flush=True)

fail = 0
for tag, jars in PLAN.items():
    r = releases.get(tag)
    if not r:
        print(f'{tag}: RELEASE MISSING - skipped'); fail += 1; continue
    have = {a['name'] for a in r['assets']}
    for jar in jars:
        if jar in have:
            print(f'{tag}: {jar} already attached'); continue
        path = os.path.join(STAGE, jar)
        if not os.path.exists(path):
            print(f'{tag}: {jar} NOT STAGED - skipped'); fail += 1; continue
        data = open(path, 'rb').read()
        url = (r['upload_url'].split('{')[0] + f'?name={urllib.parse.quote(jar)}')
        hdr = dict(HDR); hdr['Content-Type'] = 'application/java-archive'
        try:
            res = api(url, data=data, hdr=hdr)
            print(f'{tag}: UPLOADED {jar} ({res.get("state","?")})', flush=True)
        except urllib.error.HTTPError as e:
            print(f'{tag}: UPLOAD FAILED {jar} HTTP {e.code}: {e.read()[:200]}'); fail += 1
print('=== DONE ===', 'failures:', fail)
sys.exit(1 if fail else 0)
