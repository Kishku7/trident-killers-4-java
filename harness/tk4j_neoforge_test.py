"""TK4J NeoForge compat test: real NeoForge server + RCON kill harness.
Usage: python tk4j_neoforge_test.py <mc_version> <neoforge_version> <jar_path>

NeoForge maven coordinates differ by era:
  - 1.20.1 (legacy fork): net/neoforged/forge, version "1.20.1-47.1.x",
    installer forge-1.20.1-47.1.x-installer.jar
  - 1.20.2+ (modern):     net/neoforged/neoforge, version "20.2.x"/"21.1.x"...,
    installer neoforge-<ver>-installer.jar
Legacy is detected by the neoforge version starting with "1.20.1-" or "47.".
"""
import json, os, shutil, socket, struct, subprocess, sys, time, urllib.request

VER, NEO, JAR = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(ROOT, f'neoforge-{VER}')
JAVA17 = r'C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot\bin\java.exe'
JAVA21 = r'C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot\bin\java.exe'

JAVA25 = r'C:\Program Files\Eclipse Adoptium\jdk-25.0.1.8-hotspot\bin\java.exe'

def pick_java(mc):
    parts = mc.split('.')
    major = int(parts[0]); minor = int(parts[1]); patch = int(parts[2]) if len(parts) > 2 else 0
    if major >= 26:
        return JAVA25
    if minor == 20 and patch <= 4:
        return JAVA17
    return JAVA21

JAVA = pick_java(VER)
RCON_PORT, GAME_PORT, RCON_PW = 25575, 25599, 'tk4jtest'

LEGACY = NEO.startswith('1.20.1-') or NEO.startswith('47.')
if LEGACY:
    full = NEO if NEO.startswith('1.20.1-') else f'{VER}-{NEO}'
    URL = f'https://maven.neoforged.net/releases/net/neoforged/forge/{full}/forge-{full}-installer.jar'
    ARGS_REL = os.path.join('libraries', 'net', 'neoforged', 'forge', full, 'win_args.txt')
else:
    URL = f'https://maven.neoforged.net/releases/net/neoforged/neoforge/{NEO}/neoforge-{NEO}-installer.jar'
    ARGS_REL = os.path.join('libraries', 'net', 'neoforged', 'neoforge', NEO, 'win_args.txt')

def log(*a): print(*a, flush=True)
os.makedirs(os.path.join(DIR, 'mods'), exist_ok=True)

argsfile = os.path.join(DIR, ARGS_REL)
if not os.path.exists(argsfile):
    inst = os.path.join(DIR, 'neoforge-installer.jar')
    if not os.path.exists(inst):
        log('downloading installer:', URL)
        req = urllib.request.Request(URL, headers={'User-Agent': 'Kishku7/trident-killers-4-java/1.2'})
        with urllib.request.urlopen(req, timeout=120) as resp, open(inst, 'wb') as out:
            shutil.copyfileobj(resp, out)
    log('running installer --installServer ...')
    r = subprocess.run([JAVA, '-jar', inst, '--installServer'], cwd=DIR, capture_output=True, text=True, timeout=600)
    if not os.path.exists(argsfile):
        log('INSTALL FAILED'); log(r.stdout[-800:]); log(r.stderr[-400:]); sys.exit(1)
    log('installed')

with open(os.path.join(DIR, 'eula.txt'), 'w') as f: f.write('eula=true\n')
with open(os.path.join(DIR, 'server.properties'), 'w') as f:
    f.write(f'enable-rcon=true\nrcon.port={RCON_PORT}\nrcon.password={RCON_PW}\n'
            f'server-port={GAME_PORT}\nonline-mode=false\nlevel-type=minecraft\\:flat\n'
            f'spawn-protection=0\nbroadcast-rcon-to-ops=false\n')
world = os.path.join(DIR, 'world')
if os.path.isdir(world): shutil.rmtree(world)
for f in os.listdir(os.path.join(DIR, 'mods')): os.remove(os.path.join(DIR, 'mods', f))
shutil.copy(JAR, os.path.join(DIR, 'mods'))

