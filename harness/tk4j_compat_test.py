"""TK4J single-jar compat test: real Fabric server + RCON kill harness.
Usage: python tk4j_compat_test.py <mc_version>
"""
import json, os, shutil, socket, struct, subprocess, sys, time, urllib.request

VER = sys.argv[1]
JAR_ARG = sys.argv[2] if len(sys.argv) > 2 else None
ROOT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(ROOT, VER)
JAR = JAR_ARG or r'<WORKSPACE>\Minecraft\mods\trident-killers-4-java\build\libs\trident-killers-4-java-1.1+1.20.x.jar'
LOADER = '0.18.6'
RCON_PORT, GAME_PORT, RCON_PW = 25575, 25599, 'tk4jtest'

def log(*a): print(*a, flush=True)

os.makedirs(os.path.join(DIR, 'mods'), exist_ok=True)

launcher = os.path.join(DIR, 'fabric-server.jar')
if not os.path.exists(launcher):
    with urllib.request.urlopen('https://meta.fabricmc.net/v2/versions/installer', timeout=30) as r:
        inst = json.load(r)[0]['version']
    url = f'https://meta.fabricmc.net/v2/versions/loader/{VER}/{LOADER}/{inst}/server/jar'
    log('downloading launcher:', url)
    urllib.request.urlretrieve(url, launcher)

with open(os.path.join(DIR, 'eula.txt'), 'w') as f:
    f.write('eula=true\n')
with open(os.path.join(DIR, 'server.properties'), 'w') as f:
    f.write(f'enable-rcon=true\nrcon.port={RCON_PORT}\nrcon.password={RCON_PW}\n'
            f'server-port={GAME_PORT}\nonline-mode=false\nlevel-type=minecraft\\:flat\n'
            f'spawn-protection=0\nbroadcast-rcon-to-ops=false\npause-when-empty-seconds=-1\n')
# fresh world + fresh jar each run
world = os.path.join(DIR, 'world')
if os.path.isdir(world): shutil.rmtree(world)
for f in os.listdir(os.path.join(DIR, 'mods')):
    os.remove(os.path.join(DIR, 'mods', f))
shutil.copy(JAR, os.path.join(DIR, 'mods'))

slog = open(os.path.join(DIR, 'server-run.log'), 'w')
proc = subprocess.Popen(['java', '-Xmx2G', '-jar', launcher, 'nogui'], cwd=DIR,
                        stdout=slog, stderr=subprocess.STDOUT)
log(f'server starting pid={proc.pid} ({VER})')

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
for i in range(150):
    time.sleep(2)
    if proc.poll() is not None:
        log('SERVER EXITED EARLY rc=', proc.returncode); sys.exit(1)
    try:
        r = Rcon('127.0.0.1', RCON_PORT, RCON_PW); break
    except OSError:
        pass
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
    _idout = g('data get entity @e[type=minecraft:trident,limit=1] tk4j_identified')
    results['identified'] = _idout.endswith('1b') or _idout.endswith('"1"')
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
    try: proc.wait(timeout=25)
    except Exception: proc.kill()
    slog.close()

ok = all(results.values())
log(f'=== {VER} RESULTS ===')
for k, v in results.items(): log(f'  {k}: {"PASS" if v else "FAIL"}')
log(f'=== {VER}: {"ALL PASS" if ok else "FAILURES PRESENT"} ===')
sys.exit(0 if ok else 2)
