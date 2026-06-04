"""TK4J Quilt compat test: real Quilt server + RCON kill harness.
Usage: python tk4j_quilt_test.py <mc_version> <jar_path>

Quilt has no single server-jar meta endpoint like Fabric; we use the quilt-installer CLI:
  java -jar quilt-installer.jar install server <mc> --download-server --install-dir=DIR
which produces quilt-server-launch.jar in DIR. TK4J has no Fabric API dependency, so no
QSL/QFAPI is required — Quilt loader runs Fabric mods natively.
"""
import json, os, re, shutil, socket, struct, subprocess, sys, time, urllib.request

VER, JAR = sys.argv[1], sys.argv[2]
ROOT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(ROOT, f'quilt-{VER}')
RCON_PORT, GAME_PORT, RCON_PW = 25575, 25599, 'tk4jtest'
UA = {'User-Agent': 'Kishku7/trident-killers-4-java/1.2'}

def log(*a): print(*a, flush=True)
os.makedirs(os.path.join(DIR, 'mods'), exist_ok=True)

launch = os.path.join(DIR, 'quilt-server-launch.jar')
if not os.path.exists(launch):
    # latest installer version from maven metadata
    murl = 'https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-installer/maven-metadata.xml'
    with urllib.request.urlopen(urllib.request.Request(murl, headers=UA), timeout=30) as r:
        meta = r.read().decode()
    iver = re.search(r'<release>([^<]+)</release>', meta).group(1)
    inst = os.path.join(DIR, 'quilt-installer.jar')
    if not os.path.exists(inst):
        iurl = (f'https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-installer/'
                f'{iver}/quilt-installer-{iver}.jar')
        log('downloading quilt installer:', iurl)
        req = urllib.request.Request(iurl, headers=UA)
        with urllib.request.urlopen(req, timeout=120) as resp, open(inst, 'wb') as out:
            shutil.copyfileobj(resp, out)
    log('running quilt installer (install server', VER, ') ...')
    r = subprocess.run(['java', '-jar', inst, 'install', 'server', VER,
                        '--download-server', f'--install-dir={DIR}'],
                       capture_output=True, text=True, timeout=600)
    if not os.path.exists(launch):
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
jvm = ['java', '-Xmx2G']
if int(VER.split('.')[0]) >= 26:
    # MC 26.x ships unobfuscated; Quilt loader needs the official target namespace
    jvm.append('-Dloader.experimental.minecraft.targetNamespace=official')
proc = subprocess.Popen(jvm + ['-jar', launch, 'nogui'], cwd=DIR,
                        stdout=slog, stderr=subprocess.STDOUT)
log(f'quilt server starting pid={proc.pid} ({VER})')

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
log(f'=== QUILT {VER} RESULTS ===')
for k, v in results.items(): log(f'  {k}: {"PASS" if v else "FAIL"}')
log(f'=== QUILT {VER}: {"ALL PASS" if ok else "FAILURES PRESENT"} ===')
sys.exit(0 if ok else 2)
