# Practice 호버용 아이소 장면 SVG 3장 (DESK · MEETING · SITE)
# 면은 흰/회색으로 채우고 검은 선, 벽 단면은 검정. 나는 흰 채움, 다른 사람은 단선.
import math, os, sys

C30, S30 = math.cos(math.pi / 6), 0.5
INK = '#2a2926'


class Scene:
    def __init__(s, w=1600, h=1000, ox=800, oy=330, k=0.82):
        s.w, s.h, s.ox, s.oy, s.k = w, h, ox, oy, k
        s.out = []
        s.base = s.out
        s.groups = []

    # 깊이 그룹: 뒤(작은 x+y)부터 그림
    def g(s, depth):
        s.out = []
        s.groups.append((depth, len(s.groups), s.out))

    def P(s, x, y, z):
        return (s.ox + (x - y) * C30 * s.k, s.oy + ((x + y) * S30 - z) * s.k)

    def poly(s, pts3, fill='#fff', sw=1.0, stroke=INK, extra=''):
        p = ' '.join('%.1f,%.1f' % s.P(*q) for q in pts3)
        s.out.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{extra}/>')

    def line(s, a, b, sw=0.8, stroke=INK, dash=''):
        (x1, y1), (x2, y2) = s.P(*a), s.P(*b)
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')

    def pl(s, pts, sw=0.8, stroke=INK, fill='none'):
        p = ' '.join('%.1f,%.1f' % s.P(*q) for q in pts)
        s.out.append(f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')

    def raw(s, t):
        s.out.append(t)

    # 상자: 위, +y(왼쪽 앞), +x(오른쪽 앞) 면만 그림
    def box(s, x, y, z, dx, dy, dz, top='#fff', fy='#ebe8e2', fx='#d9d5cd', sw=1.0):
        X, Y, Z = x + dx, y + dy, z + dz
        s.poly([(x, Y, z), (X, Y, z), (X, Y, Z), (x, Y, Z)], fy, sw)
        s.poly([(X, y, z), (X, Y, z), (X, Y, Z), (X, y, Z)], fx, sw)
        s.poly([(x, y, Z), (X, y, Z), (X, Y, Z), (x, Y, Z)], top, sw)

    def cyl(s, cx, cy, z, r, h, top='#fff', side='#e3e0d9', sw=1.0, n=20):
        # 등각 원통: 바닥과 윗면 타원
        def ring(zz):
            return [(cx + r * math.cos(t), cy + r * math.sin(t), zz) for t in [2 * math.pi * i / n for i in range(n)]]
        bot, tp = ring(z), ring(z + h)
        pts = [s.P(*q) for q in bot]; ptt = [s.P(*q) for q in tp]
        # 옆면 외곽: 화면 x 최소·최대 점
        il = min(range(n), key=lambda i: pts[i][0]); ir = max(range(n), key=lambda i: pts[i][0])
        def arc(a, b, ring2, step):
            i, o = a, []
            while True:
                o.append(ring2[i])
                if i == b: break
                i = (i + step) % n
            return o
        # 앞쪽(화면 y 큰 쪽) 바닥 호
        f1 = arc(il, ir, pts, 1); f2 = arc(il, ir, pts, -1)
        front = f1 if sum(p[1] for p in f1) / len(f1) > sum(p[1] for p in f2) / len(f2) else f2
        side_pts = [ptt[il]] + front + [ptt[ir]]
        s.raw('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (' '.join('%.1f,%.1f' % p for p in side_pts), side, INK, sw))
        s.raw('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (' '.join('%.1f,%.1f' % p for p in ptt), top, INK, sw))

    def svg(s, bg='#e6e3dc'):
        body = ''.join(s.base) + ''.join(''.join(o) for _, _, o in sorted(s.groups, key=lambda t: (t[0], t[1])))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.w} {s.h}" width="{s.w}" height="{s.h}">'
                f'<rect width="{s.w}" height="{s.h}" fill="{bg}"/>' + body + '</svg>')


# ---------- 가구 ----------
def desk(S, x, y, w, d, h=74, legs=True):
    if legs:
        for lx, ly in [(x + 3, y + 3), (x + w - 7, y + 3), (x + 3, y + d - 7), (x + w - 7, y + d - 7)]:
            S.box(lx, ly, 0, 4, 4, h - 3, sw=0.8)
    S.box(x, y, h - 3, w, d, 3)


def monitor(S, x, y, z, face='y', w=56):
    # face='y': 화면이 +y를 봄
    if face == 'y':
        S.box(x + w / 2 - 9, y + 2, z, 18, 12, 1.2, sw=0.7)
        S.box(x + w / 2 - 2, y + 4, z, 4, 3, 14, sw=0.7)
        S.box(x, y, z + 12, w, 3, 34, top='#fff', fy='#f7f6f3', fx='#cfcac1')
        S.poly([(x + 2, y + 3, z + 14), (x + w - 2, y + 3, z + 14), (x + w - 2, y + 3, z + 44), (x + 2, y + 3, z + 44)], '#fbfaf8', 0.6)
    elif face == '-y':
        S.box(x + w / 2 - 9, y - 12, z, 18, 12, 1.2, sw=0.7)
        S.box(x, y - 3, z + 12, w, 3, 34, top='#fff', fy='#f2f0eb', fx='#cfcac1')
        S.box(x + w / 2 - 2, y, z + 4, 4, 3, 24, sw=0.7)
        S.box(x + w / 2 - 8, y, z + 20, 16, 4, 14, sw=0.6)
    else:
        S.box(x + 2, y + w / 2 - 9, z, 12, 18, 1.2, sw=0.7)
        S.box(x + 4, y + w / 2 - 2, z, 3, 4, 14, sw=0.7)
        S.box(x, y, z + 12, 3, w, 34, top='#fff', fy='#cfcac1', fx='#f7f6f3')


def keyboard(S, x, y, z, w=42, d=14):
    S.box(x, y, z, w, d, 1.5, sw=0.7)
    for i in range(1, 4):
        S.line((x + 1, y + d * i / 4, z + 1.5), (x + w - 1, y + d * i / 4, z + 1.5), 0.35)
    for i in range(1, 14):
        S.line((x + w * i / 14, y + 1, z + 1.5), (x + w * i / 14, y + d - 1, z + 1.5), 0.35)


def mouse(S, x, y, z):
    S.cyl(x, y, z, 3.2, 1.5, sw=0.6, n=12)


def chair(S, x, y, face='-y'):
    # 오피스 의자: 바퀴 5개, 기둥, 좌판, 등판
    cx, cy = x, y
    for i in range(5):
        t = 2 * math.pi * i / 5 + 0.3
        ex, ey = cx + 30 * math.cos(t), cy + 30 * math.sin(t)
        S.line((cx, cy, 6), (ex, ey, 6), 1.6)
        S.cyl(ex, ey, 0, 2.6, 3.5, sw=0.6, n=10)
    S.cyl(cx, cy, 6, 2.5, 34, sw=0.7, n=10)
    S.box(cx - 23, cy - 23, 40, 46, 46, 7, sw=0.9)
    if face == '-y':
        S.box(cx - 22, cy + 22, 47, 44, 5, 40, sw=0.9)
    elif face == '+y':
        S.box(cx - 22, cy - 27, 47, 44, 5, 40, sw=0.9)
    elif face == '-x':
        S.box(cx + 22, cy - 22, 47, 5, 44, 40, sw=0.9)
    else:
        S.box(cx - 27, cy - 22, 47, 5, 44, 40, sw=0.9)


def stool(S, x, y, h=62):
    for dx, dy in [(-16, -16), (16, -16), (-16, 16), (16, 16)]:
        S.line((x + dx, y + dy, 0), (x + dx * .8, y + dy * .8, h), 1.4)
    S.pl([(x - 14, y - 14, 25), (x + 14, y - 14, 25), (x + 14, y + 14, 25), (x - 14, y + 14, 25), (x - 14, y - 14, 25)], 1)
    S.cyl(x, y, h, 19, 4, sw=0.9, n=18)


def plant(S, x, y, z=0, r=16, h=34, big=1.0):
    S.cyl(x, y, z, r, h, top='#d8d3c9', side='#f3f1ec', sw=0.9)
    import random
    rnd = random.Random(int(x * 7 + y * 13))
    base = (x, y, z + h)
    for i in range(int(16 * big)):
        a = rnd.random() * 2 * math.pi; L = (40 + rnd.random() * 50) * big; el = 0.5 + rnd.random() * 0.9
        tip = (x + L * math.cos(a) * 0.5, y + L * math.sin(a) * 0.5, z + h + L * el)
        mid = ((base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2, (base[2] + tip[2]) / 2 + 6)
        b2, m2, t2 = S.P(*base), S.P(*mid), S.P(*tip)
        # 잎: 끝점 쪽에 넓은 잎 모양
        lx, ly = t2; px, py = m2
        dx, dy = lx - px, ly - py; n = math.hypot(dx, dy) or 1; nx, ny = -dy / n * 7 * big, dx / n * 7 * big
        S.raw(f'<path d="M{b2[0]:.1f},{b2[1]:.1f} Q{px:.1f},{py:.1f} {lx:.1f},{ly:.1f}" fill="none" stroke="{INK}" stroke-width="0.7"/>')
        S.raw(f'<path d="M{px:.1f},{py:.1f} Q{px+dx*.5+nx:.1f},{py+dy*.5+ny:.1f} {lx:.1f},{ly:.1f} Q{px+dx*.5-nx:.1f},{py+dy*.5-ny:.1f} {px:.1f},{py:.1f}Z" fill="#fff" stroke="{INK}" stroke-width="0.7"/>')


def pendant(S, x, y, z, w=120, d=8, ceil=300):
    S.line((x + 10, y + d / 2, z + 4), (x + 10, y + d / 2, ceil), 0.5)
    S.line((x + w - 10, y + d / 2, z + 4), (x + w - 10, y + d / 2, ceil), 0.5)
    S.box(x, y, z, w, d, 4, sw=0.8)


def shelf_grid(S, x, y, w, d, h, nx=3, nz=6, books=True, ink='#1d1c1a'):
    # 검은 철제 격자 선반
    import random
    rnd = random.Random(int(x + y))
    for i in range(nz + 1):
        z = h * i / nz
        S.pl([(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z), (x, y, z)], 1.3, ink)
    for i in range(nx + 1):
        xx = x + w * i / nx
        S.line((xx, y, 0), (xx, y, h), 1.3, ink); S.line((xx, y + d, 0), (xx, y + d, h), 1.3, ink)
    if books:
        for i in range(nz):
            for j in range(nx):
                if rnd.random() < 0.55:
                    bx = x + w * j / nx + 4; z0 = h * i / nz
                    for b in range(rnd.randint(2, 5)):
                        bw = 3 + rnd.random() * 3; bh = h / nz * (0.55 + rnd.random() * 0.35)
                        S.box(bx, y + 4, z0, bw, d - 8, bh, sw=0.6); bx += bw + 0.6


def glass(S, x0, y0, x1, y1, h, mull=4):
    S.poly([(x0, y0, 0), (x1, y1, 0), (x1, y1, h), (x0, y0, h)], 'rgba(255,255,255,0.35)', 0.8)
    for i in range(1, mull):
        t = i / mull
        S.line((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 0), (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, h), 0.8)
    S.line((x0, y0, h * .45), (x1, y1, h * .45), 0.5)


def roll(S, x, y, z, L=60, r=3.2):
    # 도면 롤: x 방향 원통 (단순 상자+원)
    S.box(x, y, z, L, r * 2, r * 2, sw=0.6)


def model(S, x, y, z):
    S.box(x, y, z, 30, 26, 2, sw=0.7)
    S.box(x + 3, y + 3, z + 2, 10, 9, 16, sw=0.6)
    S.box(x + 15, y + 4, z + 2, 12, 8, 9, sw=0.6)
    S.box(x + 5, y + 14, z + 2, 18, 9, 6, sw=0.6)


def papers(S, x, y, z, n=3):
    for i in range(n):
        S.poly([(x + i * 3, y + i * 2, z + i * .3), (x + 42 + i * 3, y + i * 2, z + i * .3), (x + 42 + i * 3, y + 30 + i * 2, z + i * .3), (x + i * 3, y + 30 + i * 2, z + i * .3)], '#fff', 0.6)
    for j in range(5):
        S.line((x + 10, y + 6 + j * 4, z + n * .3), (x + 38, y + 6 + j * 4, z + n * .3), 0.35)


# ---------- 사람 (2D 인물, 측면/반측면) ----------
# 관절 좌표는 cm, 발 기준 (y 위로 +)
def person(S, at, pose, me=False, flip=False, scale=1.0, helmet=False, prop=None, hip=False):
    fx, fy = S.P(*at)
    k = S.k * scale
    f = -1 if flip else 1
    J = POSES[pose]
    if hip:  # 주어진 점에 엉덩이를 맞춤 (의자 위)
        fx -= J['hip'][0] * f * k; fy += J['hip'][1] * k
    def p(name, dx=0, dy=0):
        x, y = J[name]
        return (fx + (x + dx) * f * k, fy - (y + dy) * k)
    fill = '#fdfcfa' if me else 'none'
    col = INK if me else '#6d6a64'
    sw = 1.15 if me else 0.9
    out = []
    def path(d, fl=None):
        out.append(f'<path d="{d}" fill="{fill if fl is None else fl}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')
    def limb(a, b, w1, w2, bend=0.0):
        (ax, ay), (bx, by) = a, b
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        mx, my = (ax + bx) / 2 + nx * bend * k, (ay + by) / 2 + ny * bend * k
        w1, w2 = w1 * k / 2, w2 * k / 2
        d = (f'M{ax+nx*w1:.1f},{ay+ny*w1:.1f} Q{mx+nx*(w1+w2)/2:.1f},{my+ny*(w1+w2)/2:.1f} {bx+nx*w2:.1f},{by+ny*w2:.1f} '
             f'A{w2:.1f},{w2:.1f} 0 0 1 {bx-nx*w2:.1f},{by-ny*w2:.1f} Q{mx-nx*(w1+w2)/2:.1f},{my-ny*(w1+w2)/2:.1f} {ax-nx*w1:.1f},{ay-ny*w1:.1f} '
             f'A{w1:.1f},{w1:.1f} 0 0 1 {ax+nx*w1:.1f},{ay+ny*w1:.1f}Z')
        path(d)
    # 먼 팔·다리
    limb(p('sh', -2), p('eF'), 11, 9); limb(p('eF'), p('hF'), 9, 7)
    limb(p('hip', -2), p('kF'), 17, 13, 1); limb(p('kF'), p('aF'), 12, 9)
    sx, sy = p('aF'); tx, ty = p('aF', 22, 0)
    path(f'M{sx-4*k*f:.1f},{sy-5*k:.1f} L{tx:.1f},{ty-3*k:.1f} Q{tx+3*k*f:.1f},{ty+2*k:.1f} {tx-2*k*f:.1f},{ty+3*k:.1f} L{sx-5*k*f:.1f},{sy+3*k:.1f}Z')
    # 몸통 (셔츠)
    nx_, ny_ = p('nk'); hx, hy = p('hip')
    sh1 = p('sh', 9, 0); sh2 = p('sh', -11, 0)
    w1 = p('hip', 12, 2); w2 = p('hip', -13, 4)
    path(f'M{sh2[0]:.1f},{sh2[1]:.1f} Q{nx_:.1f},{ny_-4*k:.1f} {sh1[0]:.1f},{sh1[1]:.1f} Q{(sh1[0]+w1[0])/2+4*k*f:.1f},{(sh1[1]+w1[1])/2:.1f} {w1[0]:.1f},{w1[1]:.1f} L{w2[0]:.1f},{w2[1]:.1f} Q{(sh2[0]+w2[0])/2-5*k*f:.1f},{(sh2[1]+w2[1])/2:.1f} {sh2[0]:.1f},{sh2[1]:.1f}Z')
    # 셔츠 주름 몇 줄
    out.append(f'<path d="M{(sh1[0]+w1[0])/2:.1f},{(sh1[1]+w1[1])/2:.1f} q{-6*k*f:.1f},{4*k:.1f} {-10*k*f:.1f},{12*k:.1f}" fill="none" stroke="{col}" stroke-width="{sw*.7}"/>')
    # 가까운 다리 (바지)
    limb(p('hip', 2), p('kN'), 19, 14, 1.5); limb(p('kN'), p('aN'), 13, 10)
    sx, sy = p('aN'); tx, ty = p('aN', 24, 0)
    path(f'M{sx-5*k*f:.1f},{sy-5*k:.1f} L{tx:.1f},{ty-3*k:.1f} Q{tx+3*k*f:.1f},{ty+2*k:.1f} {tx-2*k*f:.1f},{ty+3*k:.1f} L{sx-6*k*f:.1f},{sy+3*k:.1f}Z')
    # 목, 머리, 머리카락
    hx, hy = p('hd'); r = 10.5 * k
    limb(p('nk'), p('hd', -2, -8), 8, 8)
    path(f'M{hx-r*f*0.95:.1f},{hy:.1f} A{r:.1f},{r*1.12:.1f} 0 1 {1 if f>0 else 0} {hx+r*f*0.95:.1f},{hy+1*k:.1f} Q{hx+r*f*1.05:.1f},{hy+r*0.7:.1f} {hx+r*f*0.5:.1f},{hy+r*1.05:.1f} L{hx-r*f*0.2:.1f},{hy+r*1.15:.1f} Q{hx-r*f*1.0:.1f},{hy+r*0.8:.1f} {hx-r*f*0.95:.1f},{hy:.1f}Z')
    if helmet:
        path(f'M{hx-r*f*1.15:.1f},{hy-2*k:.1f} A{r*1.15:.1f},{r*1.0:.1f} 0 0 {1 if f>0 else 0} {hx+r*f*1.15:.1f},{hy-2*k:.1f} L{hx+r*f*1.45:.1f},{hy-0.5*k:.1f} L{hx-r*f*1.2:.1f},{hy-0.5*k:.1f}Z')
    else:
        path(f'M{hx-r*f*1.0:.1f},{hy+2*k:.1f} Q{hx-r*f*1.1:.1f},{hy-r*1.2:.1f} {hx+r*f*0.2:.1f},{hy-r*1.15:.1f} Q{hx+r*f*1.05:.1f},{hy-r*1.0:.1f} {hx+r*f*0.9:.1f},{hy-r*0.25:.1f} Q{hx+r*f*0.2:.1f},{hy-r*0.6:.1f} {hx-r*f*0.35:.1f},{hy-r*0.1:.1f} Q{hx-r*f*0.6:.1f},{hy+r*0.5:.1f} {hx-r*f*1.0:.1f},{hy+2*k:.1f}Z')
    # 귀, 눈
    out.append(f'<path d="M{hx-r*f*0.1:.1f},{hy+r*0.05:.1f} q{-3*k*f:.1f},{1*k:.1f} {-1*k*f:.1f},{5*k:.1f}" fill="none" stroke="{col}" stroke-width="{sw*.7}"/>')
    out.append(f'<circle cx="{hx+r*f*0.62:.1f}" cy="{hy+r*0.05:.1f}" r="{0.9*k:.2f}" fill="{col}"/>')
    # 가까운 팔
    limb(p('sh', 2), p('eN'), 12, 10, -1); limb(p('eN'), p('hN'), 10, 7.5)
    out.append(f'<circle cx="{p("hN")[0]:.1f}" cy="{p("hN")[1]:.1f}" r="{4.2*k:.1f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    if prop == 'sheet':
        a = p('hN', -2, 2); b = p('hN', 4, 30); c = p('hN', 26, 22); d = p('hN', 22, -4)
        path(f'M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} L{c[0]:.1f},{c[1]:.1f} L{d[0]:.1f},{d[1]:.1f}Z', '#fdfcfa' if me else 'none')
    if prop == 'roll':
        a = p('hF'); b = p('hF', 4, -40)
        limb(a, b, 5, 5)
    S.raw('<g>' + ''.join(out) + '</g>')


POSES = {
    'stand': dict(hip=(0, 92), kN=(3, 50), aN=(1, 7), kF=(-3, 50), fF=(0, 0), aF=(-7, 7), nk=(2, 145), sh=(1, 140), hd=(5, 158), eN=(6, 112), hN=(22, 110), eF=(-2, 112), hF=(18, 114)),
    'think': dict(hip=(0, 92), kN=(3, 50), aN=(2, 7), kF=(-3, 50), aF=(-8, 7), nk=(2, 145), sh=(1, 140), hd=(6, 158), eN=(16, 115), hN=(13, 146), eF=(-4, 113), hF=(12, 112)),
    'point': dict(hip=(0, 92), kN=(7, 50), aN=(12, 7), kF=(-4, 50), aF=(-11, 7), nk=(3, 145), sh=(2, 140), hd=(7, 158), eN=(22, 128), hN=(46, 140), eF=(2, 112), hF=(18, 118)),
    'type': dict(hip=(0, 50), kN=(44, 52), aN=(46, 7), kF=(42, 53), aF=(38, 7), nk=(8, 102), sh=(7, 98), hd=(15, 116), eN=(14, 76), hN=(42, 78), eF=(12, 78), hF=(38, 80)),
    'talk': dict(hip=(0, 64), kN=(42, 64), aN=(46, 8), kF=(40, 66), aF=(30, 34), nk=(10, 116), sh=(9, 112), hd=(18, 130), eN=(22, 92), hN=(50, 100), eF=(18, 94), hF=(44, 96)),
    'read': dict(hip=(0, 92), kN=(2, 50), aN=(3, 7), kF=(-3, 50), aF=(-8, 7), nk=(3, 145), sh=(2, 140), hd=(9, 155), eN=(8, 112), hN=(30, 126), eF=(2, 114), hF=(28, 122)),
}


def room_shell(S, W, D, H=290, floor='#efede8'):
    # 바닥, 벽(단면 검정), 바닥 슬래브 앞 단면
    S.poly([(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0)], floor, 1.0)
    for i in range(1, int(W / 60)):
        S.line((i * 60, 0, 0), (i * 60, D, 0), 0.25, '#b9b4aa')
    for i in range(1, int(D / 60)):
        S.line((0, i * 60, 0), (W, i * 60, 0), 0.25, '#b9b4aa')
    # 뒷벽 두 개 (면만) + 단면 윗면 검정
    S.poly([(0, 0, 0), (W, 0, 0), (W, 0, H), (0, 0, H)], '#f6f5f2', 1.0)
    S.poly([(0, 0, 0), (0, D, 0), (0, D, H), (0, 0, H)], '#e4e1da', 1.0)
    T = 24
    S.poly([(-T, -T, H), (W + T, -T, H), (W + T, 0, H), (0, 0, H), (0, D + T, H), (-T, D + T, H)], '#1b1a18', 1.0)
    S.poly([(W, -T, H), (W + T, -T, H), (W + T, -T, 0), (W + T, 0, 0), (W, 0, 0)], '#1b1a18', 0.8)
    S.poly([(-T, D, H), (-T, D + T, H), (-T, D + T, 0), (0, D + T, 0), (0, D, 0)], '#1b1a18', 0.8)
    # 바닥 슬래브 앞 단면
    S.poly([(0, D, 0), (W + T, D, 0), (W + T, D, -T), (0, D, -T)], '#1b1a18', 0.8)
    S.poly([(W, 0, 0), (W, D, 0), (W, D, -T), (W, -T, -T), (W, -T, 0)], '#1b1a18', 0.8)
    S.poly([(-T, D + T, 0), (W + T, D + T, 0)], '#1b1a18', 0.8) if False else None


def window_wall(S, x0, x1, z0, z1, n):
    S.poly([(x0, 0.5, z0), (x1, 0.5, z0), (x1, 0.5, z1), (x0, 0.5, z1)], '#fbfbf9', 1.0)
    for i in range(1, n):
        x = x0 + (x1 - x0) * i / n
        S.line((x, 0.5, z0), (x, 0.5, z1), 1.0)
    S.line((x0, 0.5, z0 + 30), (x1, 0.5, z0 + 30), 0.6)
    # 창 밖 나무·건물 실루엣 (희미하게)
    for i in range(n):
        x = x0 + (x1 - x0) * (i + .5) / n
        S.line((x - 14, 0.5, z0 + 60), (x - 14, 0.5, z0 + 120 + (i % 3) * 25), 0.3, '#bdb8ae')


def desk_scene():
    S = Scene(ox=760, oy=250, k=1.25)
    W, D = 720, 470
    room_shell(S, W, D)
    window_wall(S, 90, 660, 40, 250, 6)
    S.poly([(0.5, 330, 0), (0.5, 420, 0), (0.5, 420, 215), (0.5, 330, 215)], '#fbfbf9', 1.0)
    S.g(40); shelf_grid(S, 30, 24, 130, 34, 210, nx=3, nz=5)
    S.g(700); S.box(600, 40, 0, 90, 40, 80, sw=0.9); plant(S, 645, 60, 80, 12, 22, 0.7)
    # 책상 2줄: 사람은 각 책상 뒤(-y)에 앉아 화면(+y 쪽)을 봄
    for row, y0 in enumerate([200, 330]):
        cy = y0 - 34
        for i, x in enumerate([200, 320, 440]):
            S.g(x + 28 + cy - 1); chair(S, x + 30, cy, '+y')
            who = {(0, 1): 1, (1, 0): 0, (0, 2): 0, (1, 2): 0}.get((row, i))
            if who is not None:
                S.g(x + 28 + cy); person(S, (x + 30, cy - 6, 50), 'type', me=bool(who), flip=True, hip=True, scale=1.05)
        S.g(340 + y0 + 40)
        desk(S, 180, y0, 360, 70)
        for i, x in enumerate([200, 320, 440]):
            monitor(S, x, y0 + 50, 74, face='-y')
            keyboard(S, x + 6, y0 + 8, 74)
            mouse(S, x + 58, y0 + 14, 74)
        if row == 0:
            model(S, 500, y0 + 30, 74); roll(S, 190, y0 + 34, 74, 40)
        else:
            papers(S, 480, y0 + 30, 74)
        S.g(900 + row); pendant(S, 200, y0 + 30, 200, 320, ceil=290)
    S.g(420); person(S, (120, 300, 0), 'read', prop='sheet', flip=True)
    S.g(1000); plant(S, 660, 420, 0, 18, 36, 1.2)
    S.g(300); plant(S, 50, 380, 0, 16, 32, 0.9)
    return S


def meeting_scene():
    S = Scene(oy=250, k=0.9)
    W, D = 900, 620
    room_shell(S, W, D)
    # 화이트보드 + 핀업
    S.poly([(140, 0.5, 90), (620, 0.5, 90), (620, 0.5, 230), (140, 0.5, 230)], '#fff', 1.2)
    S.pl([(170, 0.5, 120), (240, 0.5, 200), (300, 0.5, 140), (380, 0.5, 210)], 1.1, '#c9452c')
    for i in range(3):
        S.poly([(420 + i * 62, 0.5, 120), (470 + i * 62, 0.5, 120), (470 + i * 62, 0.5, 200), (420 + i * 62, 0.5, 200)], '#f4f2ee', 0.7)
    S.poly([(0.5, 120, 60), (0.5, 420, 60), (0.5, 420, 250), (0.5, 120, 250)], '#fbfbf9', 1.0)
    for i in range(1, 4):
        S.line((0.5, 120 + 75 * i, 60), (0.5, 120 + 75 * i, 250), 0.8)
    shelf_grid(S, 700, 30, 150, 34, 200, nx=3, nz=5)
    plant(S, 790, 60, 200, 10, 16, 0.6)
    # 테이블과 모형, 도면
    desk(S, 280, 250, 340, 150, h=90)
    model(S, 420, 300, 90); model(S, 455, 320, 90)
    papers(S, 300, 270, 90); papers(S, 540, 340, 90, 2)
    roll(S, 330, 360, 90, 70)
    for x, y in [(260, 330), (640, 300)]:
        stool(S, x, y)
    pendant(S, 300, 320, 220, 300)
    plant(S, 830, 560, 0, 22, 44, 1.4)
    # 사람
    person(S, (300, 140, 0), 'think')
    person(S, (560, 160, 0), 'read', flip=True, prop='sheet')
    person(S, (720, 350, 0), 'stand', flip=True)
    person(S, (262, 332, 0), 'talk', me=True, scale=1.05)
    person(S, (640, 302, 0), 'talk', flip=True)
    return S


def site_scene():
    S = Scene(oy=330, k=0.62)
    W, D = 1300, 900
    # 땅
    S.poly([(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0)], '#e9e5dc', 1.0)
    import random
    rnd = random.Random(3)
    for i in range(500):
        x, y = rnd.random() * W, rnd.random() * D
        a = S.P(x, y, 0)
        S.raw(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="0.7" fill="#9c968a"/>')
    # 땅 단면
    T = 40
    S.poly([(0, D, 0), (W, D, 0), (W, D, -T), (0, D, -T)], '#1b1a18', 0.8)
    S.poly([(W, 0, 0), (W, D, 0), (W, D, -T), (W, 0, -T)], '#1b1a18', 0.8)
    # 기초 슬래브
    S.box(200, 120, 0, 840, 520, 18, top='#f3f1ec')
    # 철골: 기둥 H형 단순화 (상자 2개)
    cols = [(220 + i * 270, 140 + j * 240) for j in range(3) for i in range(4)]
    for k2, (x, y) in enumerate(sorted(cols, key=lambda c: c[0] + c[1])):
        hgt = 720 if (x < 800) else 380
        S.box(x - 9, y - 3, 18, 18, 6, hgt, sw=0.8)
        S.box(x - 3, y - 9, 18, 6, 18, hgt, sw=0.8)
    for z in [380, 720]:
        for j in range(3):
            y = 140 + j * 240
            xe = 220 + 3 * 270 if z == 380 else 220 + 2 * 270
            S.box(220, y - 6, z, xe - 220, 12, 22, sw=0.8)
        for i in range(4 if z == 380 else 3):
            x = 220 + i * 270
            S.box(x - 6, 140, z, 12, 480, 22, sw=0.8)
    # 데크 일부 (골판 선)
    S.poly([(220, 140, 402), (760, 140, 402), (760, 380, 402), (220, 380, 402)], '#f7f6f2', 0.9)
    for i in range(1, 30):
        S.line((220 + i * 18, 140, 402), (220 + i * 18, 380, 402), 0.35)
    # 가새
    S.line((220, 620, 18), (490, 620, 380), 1.6); S.line((490, 620, 18), (220, 620, 380), 1.6)
    # 비계
    for i in range(6):
        x = 160 + i * 100
        S.line((x, 680, 0), (x, 680, 520), 1.0); S.line((x, 720, 0), (x, 720, 520), 1.0)
    for z in [130, 260, 390, 520]:
        S.line((160, 680, z), (660, 680, z), 1.0); S.line((160, 720, z), (660, 720, z), 1.0)
        S.poly([(160, 680, z), (660, 680, z), (660, 720, z), (160, 720, z)], '#fff', 0.7)
    for i in range(5):
        S.line((160 + i * 100, 720, 0 + (i % 2) * 130), (260 + i * 100, 720, 130 + (i % 2) * 130), 0.7)
    # 자재 더미, 바리케이드
    for i in range(4):
        S.box(1080, 300 + i * 0, i * 14, 160, 90, 14, sw=0.7)
    for i in range(3):
        S.cyl(1120 + i * 30, 560, 0, 12, 60, sw=0.7, n=14)
    for i in range(5):
        S.box(60 + i * 110, 840, 0, 90, 8, 70, top='#fff', fy='#f4c430' if i % 2 else '#fff', fx='#d9d5cd', sw=0.8)
    # 크레인 훅
    S.line((900, 300, 720), (900, 300, 1100), 0.8)
    S.box(890, 290, 690, 20, 20, 30, sw=0.8)
    # 사람
    person(S, (700, 560, 0), 'point', me=True, helmet=True, prop='roll', scale=1.25)
    person(S, (900, 640, 0), 'read', helmet=True, flip=True, prop='sheet', scale=1.25)
    person(S, (520, 700, 390), 'stand', helmet=True, scale=1.25)
    return S


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'img/practice'
    os.makedirs(out, exist_ok=True)
    for name, fn in [('desk', desk_scene), ('meeting', meeting_scene), ('site', site_scene)]:
        open(os.path.join(out, name + '.svg'), 'w').write(fn().svg())
    print('ok')