slog = open(os.path.join(DIR, 'server-run.log'), 'w')
proc = subprocess.Popen([JAVA, '-Xmx2G', f'@{argsfile}', 'nogui'], cwd=DIR, stdout=slog, stderr=subprocess.STDOUT)
log(f'neoforge server starting pid={proc.pid} ({VER} / {NEO})')

class Rcon:
    def __init__(s, host, port, pw):
        s.s = socket.create_connection((host, port), timeout=10); s.rid = 0; s._send(3, pw)
    def _send(s, t, p):
        s.rid += 1; d = struct.pack('<ii', s.rid, t) + p.encode() + b'\x00\x00'
        s.s.sendall(struct.pack('<i', len(d)) + d)
        ln = struct.unpack('<i', s._recv(4))[0]; b = s._recv(ln); return b[8:-2].decode(errors='replace')
    def _recv(s, n):
        buf = b''
        while len(buf) < n:
            c = s.s.recv(n - len(buf))
            if not c: raise IOError('closed')
            buf += c
        return buf
    def cmd(s, c): return s._send(2, c)

r = None
for i in range(180):
    time.sleep(2)
    if proc.poll() is not None:
        log('SERVER EXITED EARLY rc=', proc.returncode); sys.exit(1)
    try:
        r = Rcon('127.0.0.1', RCON_PORT, RCON_PW); break
    except OSError: pass
if r is None:
    log('RCON NEVER CAME UP'); proc.kill(); sys.exit(1)
log('rcon connected')

g = lambda c: r.cmd(c).strip()
results = {}
try:
    g('forceload add -32 -32 32 32')
    g('kill @e[type=!minecraft:player]'); time.sleep(0.8)
    g('fill -3 199 -3 4 220 4 minecraft:air')
    g('fill -3 199 -3 4 199 4 minecraft:stone')
    g('summon minecraft:trident 0.5 203 0.5'); time.sleep(2.5)
    results['stuck'] = '200.05' in g('data get entity @e[type=minecraft:trident,limit=1] Pos')
    g('setblock 1 200 0 minecraft:piston[facing=west]')
    g('summon minecraft:pig 0.5 200.5 0.5 {NoAI:1b}'); time.sleep(0.6)
    g('setblock 2 200 0 minecraft:redstone_block'); time.sleep(1.5)
    _id = g('data get entity @e[type=minecraft:trident,limit=1] tk4j_identified')
    results['identified'] = _id.endswith('1b') or _id.endswith('"1"')
    results['hit_8dmg'] = '2.0f' in g('data get entity @e[type=minecraft:pig,limit=1] Health')
    g('setblock 2 200 0 minecraft:air'); time.sleep(1.2)
    g('tp @e[type=minecraft:pig,limit=1] 0.5 200.5 0.5'); time.sleep(0.4)
    g('setblock 2 200 0 minecraft:redstone_block'); time.sleep(1.5)
    results['killed'] = 'failed' in g('execute if entity @e[type=minecraft:pig]').lower()
    results['loot_dropped'] = 'passed' in g('execute if entity @e[type=minecraft:item]').lower()
    results['xp_suppressed'] = 'failed' in g('execute if entity @e[type=minecraft:experience_orb]').lower()
    results['anchored'] = '0.5d, 200.05' in g('data get entity @e[type=minecraft:trident,limit=1] Pos')
    l1 = g('data get entity @e[type=minecraft:trident,limit=1] life')
    time.sleep(3)
    results['despawn_frozen'] = g('data get entity @e[type=minecraft:trident,limit=1] life') == l1
finally:
    try: g('stop')
    except Exception: pass
    try: proc.wait(timeout=30)
    except Exception: proc.kill()
    slog.close()

ok = all(results.values())
log(f'=== NEOFORGE {VER} ({NEO}) RESULTS ===')
for k, v in results.items(): log(f'  {k}: {"PASS" if v else "FAIL"}')
log(f'=== NEOFORGE {VER}: {"ALL PASS" if ok else "FAILURES PRESENT"} ===')
sys.exit(0 if ok else 2)
