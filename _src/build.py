# -*- coding: utf-8 -*-
"""정적 사이트 생성기: python3 build.py <이미지폴더> <출력폴더>
이미지폴더에는 <id>.jpg (포트폴리오 asset) 와 pg_<id>.jpg (페이지 렌더)가 있어야 함."""
import os, json, sys, shutil, html
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import SITE, PROJECTS, ABOUT, PUBLISH, PRACTICE, PROCESS
PRACTICE = sorted(PRACTICE, key=lambda i: i['year'][:4], reverse=True)

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT + '/img', exist_ok=True)
os.makedirs(OUT + '/works', exist_ok=True)
os.makedirs(OUT + '/practice', exist_ok=True)
os.makedirs(OUT + '/vid', exist_ok=True)
BK = os.environ.get('BK', os.path.join(os.path.dirname(SRC.rstrip('/')), 'bk'))
VID = os.environ.get('VID', os.path.join(os.path.dirname(SRC.rstrip('/')), 'vid'))
E = html.escape
sizes = {}

def use(i, thumb=False):
    """이미지를 출력폴더로 복사하고 (경로, w, h) 반환"""
    name = f'{i}.jpg'
    src = f'{SRC}/{name}'
    if thumb:
        dst = f'{OUT}/img/t_{name}'
        if not os.path.exists(dst):
            im = Image.open(src); im.thumbnail((1400, 1400)); im.save(dst, quality=82, optimize=True, progressive=True)
        w, h = Image.open(dst).size
        return f'img/t_{name}', w, h
    dst = f'{OUT}/img/{name}'
    if not os.path.exists(dst):
        shutil.copy(src, dst)
    w, h = Image.open(dst).size
    return f'img/{name}', w, h

def pic(i, root, cls='', alt=''):
    p, w, h = use(i)
    return f'<img class="{cls}" src="{root}{p}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{E(alt)}">'

CSS = r"""
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Nanum+Pen+Script&family=Noto+Serif+KR:wght@500&display=swap');
:root{--bg:#f6f5f2;--fg:#1d1c1a;--mute:#86827b;--line:#dedad3;--acc:#c8572f;--max:1180px;--text:680px}
.dark{--bg:#0b0b0a;--fg:#ecebe7;--mute:#8d8a84;--line:#2a2927;--acc:#e0673a}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--fg);font-family:Pretendard,-apple-system,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;font-size:16px;line-height:1.75;word-break:keep-all;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%;height:auto}
header.top{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:baseline;padding:18px clamp(16px,4vw,48px);background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px)}
header.top .name{font-weight:600;letter-spacing:.01em}
header.top .name span{color:var(--mute);font-weight:400;margin-left:.5em}
header.top nav a{margin-left:clamp(14px,2.5vw,32px);color:var(--mute);font-size:14px}
header.top nav a:hover,header.top nav a.on{color:var(--fg)}
main{padding:0 clamp(16px,4vw,48px)}
.intro{max-width:var(--max);margin:9vh auto 7vh}
.intro h1{font-size:clamp(28px,4.4vw,54px);font-weight:500;line-height:1.25;letter-spacing:-.02em}
.intro p{color:var(--mute);margin-top:18px}
.works{max-width:var(--max);margin:28px auto 14vh;display:grid;grid-template-columns:1fr 1fr;gap:72px 40px}
.work img{width:100%;transition:opacity .3s}
.work:hover img{opacity:.85}
.work .cap{display:flex;gap:14px;margin-top:14px;font-size:15px;align-items:baseline}
.work .cap .no{color:var(--mute);font-variant-numeric:tabular-nums}
.work .cap .t{font-weight:600}
.work .cap .k{color:var(--mute);margin-left:auto;font-size:13px;text-align:right}
.works{grid-template-columns:repeat(6,1fr)}
.work{grid-column:span 3}
.work:nth-child(1){grid-column:1/-1}
.work:nth-child(n+4){grid-column:span 2}
.work:nth-child(n+4) .cap .k{display:none}
/* project */
.hero{margin:0 calc(-1*clamp(16px,4vw,48px))}
.hero img{width:100%;height:auto}
.phead{max-width:var(--max);margin:64px auto 40px;display:grid;grid-template-columns:5fr 7fr;gap:40px}
.phead .no{color:var(--mute);font-size:14px}
.phead h1{font-size:clamp(30px,4vw,48px);font-weight:600;line-height:1.15;letter-spacing:-.01em;margin-top:6px}
.phead h1 small{display:block;font-size:.45em;font-weight:400;color:var(--mute);margin-top:10px;letter-spacing:0}
.phead dl{margin-top:28px;display:grid;grid-template-columns:auto 1fr;gap:4px 18px;font-size:14px}
.phead dt{color:var(--mute)}
.phead .st{font-size:clamp(19px,2vw,24px);font-weight:500;line-height:1.5;margin-bottom:20px}
.phead .body p+p{margin-top:1em}
.phead .en{color:var(--mute);font-size:14.5px;margin-top:1.2em}
.blk{max-width:var(--max);margin:0 auto 56px}
.blk.w{max-width:var(--max)}
figure img{width:100%;cursor:zoom-in}
figure video{width:100%;display:block;background:#000}
.fade{opacity:0;transform:translateY(16px);transition:opacity .8s ease,transform .8s ease}
.fade.in{opacity:1;transform:none}
#lb button{position:absolute;top:50%;transform:translateY(-50%);background:none;border:0;color:#fff;font-size:34px;padding:20px;cursor:pointer;opacity:.6}
#lb button:hover{opacity:1}
#lb .p{left:4px}#lb .n{right:4px}
#lb .c{position:absolute;bottom:14px;left:0;right:0;text-align:center;color:#aaa;font-size:13px}
.intro .lead{color:var(--fg);max-width:620px;margin-top:22px;font-size:17px}
figcaption{font-size:13px;color:var(--mute);margin-top:10px;line-height:1.55}
.row{display:grid;gap:16px;align-items:end}
.txt{max-width:var(--max);margin:96px auto 40px;display:grid;grid-template-columns:5fr 7fr;gap:40px}
.txt h2{font-size:clamp(19px,2vw,23px);font-weight:600;line-height:1.45}
.txt h2 small{display:block;font-size:13px;font-weight:400;color:var(--mute);margin-top:6px;letter-spacing:.02em}
.txt .b p+p{margin-top:1em}
ol.leg{max-width:var(--max);margin:-24px auto 56px;columns:3;font-size:14px;color:var(--mute);padding-left:1.4em}
.pnav{max-width:var(--max);margin:120px auto 0;padding:28px 0 80px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:20px;font-size:15px}
.pnav a span{display:block;color:var(--mute);font-size:13px}
.pnav a:last-child{text-align:right}
footer{max-width:var(--max);margin:0 auto;padding:0 0 48px;color:var(--mute);font-size:13px}
main>footer{padding-left:0}
/* about */
.about{max-width:var(--max);margin:10vh auto 14vh;display:grid;grid-template-columns:4fr 8fr;gap:56px}
.about img{width:100%;max-width:340px}
.about h1{font-size:clamp(28px,3.6vw,44px);font-weight:500;line-height:1.2}
.about h1 small{display:block;font-size:.42em;color:var(--mute);font-weight:400;margin-top:10px}
.about h3{font-size:13px;color:var(--mute);font-weight:500;letter-spacing:.06em;text-transform:uppercase;margin:44px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.about table{border-collapse:collapse;width:100%;font-size:15px}
.about td{padding:6px 0;vertical-align:top}
.about td:first-child{color:var(--mute);width:150px;font-variant-numeric:tabular-nums;padding-right:16px}
.about td .r{color:var(--mute)}
.about .lead{font-size:18px;margin-top:28px;max-width:var(--text)}
/* lightbox */
#lb{position:fixed;inset:0;background:rgba(10,10,9,.96);display:none;align-items:center;justify-content:center;z-index:50;cursor:zoom-out;padding:2vw}
#lb.on{display:flex}
#lb img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain}

.sec{max-width:var(--max);margin:0 auto 18px;display:flex;align-items:baseline;gap:16px;border-top:1px solid var(--line);padding-top:18px}
.sec h2{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
.sec span{color:var(--mute);font-size:13px}
.works+.sec,.cards+.sec{margin-top:0}
.cards{max-width:var(--max);margin:28px auto 14vh;display:grid;grid-template-columns:repeat(4,1fr);gap:40px 24px}
.card .im{aspect-ratio:4/5;background:color-mix(in srgb,var(--fg) 5%,var(--bg));display:flex;align-items:center;justify-content:center;overflow:hidden}
.card .im img{width:100%;height:100%;object-fit:contain}
.card .im em{font-style:normal;color:var(--mute);font-size:13px;padding:16px;text-align:center}
.card .t{font-weight:600;margin-top:12px;font-size:15px;line-height:1.4}
.card .k{color:var(--mute);font-size:13px}
.plist{max-width:var(--max);margin:28px auto 14vh;list-style:none}
.works.pw{margin-bottom:40px}
.works.pw .work,.works.pw .work:nth-child(n){grid-column:span 3}
.works.pw .work .cap .k{display:block}
.plist li{display:grid;grid-template-columns:120px 1fr auto;gap:16px;padding:14px 0;border-bottom:1px solid var(--line);align-items:baseline}
.plist .y{color:var(--mute);font-variant-numeric:tabular-nums;font-size:14px}
.plist .t{font-weight:600}
.plist .k{color:var(--mute);font-size:14px}
.card .im img{transition:transform .5s ease}a.card:hover .im img{transform:scale(1.03)}
.phead dd a,.about td a{text-decoration:underline;text-decoration-color:var(--line);text-underline-offset:3px}.phead dd a:hover,.about td a:hover{color:var(--acc)}
.bookpg{height:100vh;height:100dvh;overflow:hidden;background:#141412;user-select:none;-webkit-user-select:none}
.bookpg header.top{background:transparent;backdrop-filter:none;align-items:center}
.bookpg .bt{font-size:14px;font-weight:600}.bookpg .pdfl{margin-left:1em;color:#d9b97a;text-decoration:none;font-weight:400}.bookpg .bt em{font-style:normal;font-weight:400;color:var(--mute);margin-left:.6em}
.stage{height:calc(100dvh - 130px);display:flex;align-items:center;justify-content:center;perspective:4200px}
#book{--w:300px;--h:420px;position:relative;display:flex;width:calc(var(--w)*2);height:var(--h);transition:transform .7s cubic-bezier(.4,.1,.2,1);transform-style:preserve-3d;cursor:pointer}
#book .pg{width:var(--w);height:var(--h);position:relative;background:#1b1b19;box-shadow:0 18px 50px rgba(0,0,0,.55)}
#book .pg.empty{background:transparent;box-shadow:none}
#book img{width:100%;height:100%;object-fit:cover;display:block;pointer-events:none}
#book .L::after,#book .R::after{content:"";position:absolute;inset:0;pointer-events:none}
#book .L:not(.empty)::after{background:linear-gradient(to left,rgba(0,0,0,.35),rgba(0,0,0,0) 7%)}
#book .R:not(.empty)::after{background:linear-gradient(to right,rgba(0,0,0,.35),rgba(0,0,0,0) 7%)}
#book .spine{display:none}
.leaf{position:absolute;top:0;width:var(--w);height:var(--h);transform-style:preserve-3d;transition:transform .85s cubic-bezier(.45,.05,.25,1);z-index:5}
.leaf.fw{left:var(--w);transform-origin:left center}.leaf.fw.go{transform:rotateY(-180deg)}
.leaf.bw{left:0;transform-origin:right center}.leaf.bw.go{transform:rotateY(180deg)}
.leaf .f,.leaf .b{position:absolute;inset:0;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:#1b1b19;overflow:hidden}
.leaf .b{transform:rotateY(180deg)}
.leaf .f.empty,.leaf .b.empty{background:transparent}
.leaf .sh{position:absolute;inset:0;opacity:0;transition:opacity .85s;pointer-events:none}
.leaf.fw .f .sh{background:linear-gradient(to left,rgba(0,0,0,.5),transparent 60%)}.leaf.fw .b .sh{background:linear-gradient(to left,rgba(0,0,0,.4),transparent 40%)}
.leaf.bw .f .sh{background:linear-gradient(to right,rgba(0,0,0,.5),transparent 60%)}.leaf.bw .b .sh{background:linear-gradient(to right,rgba(0,0,0,.4),transparent 40%)}
.leaf.go .f .sh{opacity:1}.leaf .b .sh{opacity:1}.leaf.go .b .sh{opacity:0}
#book.one{width:var(--w)}#book.one .L{display:none}#book.one .R::after{display:none}
.bctl{display:flex;justify-content:center;align-items:center;gap:22px;color:var(--mute);font-size:13px;font-variant-numeric:tabular-nums}
.bctl button{background:none;border:1px solid var(--line);color:var(--fg);width:40px;height:40px;border-radius:50%;font-size:22px;line-height:1;cursor:pointer}
.bctl button:disabled{opacity:.25;cursor:default}
.bhint{text-align:center;color:var(--mute);font-size:12px;margin-top:8px;opacity:.7}
@media (max-width:760px){.cards{grid-template-columns:1fr 1fr}.plist li{grid-template-columns:70px 1fr}.plist .k{grid-column:2}}
@media (max-width:760px){
  .works{grid-template-columns:1fr;gap:48px}
  .work,.work:nth-child(n+4){grid-column:1/-1}
  .phead,.txt,.about{grid-template-columns:1fr;gap:20px}
  .txt{margin-top:64px}
  .row.g{grid-template-columns:1fr 1fr!important}
  .row.g>div:last-child:nth-child(odd){grid-column:1/-1}
  ol.leg{columns:1}
  header.top .name span{display:none}
  .work .cap .k{display:none}
}

/* ---- v2 index */
.mhero{display:block;position:relative;margin:0 calc(-1*clamp(16px,4vw,48px));height:calc(100svh - 62px);min-height:460px;overflow:hidden;color:#fff}
.mhero img{width:100%;height:100%;object-fit:cover}
.mhero::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.55),rgba(0,0,0,0) 45%)}
.mh-t{position:absolute;left:clamp(16px,4vw,48px);bottom:clamp(56px,9vh,96px);z-index:1}
.mh-t h1{font-size:clamp(34px,6vw,84px);font-weight:600;line-height:1.05;letter-spacing:-.025em}
.mh-t h1 span{font-weight:300}
.mh-t p{font-size:clamp(15px,1.4vw,19px);opacity:.85;margin-top:10px}
.mh-c{position:absolute;left:clamp(16px,4vw,48px);right:clamp(16px,4vw,48px);bottom:22px;z-index:1;font-size:13px;display:flex;gap:10px;align-items:baseline;border-top:1px solid rgba(255,255,255,.35);padding-top:12px}
.mh-c span{opacity:.75}.mh-c span:last-child{margin-left:auto}
.mhero:hover img{transform:scale(1.015)}.mhero img{transition:transform 1.2s ease}
.intro{max-width:var(--max);margin:12vh auto 14vh;display:grid;grid-template-columns:4fr 8fr;gap:40px}
.intro .sch{color:var(--mute);margin:0;font-size:14px;padding-top:6px}
.intro .lead{font-size:clamp(19px,2vw,26px);line-height:1.6;margin:0;max-width:none;font-weight:400;letter-spacing:-.01em}
.sec{padding-top:22px;margin-bottom:28px}
.sec h2{font-size:clamp(22px,2.4vw,30px);font-weight:500;letter-spacing:-.01em;text-transform:none}
.sec span{font-size:14px}
.works{grid-template-columns:repeat(6,1fr);gap:64px 32px}
.work,.work:nth-child(n){grid-column:span 3}
.work:nth-child(n+3){grid-column:span 2}
.work .ph{aspect-ratio:4/3;overflow:hidden;background:color-mix(in srgb,var(--fg) 6%,var(--bg))}
.work .ph img{width:100%;height:100%;object-fit:cover;transition:transform .6s ease,opacity .3s}
.work:hover .ph img{transform:scale(1.03);opacity:1}
.work:nth-child(n+3) .cap .k{display:block}
.works.pw .work:nth-child(n){grid-column:span 3}
.works.pw .work:first-child{grid-column:1/-1}.works.pw .work:first-child .ph{aspect-ratio:21/9}
.cards{grid-template-columns:4fr 4fr 4fr;gap:32px;align-items:start}
.cnote{color:var(--mute);font-size:15px;max-width:280px}
.card .im{aspect-ratio:4/5}
.plist{margin-top:0}
@media (max-width:760px){
 .mhero{height:78svh}
 .intro{grid-template-columns:1fr;gap:14px;margin:8vh auto 10vh}
 .works,.works.pw{grid-template-columns:1fr;gap:44px}
 .work,.work:nth-child(n),.works.pw .work:nth-child(n){grid-column:1/-1}
 .cards{grid-template-columns:1fr 1fr}.cnote{grid-column:1/-1}
 .mh-c span:nth-child(3){display:none}
}

/* ---- C: index list */
.ix{max-width:var(--max);margin:9vh auto 16vh;display:grid;grid-template-columns:7fr 5fr;gap:56px;align-items:start}
.ixh{grid-column:1/-1;margin-bottom:20px}
.ixh h1{font-size:clamp(36px,5.4vw,68px);font-weight:600;letter-spacing:-.025em;line-height:1.08}
.ixh h1 span{font-weight:300}
.ixh .sub{color:var(--mute);margin-top:10px;font-size:15px}
.ixh .lead{max-width:640px;margin-top:28px;font-size:17px;line-height:1.75}
.ixl{list-style:none;border-top:1px solid var(--fg)}
.ixl a{display:grid;grid-template-columns:44px 1fr auto;gap:12px;align-items:baseline;padding:20px 0;border-bottom:1px solid var(--line);transition:padding .35s ease,color .25s}
.ixl .n{color:var(--mute);font-size:13px;font-variant-numeric:tabular-nums}
.ixl .t{font-size:clamp(24px,2.7vw,38px);font-weight:500;letter-spacing:-.015em;line-height:1.15}
.ixl .k{color:var(--mute);font-size:13px;text-align:right}
.ixl .mt{display:none}
.ixl:hover a{color:var(--mute)}.ixl:hover a .t{color:color-mix(in srgb,var(--fg) 35%,var(--bg))}
.ixl li.on a,.ixl li:hover a{padding-left:14px}.ixl li:hover a .t,.ixl li.on a .t{color:var(--fg)}
.pv{position:sticky;top:96px;aspect-ratio:4/5;overflow:hidden;background:color-mix(in srgb,var(--fg) 6%,var(--bg))}
.pv img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .45s ease,transform 1.4s ease;transform:scale(1.04)}
.pv img.on{opacity:1;transform:none}
@media (max-width:760px){
 .ix{grid-template-columns:1fr;gap:0;margin:6vh auto 12vh}.pv{display:none}
 .ixl a{grid-template-columns:32px 1fr;padding:16px 0}.ixl .k{grid-column:2;text-align:left;margin-top:-6px}
 .ixl .mt{display:block;grid-column:1/-1;width:100%;height:58vw;object-fit:cover;margin-top:10px}
 .ixl:hover a{color:inherit}.ixl:hover a .t{color:var(--fg)}.ixl li:hover a{padding-left:0}
}

/* ---- C2: render | drawing stage + rising card */
.ix{grid-template-columns:5fr 7fr;gap:48px}
.ixl .t{font-size:clamp(22px,2.3vw,34px)}
.ixl .ms{display:none}
.ixl a{grid-template-columns:40px 1fr;row-gap:2px;padding:18px 0}
.ixl .k{grid-column:2;text-align:left}
.stg{position:sticky;top:84px;aspect-ratio:4/3;max-height:calc(100vh - 110px);width:100%}
.stg .sl{position:absolute;inset:0;display:grid;grid-template-columns:1fr 1fr;opacity:0;visibility:hidden;transition:opacity .45s ease,visibility 0s .45s}
.stg .sl.on{opacity:1;visibility:visible;transition:opacity .45s ease}
.stg .r,.stg .d{overflow:hidden;position:relative}
.stg .r img{width:100%;height:100%;object-fit:cover;transform:scale(1.04);transition:transform 1.4s ease}
.stg .sl.on .r img{transform:none}
.stg .d{background:#ecebe6;display:flex;align-items:center;justify-content:center;padding:6%}
.stg .d img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;mix-blend-mode:multiply}
.stg .cd{position:absolute;left:0;bottom:0;width:56%;background:#d8b04a;color:#1d1c1a;padding:22px 24px 20px;transform:translateY(24px);opacity:0;transition:transform .55s cubic-bezier(.2,.7,.2,1) .12s,opacity .4s ease .12s}
.stg .sl.on .cd{transform:none;opacity:1}
.stg .cd .cn{font-size:12px;opacity:.7;display:block}
.stg .cd b{display:block;font-size:22px;font-weight:600;letter-spacing:-.01em;margin-top:6px;line-height:1.2}
.stg .cd p{font-size:16px;line-height:1.55;margin-top:10px}
.stg .cd .go{display:inline-block;font-size:13px;margin-top:14px;border-bottom:1px solid currentColor}
.stg .sl:hover .cd .go{opacity:.7}
@media (max-width:760px){
 .ix{grid-template-columns:1fr;gap:0}
 .ixl li.on a,.ixl li:hover a{padding-left:0}
 .ixl a{grid-template-columns:32px 1fr}
 .stg{display:none}
 .ixl .ms{display:block;grid-column:1/-1;font-size:15px;color:var(--fg);margin-top:8px}
}

/* contact */
.contact{max-width:var(--max);margin:0 auto 12vh}
.contact .sec{margin-bottom:36px}
.ct .big{display:block;font-size:clamp(28px,4.6vw,60px);font-weight:500;letter-spacing:-.02em;line-height:1.2;width:fit-content;border-bottom:2px solid transparent;transition:border-color .25s,color .25s}
.ct .big:hover{border-color:currentColor;color:var(--acc)}
.ct p{color:var(--mute);margin-top:24px;font-size:15px}
@media (max-width:760px){header.top nav a{margin-left:12px;font-size:13px}}
.blk.nr img{max-width:560px;width:100%}

/* process */
.phd{max-width:var(--max);margin:10vh auto 10vh}
.phd .k{color:var(--mute);font-size:14px}
.phd h1{font-size:clamp(34px,5vw,64px);font-weight:600;letter-spacing:-.025em;line-height:1.1;margin-top:8px}
.phd h1 small{display:block;font-size:.32em;font-weight:400;color:var(--mute);letter-spacing:0;margin-top:14px}
.phd .lead{max-width:720px;margin-top:28px;font-size:18px;line-height:1.75}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:56px;border-top:1px solid var(--fg);padding-top:20px}
.stats b{display:block;font-size:clamp(30px,3.6vw,48px);font-weight:500;letter-spacing:-.02em}
.stats span{color:var(--mute);font-size:14px}
.pstep{max-width:var(--max);margin:0 auto;display:grid;grid-template-columns:4fr 8fr;gap:40px;padding:56px 0;border-top:1px solid var(--line)}
.pstep .no{color:var(--mute);font-size:14px;font-variant-numeric:tabular-nums}
.pstep h2{font-size:clamp(24px,2.6vw,34px);font-weight:500;letter-spacing:-.015em;line-height:1.2;margin-top:6px;position:sticky;top:90px}
.pstep h2 small{display:block;font-size:14px;color:var(--mute);font-weight:400;margin-top:8px;letter-spacing:0}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:2px;background:var(--line)}
.cmp>div{background:var(--bg);padding:18px 20px}
.cmp .ai{background:color-mix(in srgb,#a9b89a 28%,var(--bg))}
.cmp h4{font-size:12px;font-weight:600;letter-spacing:.06em;color:var(--mute);margin-bottom:8px}
.cmp p{font-size:15.5px;line-height:1.7}
.hm{margin-top:16px;font-size:15px}.hm b{font-weight:600;margin-right:8px}
pre.code{margin-top:20px;background:#1d1c1a;color:#e9e4d8;padding:18px 20px;font:13px/1.65 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;overflow-x:auto;white-space:pre}
pre.code .f{display:block;color:#a9b89a;font-family:Pretendard,sans-serif;font-size:12px;margin-bottom:10px}
.f2{margin-top:16px;color:var(--mute);font-size:13px}
.pfig{margin-top:20px}.pfig img{width:100%;height:auto;max-height:78vh;object-fit:contain;object-position:left;display:block}.pfig figcaption{margin-top:8px;color:var(--mute);font-size:13px}
.flow{list-style:none;display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin:18px 0 6px;counter-reset:f}
.flow li{border-top:2px solid #1d1c1a;padding:10px 14px 0 0;position:relative}.flow li:not(:last-child):after{content:'→';position:absolute;right:10px;top:8px}
.flow b{display:block;font-size:15px}.flow span{font-size:13px;opacity:.75}
@media (max-width:760px){.flow{grid-template-columns:1fr 1fr}}
.imgph{margin-top:20px;aspect-ratio:16/9;border:1px dashed var(--line);display:flex;align-items:center;justify-content:center;color:var(--mute);font-size:13px}
.pnote{max-width:var(--max);margin:24px auto 56px;background:#d8b04a;color:#1d1c1a;padding:28px 32px}
.pnote h3{font-size:18px;font-weight:600}
.pnote ul{margin-top:12px;padding-left:1.2em}.pnote li{margin-top:6px;font-size:15.5px}
@media (max-width:760px){.stats{grid-template-columns:1fr 1fr}.pstep{grid-template-columns:1fr;gap:16px}.pstep h2{position:static}.cmp{grid-template-columns:1fr}}

pre.code.ask{white-space:pre-wrap;font:14px/1.75 Pretendard,sans-serif;background:#ecebe6;color:#1d1c1a;border-left:3px solid #1d1c1a}
pre.code.ask .f{color:var(--mute)}
.lab{max-width:var(--max);margin:8px auto 64px;background:#1d1c1a;color:#ecebe6;padding:32px}
.lab .k{color:#a9b89a;font-size:13px}
.lab h3{font-size:clamp(22px,2.4vw,30px);font-weight:500;margin-top:6px}
.lh>p:last-child{max-width:760px;margin-top:10px;font-size:15px;line-height:1.7;opacity:.85}
.lbody{display:grid;grid-template-columns:260px 1fr;gap:32px;margin-top:28px}
.lctl fieldset{border:0;margin-bottom:18px}
.lctl legend{font-size:12px;color:#a9b89a;letter-spacing:.05em;margin-bottom:6px}
.lctl label{display:grid;grid-template-columns:84px 1fr 38px;align-items:center;gap:8px;font-size:13px;margin:4px 0}
.lctl input{width:100%;accent-color:#d48f62}
.lctl output{text-align:right;font-variant-numeric:tabular-nums;opacity:.8}
.reroll{width:100%;padding:10px;background:#d48f62;color:#1d1c1a;border:0;font:600 14px Pretendard,sans-serif;cursor:pointer}
.lsum{font-size:15px}.lsum b{color:#d48f62;font-weight:600}
.lhist{position:relative;height:56px;display:flex;align-items:flex-end;gap:2px;margin:12px 0 22px;border-bottom:1px solid #555}
.lhist i{flex:1;background:#555;min-height:1px}.lhist i.on{background:#a9b89a}
.lhist em{position:absolute;top:0;bottom:0;border-left:1px dashed #d48f62}
.lpick{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:26px}
.lpick figure{background:#f6f5f2;color:#1d1c1a;padding:12px}
.lpick .lpv svg{width:100%;height:auto;display:block}
.lpick text{font-family:Pretendard,sans-serif;fill:#1d1c1a}
.lpick .sc{font-size:13px;color:var(--mute);margin:6px 0}.lpick .sc b{font-size:22px;color:#1d1c1a;font-weight:600}
.bar{display:grid;grid-template-columns:30px 1fr 24px;gap:6px;align-items:center;font-size:12px;margin:2px 0}
.bar i{height:5px;background:linear-gradient(90deg,#1d1c1a var(--v),#dedad3 var(--v))}.bar b{font-weight:500;text-align:right}
.adjl{display:flex;flex-wrap:wrap;gap:2px 10px;font-size:11px;margin-top:6px}.adjl .no{color:#c8572f}
.lpick .none{grid-column:1/-1;opacity:.8}
.lgrid{display:grid;grid-template-columns:repeat(12,1fr);gap:4px;margin-top:8px}
.lgrid .t{position:relative;background:#2a2927;padding:3px}.lgrid .t svg{width:100%;height:auto;aspect-ratio:1;display:block}
.lgrid .t span{position:absolute;right:3px;bottom:1px;font-size:9px;opacity:.7}
.lgrid .low{opacity:.25}.lgrid .pk{outline:2px solid #d48f62}
@media (max-width:900px){.lbody{grid-template-columns:1fr}.lpick{grid-template-columns:1fr 1fr}.lgrid{grid-template-columns:repeat(6,1fr)}.lgrid .t:nth-child(n+37){display:none}.lab{padding:22px 16px}}

/* lab mood */
.labpg{--bg:#121311;--fg:#e6e4dc;--mute:#8a8a80;--line:#2c2e2a;--mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
 background-color:var(--bg);background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px),linear-gradient(#ffffff04 1px,transparent 1px),linear-gradient(90deg,#ffffff04 1px,transparent 1px);background-size:120px 120px,120px 120px,24px 24px,24px 24px}
.labpg header.top{background:color-mix(in srgb,var(--bg) 88%,transparent)}
.labpg .phd .k,.labpg .log,.labpg .pstep .no,.labpg .st,.labpg .cmp h4,.labpg .lab .k,.labpg .lctl legend,.labpg pre.code .f,.labpg .hm b{font-family:var(--mono);letter-spacing:.02em}
.labpg .phd .k{color:#b6d36b}
.labpg .log{color:var(--mute);font-size:12px;margin-top:6px}
.labpg .log:before{content:'';display:inline-block;width:7px;height:7px;border-radius:50%;background:#b6d36b;margin-right:8px;box-shadow:0 0 8px #b6d36b;animation:blink 1.6s infinite}
@keyframes blink{50%{opacity:.25}}
.labpg .pstep{border-top:1px dashed var(--line)}
.labpg .pstep .no{color:#b6d36b;font-size:12px}
.labpg .st{display:inline-block;margin-left:10px;font-size:11px;color:var(--mute);border:1px solid var(--line);padding:1px 7px}
.labpg .st.on{color:#121311;background:#b6d36b;border-color:#b6d36b}
.labpg .cmp{background:var(--line)}
.labpg .cmp>div{background:#171816}
.labpg .cmp .ai{background:#1c2117}
.labpg .cmp .ai h4{color:#b6d36b}
.labpg pre.code.ask{background:#0c0d0b;color:#d8d6cc;border:1px solid var(--line);border-left:3px solid #b6d36b;font-family:var(--mono);font-size:13px}
.labpg pre.code.ask .f{color:#b6d36b}

.labpg .pnote{background:transparent;color:var(--fg);border:1px solid #b6d36b}
.labpg .pnote h3{font-family:var(--mono);font-size:15px;color:#b6d36b}
.labpg .flow li{border-top-color:#b6d36b}
.labpg .lab{background:#0c0d0b;border:1px solid #b6d36b;box-shadow:0 0 0 6px #121311,0 0 0 7px var(--line)}
.labpg .lab .k{color:#b6d36b}
.labpg .lsum b{color:#b6d36b}.labpg .lhist i.on{background:#b6d36b}
.labpg .reroll{background:#b6d36b}
.labpg .lctl input{accent-color:#b6d36b}
.labpg .lgrid .pk{outline-color:#b6d36b}

.labcard{max-width:var(--max);margin:0 auto 56px;display:grid;grid-template-columns:5fr 7fr;border:1px solid #b6d36b;background:#0c0d0b;color:inherit;text-decoration:none;transition:background .2s}
.labcard:hover{background:#1c2117}
.labcard img{width:100%;height:240px;object-fit:cover;object-position:left top;display:block}
.labcard>div{padding:26px 30px;display:flex;flex-direction:column;gap:8px}
.labcard .k{font-family:var(--mono);color:#b6d36b;font-size:12px}
.labcard h3{font-size:clamp(20px,2.2vw,28px);font-weight:500}
.labcard p{font-size:15px;opacity:.85}
.labcard .go{margin-top:auto;font-family:var(--mono);font-size:13px;color:#b6d36b}
.labpg .lab{margin-top:40px}
.lab .k a{color:inherit}
@media (max-width:760px){.labcard{grid-template-columns:1fr}.labcard img{min-height:0;aspect-ratio:16/9}}

.labs{margin-top:18px;border:1px solid var(--line)}
.labs summary{cursor:pointer;list-style:none;padding:10px 14px;font-family:var(--mono);font-size:13px;color:#b6d36b;display:flex;justify-content:space-between}
.labs summary::-webkit-details-marker{display:none}
.labs summary:after{content:'+'}.labs[open] summary:after{content:'−'}
.labs ul{list-style:none;border-top:1px solid var(--line)}
.labs li a{display:grid;grid-template-columns:64px 1fr 20px;gap:4px 12px;padding:12px 14px;color:inherit;text-decoration:none;border-top:1px solid var(--line)}
.labs li:first-child a{border-top:0}
.labs li a:hover{background:#1c2117}
.labs .ln{font-family:var(--mono);font-size:12px;color:#b6d36b;padding-top:3px}
.labs b{font-weight:500}.labs em{grid-column:2;font-style:normal;font-size:13px;color:var(--mute)}
.labs i{grid-row:1;grid-column:3;font-style:normal;color:#b6d36b}

.embed header.top,.embed footer{display:none}.embed .labpg,.embed body{background:#0c0d0b}.embed .lab{margin:0;border:0;box-shadow:none}.embed main{padding:0}
.app{display:grid;grid-template-columns:240px 1fr;gap:28px;margin-top:26px}
.app .lctl select{width:100%;background:#1c2117;color:inherit;border:1px solid var(--line);padding:3px}
.nlv{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.cv canvas{width:100%;height:420px;display:block;background:#121311;border:1px solid var(--line);touch-action:none}
.cv .iso{cursor:grab}.cv .top{cursor:crosshair}
.cv.sheet canvas{background:#fbfbf8;border:0}
.hint{font-family:var(--mono);font-size:11px;color:var(--mute);margin-top:6px}
.nls{grid-column:2;display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}
.nls div{background:#0c0d0b;padding:10px 12px}.nls span{display:block;font-size:12px;color:var(--mute)}.nls b{font-family:var(--mono);font-weight:500;font-size:15px}
.nls .hi b{color:#b6d36b}.nls .ng b{color:#ff6b4a!important}
.nls .note{grid-column:1/-1;background:#0c0d0b;padding:10px 12px;font-size:13px;color:var(--mute)}
@media (max-width:900px){.app{grid-template-columns:1fr}.nlv{grid-template-columns:1fr}.nls{grid-column:1;grid-template-columns:1fr 1fr}.cv canvas{height:320px}}

.agrid{max-width:1480px;margin:0 auto 12vh;padding:0 24px;display:grid;grid-template-columns:1fr 1fr;gap:18px}
.acard{background:#151513!important;border:1px solid #2c2e2a!important;box-shadow:none!important;padding:16px 18px!important;margin:0!important}
.acard header{display:flex;align-items:baseline;gap:10px;font-family:var(--mono)}
.acard header b{font-size:12px;letter-spacing:.14em;color:#e0a15a;font-weight:500}
.acard header span{font-size:11px;color:var(--mute)}
.acard header a{margin-left:auto;color:var(--mute);text-decoration:none;font-size:15px}.acard header a:hover{color:#b6d36b}
.acard .app{display:block;margin-top:10px}
.acard .lctl,.acard .nls .note{display:none}
.acard .nlv{gap:0;border-top:1px solid #2c2e2a}
.acard .cv canvas{height:300px}
.acard .nlv .cv+.cv canvas{border-left:1px solid #2c2e2a}
.acard .hint{font-size:10px;margin:4px 0 0}
.acard .nls{display:block;background:none;border:0;margin-top:8px;font-family:var(--mono);font-size:11px;line-height:1.7;color:#cfcac0}
.acard .nls div{display:inline;background:none;padding:0}
.acard .nls span{display:inline;font-size:11px}.acard .nls span:after{content:': '}
.acard .nls b{font-size:11px;font-weight:400}.acard .nls div:not(:last-of-type):after{content:'  |  ';color:#555}
.cv.sheet canvas{background:#151513}
@media (max-width:1100px){.agrid{grid-template-columns:1fr}}
@media (max-width:760px){.agrid{padding:0 12px}.acard .nlv{grid-template-columns:1fr}.acard .nlv .cv+.cv canvas{border-left:0}}

/* ===== 표지 */
.coverpg{--bg:#0d0d0c;--fg:#efede6;--mute:#8b887f;--line:#2a2927}
.coverpg header.top,.coverpg footer{display:none}.coverpg main{padding:0}
.cv0{position:relative;min-height:100vh;min-height:100svh;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr auto;padding:5vh 5vw 4vh;gap:4vh 6vw;overflow:hidden}
.bgs{position:absolute;inset:0;z-index:0}
.bg{position:absolute;inset:0;background-size:cover;background-position:center;opacity:0;transition:opacity .6s ease,transform 1.6s ease;transform:scale(1.04);filter:brightness(.42) saturate(.85)}
.bg.on{opacity:1;transform:none}
.abtg canvas{position:absolute;inset:0}
.abtg .smap{--w:min(66vw,980px);position:absolute;width:var(--w);left:calc(40% - var(--fx) * var(--w));top:calc(42% - var(--fy) * var(--w) * var(--ar));overflow:visible}
.smap path{fill:none;stroke-linejoin:round;stroke-linecap:round}
.smap .mz{transition:transform .4s}.abtg.on .smap .mz{transform:scale(1.16);transition:transform 2.6s cubic-bezier(.3,0,.2,1) .8s}
.smap .rv{stroke:#26363b;stroke-width:9;opacity:0;transition:opacity .3s}.abtg.on .smap .rv{opacity:.9;transition:opacity 1s .5s}
.smap .dg{stroke:#ece8de;stroke-width:.3;opacity:0;transition:opacity .3s}.abtg.on .smap .dg{opacity:.15;transition:opacity 1.2s .7s}
.smap .gg{stroke:#ece8de;stroke-opacity:.42;stroke-width:.55;stroke-dasharray:1;stroke-dashoffset:1;transition:stroke-dashoffset .3s}
.smap .og{stroke:#ece8de;stroke-width:.8;stroke-dasharray:1;stroke-dashoffset:1;transition:stroke-dashoffset .3s}
.abtg.on .smap .og{stroke-dashoffset:0;transition:stroke-dashoffset 1.5s cubic-bezier(.5,0,.3,1) .1s}.abtg.on .smap .gg{stroke-dashoffset:0;transition:stroke-dashoffset 1.5s cubic-bezier(.5,0,.3,1) .4s}
.smap .pk{fill:#e0603a;stroke:#121311;stroke-width:.5}.smap .pd{fill:#121311}
.smap .pk,.smap .pd{opacity:0}.abtg.on .smap .pk,.abtg.on .smap .pd{animation:pdrop .55s cubic-bezier(.3,1.5,.5,1) 1.7s both}
@keyframes pdrop{0%{opacity:0;transform:translateY(-22px)}40%{opacity:1}100%{opacity:1;transform:none}}
.smap .pr1,.smap .pr2{fill:none;stroke:#e0603a;stroke-width:.5;opacity:0;transform-box:fill-box;transform-origin:center}
.abtg.on .smap .pr1{animation:pls 2.2s ease-out 2.2s infinite}.abtg.on .smap .pr2{animation:pls 2.2s ease-out 3.3s infinite}
@keyframes pls{0%{opacity:.8;transform:scale(.6)}100%{opacity:0;transform:scale(4.5)}}
.smap .ld{stroke:#e0603a;stroke-width:.4;stroke-dasharray:70;stroke-dashoffset:70}.abtg.on .smap .ld{stroke-dashoffset:0;transition:stroke-dashoffset .6s ease 2.1s}
.smap text{fill:#ece8de;opacity:0;letter-spacing:0;text-transform:none;paint-order:stroke;stroke:#121311;stroke-width:1.1px;stroke-linejoin:round;font-family:'Wanted Sans','Pretendard',system-ui,sans-serif}.smap .t1{font-size:4.3px;font-weight:600}.smap .t2{font-size:3px;fill:#cfc9bc}.smap .t3{font-size:2.4px;font-family:'JetBrains Mono',ui-monospace,monospace;fill:#e0603a;letter-spacing:.05px!important}
.abtg.on .smap text{opacity:1;transition:opacity .5s 2.5s}.abtg.on .smap .t2{transition-delay:2.65s}.abtg.on .smap .t3{transition-delay:2.8s}
@media (max-width:860px){.abtg .smap{--w:150vw;left:calc(45% - var(--fx) * var(--w))}}
.bg.grid{background-color:#121311;background-image:linear-gradient(#ffffff10 1px,transparent 1px),linear-gradient(90deg,#ffffff10 1px,transparent 1px);background-size:48px 48px;filter:none}
.cvh,.cvm,.cvf{position:relative;z-index:1}
.cvh{align-self:end}
.cvh>p:first-child{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.cvh h1{font-size:clamp(64px,11vw,180px);font-weight:700;letter-spacing:-.05em;line-height:.92;margin-top:2vh}
.cvh h1 span{display:block;font-size:.3em;font-weight:400;letter-spacing:-.01em;color:var(--mute);margin-top:.5em}
.cvh .tag{max-width:440px;margin-top:4vh;font-size:15px;line-height:1.75;color:#c9c6bd}
.cvm{list-style:none;align-self:end;justify-self:end;width:min(100%,520px)}
.cvm a{display:grid;grid-template-columns:40px 1fr auto;align-items:baseline;gap:12px;padding:10px 0;border-top:1px solid #ffffff22;color:inherit;text-decoration:none;transition:opacity .3s,padding .3s}
.cvm li:last-child a{border-bottom:1px solid #ffffff22}
.cvm .n{font-size:12px;color:var(--mute);font-variant-numeric:tabular-nums}
.cvm .w{font-size:clamp(30px,3.6vw,54px);font-weight:500;letter-spacing:-.03em;line-height:1.1}
.cvm .c{font-size:13px;color:var(--mute)}
.cvm.hov a{opacity:.35}.cvm.hov a.on{opacity:1;padding-left:14px}
.cvf{grid-column:1/-1;display:flex;justify-content:space-between;gap:16px;font-size:13px;color:var(--mute)}.sunr{font-family:var(--mono,ui-monospace,monospace);font-size:11px;letter-spacing:.04em}.cvf a{color:inherit}
@media (max-width:860px){.cv0{grid-template-columns:1fr;padding:8vh 20px 4vh}.cvm{justify-self:stretch}.cvf{flex-direction:column;gap:4px}}

/* ===== 공통 페이지 머리 */
.pk{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}
.ixh h1 span{color:var(--mute);font-weight:400}

/* ===== Publish: 서가 */
.pubpg{--bg:#1d1916;--fg:#efe6d6;--mute:#a39784;--line:#3a322b}
.pubpg header.top{background:color-mix(in srgb,#1d1916 90%,transparent)}
.shelfh{max-width:var(--max);margin:12vh auto 8vh}
.shelfh h1{font-family:'Noto Serif KR',Georgia,serif;font-size:clamp(56px,9vw,140px);font-weight:500;letter-spacing:-.03em;line-height:1;margin-top:12px}
.shelfh>p:last-child{max-width:420px;margin-top:20px;color:var(--mute)}
.shelf{max-width:var(--max);margin:0 auto 16vh;display:grid;grid-template-columns:1fr 1fr;gap:8vw;padding:6vh 0 0;border-top:1px solid var(--line)}
.bk{color:inherit;text-decoration:none;display:grid;grid-template-rows:auto auto;gap:28px;perspective:1600px}
.bk .obj{position:relative;width:72%;margin:0 auto;transform:rotateY(-24deg) rotateX(4deg);transform-style:preserve-3d;transition:transform .7s cubic-bezier(.2,.7,.2,1);box-shadow:30px 34px 50px rgba(0,0,0,.55)}
.bk .obj img{display:block;width:100%;height:auto}
.bk .obj i{position:absolute;inset:0 auto 0 0;width:6%;background:linear-gradient(90deg,rgba(0,0,0,.45),rgba(255,255,255,.12) 60%,rgba(0,0,0,.1))}
.bk:hover .obj{transform:rotateY(-4deg) rotateX(0) translateY(-10px)}
.bk .meta{display:grid;gap:4px;text-align:center}
.bk .meta span{font-size:12px;letter-spacing:.1em;color:var(--mute)}
.bk .meta b{font-family:'Noto Serif KR',Georgia,serif;font-size:28px;font-weight:500}
.bk .meta em{font-style:italic;color:var(--mute);font-size:14px}
.bk .meta u{text-decoration:none;font-size:13px;margin-top:8px;color:#d9b97a}
.bk.paper .obj{width:62%;box-shadow:6px 6px 0 -1px #e9e5dc,12px 12px 0 -2px #d8d3c8,30px 34px 50px rgba(0,0,0,.55)}.bk.paper .obj i{display:none}.bk.paper .meta b{font-size:20px;line-height:1.4;max-width:24em;margin:0 auto;word-break:keep-all}
@media (max-width:760px){.shelf{grid-template-columns:1fr;gap:10vh}}

/* ===== Practice: 원장 */
.ledpg{--bg:#f4f3ef;--fg:#111;--mute:#7b7a75;--line:#111}
.ledh{max-width:var(--max);margin:12vh auto 0}
.ledh h1{font-size:clamp(48px,8vw,124px);font-weight:600;letter-spacing:-.045em;line-height:.95;margin:16px 0 8vh}
.lcol,.lr{display:grid;grid-template-columns:110px 168px 1.3fr 1fr 30px;gap:24px;align-items:center}
.lr .th{display:block;aspect-ratio:4/3;overflow:hidden;background:#11111108}.lr .th:empty{background:none}.lr .th img{width:100%;height:100%;object-fit:cover;display:block;filter:grayscale(.15);transition:transform .5s,filter .3s}.lr.f:hover .th img{transform:scale(1.06);filter:none}
.lcol{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);padding-bottom:10px;border-bottom:2px solid #111}
.ledger{max-width:var(--max);margin:0 auto 16vh}
.lr{padding:22px 0;border-bottom:1px solid #11111133;color:inherit;text-decoration:none;transition:background .2s,padding .2s}
.lr .y{font-variant-numeric:tabular-nums;font-size:15px;font-weight:600}
.lr .t b{display:block;font-size:clamp(18px,1.8vw,24px);font-weight:600;letter-spacing:-.01em;line-height:1.3}
.lr .t small{display:block;font-size:13px;color:var(--mute);margin-top:4px}
.lr .r{font-size:14px;color:#333}
.lr .go{font-size:18px}
.lr.f:hover{background:#111;color:#f4f3ef;padding-left:16px;padding-right:16px}.lr.f:hover .r,.lr.f:hover small{color:#bbb}
.lpv{position:fixed;left:0;top:0;width:320px;aspect-ratio:4/3;object-fit:cover;pointer-events:none;opacity:0;transition:opacity .25s;z-index:30;box-shadow:0 20px 40px rgba(0,0,0,.3)}
.lpv.on{opacity:1}
@media (max-width:760px){.lcol{display:none}.lr{grid-template-columns:96px 1fr 20px;column-gap:14px;row-gap:4px}.lr .y{grid-column:2;grid-row:1}.lr .th{grid-column:1;grid-row:1/4}.lr .t{grid-column:2}.lr .r{grid-column:2;font-size:13px}.lr .go{grid-row:1;grid-column:3}.lr .th:empty{display:none}.lr:not(.f) .y,.lr:not(.f) .t,.lr:not(.f) .r{grid-column:1/3}}

.cv0 .cad{position:absolute;inset:0;width:100%;height:100%;z-index:0;display:block}.cdr{font:11px 'JetBrains Mono',ui-monospace,monospace;letter-spacing:.04em;color:#ff8a6e}.cv0 .cvo{position:absolute;inset:0;z-index:0;background:linear-gradient(90deg,#0d0c0bcc 0%,#0d0c0b55 45%,#0d0c0b99 100%),linear-gradient(0deg,#0d0c0bb3 0%,transparent 40%)}@media (prefers-reduced-motion:reduce){.cv0 .cvv{display:none}}
.cv0 .bgs{z-index:0}

.lio{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:8px;align-items:flex-start;margin-top:4px}
.app .lio{grid-column:2}
.lio>button,.lio .up,.lio .ap{background:#1c2117;color:#b6d36b;border:1px solid #3c4a2a;font:12px var(--mono);padding:6px 12px;cursor:pointer}
.lio>button:hover,.lio .up:hover{background:#26301b}
.lin{flex-basis:100%;border:1px solid var(--line);padding:0}
.lin summary{cursor:pointer;padding:6px 12px;font:12px var(--mono);color:#b6d36b}
.lin p{font-size:12px;color:var(--mute);padding:0 12px}.lin code{color:#e6e3da}
.lin textarea{width:calc(100% - 24px);margin:8px 12px;background:#0c0d0b;color:#e6e3da;border:1px solid var(--line);font:12px/1.5 var(--mono);padding:8px}
.lin div{display:flex;gap:8px;align-items:center;padding:0 12px 12px}.lin .up input{display:none}.lin .msg{font-size:12px;color:var(--mute)}
@media (max-width:600px){header.top .name span,header.top nav a[href$="#contact"]{display:none}header.top nav a{margin-left:12px;font-size:13px}}
/* 표지 인트로: 가운데 작은 창에서 이미지가 빠르게 바뀌고, 창이 화면 가득 열린다 */
.ifr{position:absolute;inset:0;z-index:0;pointer-events:none}.ifr img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0}
.ifr img.on{opacity:1}.ifr.out img{transition:opacity 1s ease}
.iwd{display:none}
.cvi .cv0{clip-path:var(--ic,inset(21% 39% 21% 39%))}.cvi.open .cv0{clip-path:inset(0 0 0 0);transition:clip-path 1.15s cubic-bezier(.76,0,.2,1)}
html.cviing,html.cviing body{background:#0e0e0d;overflow:hidden}
.cvi .cvh,.cvi .cvm,.cvi .cvf,.cvi .cvo,.cvi header.top{opacity:0}
.cvh,.cvm,.cvf,.cvo,.coverpg header.top{transition:opacity .9s ease,transform .9s cubic-bezier(.2,.7,.2,1)}
.cvi .cvh h1{transform:translateY(40px)}.cvi .cvm{transform:translateY(24px)}
.cvi .iwd{display:flex;position:fixed;left:0;right:0;top:50%;z-index:60;justify-content:space-between;padding:0 2.6vw;margin-top:-.6em;font:600 13px/1 Pretendard,sans-serif;letter-spacing:-.01em;text-transform:uppercase;color:#efede6;mix-blend-mode:difference;pointer-events:none}
.cvi .iwd span{opacity:0;transition:opacity .5s}.cvi.w1 .iwd span:nth-child(1),.cvi.w2 .iwd span:nth-child(-n+2),.cvi.w3 .iwd span{opacity:1}
.cvi.open .iwd{opacity:0;transition:opacity .4s}
/* 표지 영상 위 분석 태그 + 선 스크린 */
.cv0 .cvo{pointer-events:none;background:radial-gradient(120% 80% at 20% 85%,#0d0c0bd9 0%,#0d0c0b00 45%),radial-gradient(60% 70% at 85% 80%,#0d0c0bcc 0%,#0d0c0b00 60%)!important}
.ctg{position:absolute;inset:0;z-index:0;pointer-events:none}
.ctg .tg{position:absolute;transform:translate(-6px,-6px);font:11px/1.35 'JetBrains Mono',ui-monospace,monospace;color:#efede6;letter-spacing:.04em;opacity:0;transition:opacity .35s}
.ctg .tg.on{opacity:1}
.ctg .tg i{position:absolute;left:0;top:0;width:12px;height:12px;border:1px solid #ff6b4a}.ctg .tg i:after{content:'';position:absolute;left:5px;top:5px;width:2px;height:2px;background:#ff6b4a}
.ctg .tg u{position:absolute;left:12px;top:6px;height:1px;width:0;background:#ff6b4a;transition:width .5s .1s;text-decoration:none}.ctg .tg.on u{width:48px}
.ctg .tg b{position:absolute;left:60px;top:-4px;white-space:nowrap;background:#ff6b4a;color:#120f0d;font-weight:600;padding:3px 7px;text-transform:uppercase}
.ctg .tg small{position:absolute;left:60px;top:18px;white-space:nowrap;font-size:10.5px;color:#d8d4ca;background:#0d0c0bb0;padding:2px 7px}
@media (max-width:860px){.ctg .tg{display:none}}
/* About: 명함 */
.cardpg{--bg:#1c1b19;--fg:#ece9e1;--mute:#8d887e;--line:#34322e;--paper:#a04d35;--ink:#f8eee5;--pm:#ecc2ae;--sub:#f3d9cb;--rule:#bd6c52;--mkf:#a04d35;--mka:#ffd9c4;--mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.cardpg header.top{background:var(--paper);backdrop-filter:none;color:var(--ink)}.cardpg header.top nav a{color:var(--pm)}.cardpg header.top nav a.on,.cardpg header.top nav a:hover{color:var(--ink)}.cardpg header.top .name span{color:var(--pm)}
.cardpg main{padding:0}
.cm{position:absolute;inset:14px;pointer-events:none;--c:var(--pm);background:linear-gradient(var(--c),var(--c)) 0 0/14px 1px,linear-gradient(var(--c),var(--c)) 0 0/1px 14px,linear-gradient(var(--c),var(--c)) 100% 0/14px 1px,linear-gradient(var(--c),var(--c)) 100% 0/1px 14px,linear-gradient(var(--c),var(--c)) 0 100%/14px 1px,linear-gradient(var(--c),var(--c)) 0 100%/1px 14px,linear-gradient(var(--c),var(--c)) 100% 100%/14px 1px,linear-gradient(var(--c),var(--c)) 100% 100%/1px 14px;background-repeat:no-repeat;opacity:.7}
.bc{min-height:calc(100svh - 64px);background:var(--paper);display:flex}
.bcs{position:relative;flex:1;color:var(--ink);padding:clamp(40px,5vw,72px) clamp(28px,6vw,96px) clamp(56px,6vw,88px);display:grid;grid-template-columns:4fr 4.4fr 3.6fr;grid-template-rows:auto auto 1fr;column-gap:clamp(32px,5vw,88px)}
.bcs .t1{grid-column:1/-1;font:12px var(--mono);letter-spacing:.22em;text-transform:uppercase;color:var(--pm);display:flex;gap:28px;flex-wrap:wrap}.bcs .t1 span{letter-spacing:.08em;text-transform:none;font-size:13px;color:var(--sub)}
.bcs .seal{position:absolute;right:clamp(28px,6vw,96px);top:clamp(30px,4vw,58px);color:var(--ink);font-style:normal}.bcs .seal .kh{width:clamp(150px,14vw,220px);height:auto;display:block}
.bcs>.cl{position:absolute;inset:0;width:100%;height:100%;color:var(--ink);opacity:.035;pointer-events:none}.bcs>*{position:relative}.bcs>.seal,.bcs>.sz{position:absolute}
.bcs h1{grid-column:1/-1;font-size:clamp(64px,8.4vw,140px);font-weight:600;letter-spacing:-.05em;line-height:.95;margin:clamp(28px,4vh,48px) 0 20px;display:flex;align-items:baseline;gap:.35em;flex-wrap:wrap}
.bcs h1 span{font-size:.24em;font-weight:400;letter-spacing:-.01em;color:var(--pm)}
.bcs .c1{display:flex;flex-direction:column;justify-content:space-between;gap:36px}
.bcs .lead{font-size:clamp(17px,1.35vw,20px);line-height:1.75;color:var(--ink);letter-spacing:-.01em}
.bcs .ct{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:6px 28px;font:15px var(--mono);margin:-12px 0 clamp(36px,6vh,60px);padding-top:12px;border-top:1.5px solid var(--ink)}.bcs .ct div{display:flex;gap:10px}.bcs .ct dt{color:var(--pm)}.bcs .ct dt{color:var(--pm)}.bcs .ct a{color:inherit;text-decoration:none;border-bottom:1px solid var(--rule)}
.bcs .c3,.bcs .c1s{display:flex;flex-direction:column;gap:30px}.bcs .c1{justify-content:flex-start}
.bcs h3{display:flex;gap:10px;align-items:baseline;font:12px var(--mono);letter-spacing:.2em;text-transform:uppercase;color:var(--ink);font-weight:500;padding-bottom:10px;margin-bottom:6px;border-bottom:1.5px solid var(--ink)}
.bcs h3 b{color:var(--pm);font-weight:500;letter-spacing:.05em}
.bcs .it{padding:9px 0;border-bottom:1px solid var(--rule);display:flex;flex-direction:column;gap:1px}.bcs section .it:last-child{border-bottom:0}
.bcs .it span{font:12.5px var(--mono);color:var(--pm);letter-spacing:.02em}
.bcs .it strong{font-size:17px;font-weight:600;letter-spacing:-.01em;line-height:1.4}
.bcs .it em{font-style:normal;font-size:14px;color:var(--sub);line-height:1.5}
.bcs .sz{position:absolute;right:clamp(28px,6vw,96px);bottom:26px;font:10px var(--mono);letter-spacing:.12em;color:var(--pm)}
.flyin .bcs>*{animation:bcin .7s .05s both}@keyframes bcin{from{opacity:0;transform:translateY(10px)}}
.bg.prjg{background:radial-gradient(80% 60% at 36% 30%,#1c1d1b 0%,#121311 70%);filter:none}
.fdg{position:absolute;left:36%;top:8%;transform:translateX(-50%);display:grid;grid-template-columns:repeat(3,min(15vw,190px));gap:28px 44px}
.fd{position:relative;display:block;aspect-ratio:4/3;pointer-events:none;opacity:0;transform:translateY(14px);transition:opacity .35s,transform .5s cubic-bezier(.2,.8,.2,1);transition-delay:calc(var(--i) * 70ms)}
.prjg.on .fd{opacity:1;transform:none}
.fd svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.fd .fb0 path{fill:#161715;stroke:#ece8de;stroke-width:1.1;stroke-linejoin:round}
.fd .ff0 path{fill:#1b1c1a;fill-opacity:.8;stroke:#ece8de;stroke-width:1.1;stroke-linejoin:round}.fd .ff0 .ln{fill:none;stroke-opacity:.35}
.fd .ff0{transform-origin:50% 100%;transform:perspective(400px) rotateX(0);transition:transform .5s cubic-bezier(.2,.8,.2,1);transition-delay:calc(var(--i) * 70ms + .25s)}
.prjg.on .fd .ff0{transform:perspective(400px) rotateX(-14deg)}
.fd img{position:absolute;left:12%;width:76%;top:30%;height:52%;object-fit:cover;border:3px solid #ece8de;box-shadow:0 6px 14px #0008;transform:translateY(16%) rotate(-2deg);transition:transform .6s cubic-bezier(.2,1.3,.4,1);transition-delay:calc(var(--i) * 70ms + .3s)}
.fd:nth-child(even) img{transform:translateY(16%) rotate(2deg)}
.prjg.on .fd img{transform:translateY(-38%) rotate(-3deg)}.prjg.on .fd:nth-child(even) img{transform:translateY(-38%) rotate(3deg)}
.fd .fn{position:absolute;left:0;right:0;top:calc(100% + 8px);font:11px 'JetBrains Mono',ui-monospace,monospace;letter-spacing:.08em;color:#cfc9bc;text-align:center;white-space:nowrap}
@media (max-width:860px){.fdg{left:50%;grid-template-columns:repeat(3,26vw);gap:20px 14px}}
.bg.pubg{background:radial-gradient(80% 60% at 36% 30%,#26231f 0%,#121110 70%);filter:none;overflow:hidden}
.shf{position:absolute;left:36%;top:6%;height:min(40vh,360px);transform:translateX(-50%);display:flex;align-items:flex-end;gap:1px;padding:0 18px}
.shf::after{content:'';position:absolute;left:-10px;right:-10px;bottom:-14px;height:14px;background:linear-gradient(#3a342c,#1d1a16);box-shadow:0 18px 40px #000c}
.shf::before{content:'';position:absolute;left:-10px;right:-10px;top:-20px;bottom:-14px;border:1px solid #ffffff10;border-bottom:0;pointer-events:none}
.sp{position:relative;flex:none;display:flex;align-items:center;justify-content:center;box-shadow:inset 2px 0 0 #ffffff14,inset -2px 0 0 #00000040;transform-origin:50% 100%}
.sp b{writing-mode:vertical-rl;font:600 9px/1 Inter,system-ui,sans-serif;letter-spacing:.18em;white-space:nowrap;overflow:hidden;max-height:86%}.sp b.ko{text-orientation:upright;letter-spacing:.08em}
.pubg.shk .shf{animation:shk .34s cubic-bezier(.3,0,.3,1)}
@keyframes shk{0%{transform:translateX(-50%)}25%{transform:translateX(-50%) translateY(4px)}55%{transform:translateX(-50%) translateY(-1px)}100%{transform:translateX(-50%)}}
.pubg.shk .sp:not(.f1):not(.f2){animation:wob .4s ease-out}
@keyframes wob{35%{transform:rotate(-1deg)}100%{transform:none}}
.shf{perspective:700px}
.shf{perspective:900px;transform-style:preserve-3d}
.sp.f1,.sp.f2{transform-style:preserve-3d}
.sp .cvr,.sp .pgs{position:absolute;top:0;left:100%;height:100%;width:calc(var(--bh) * .705);transform-origin:0 50%;transform:rotateY(90deg);background:#1d1c1a center/cover no-repeat;box-shadow:inset 0 0 0 1px #0006}
.sp .pgs{left:0;transform:rotateY(90deg) translateZ(0);transform-origin:0 50%;background:repeating-linear-gradient(90deg,#e9e3d6 0 2px,#cfc8b9 2px 3px)}
.pubg.drop .sp.f1{animation:bkf 1.05s cubic-bezier(.4,0,.75,.45) forwards}
.pubg.drop .sp.f2{animation:bkf2 1.05s cubic-bezier(.4,0,.75,.45) .16s forwards}
@keyframes bkf{0%{transform:none}28%{transform:translate3d(0,-2%,90px)}100%{transform:translate3d(-60px,135%,220px) rotateY(-78deg) rotateZ(-28deg)}}
@keyframes bkf2{0%{transform:none}28%{transform:translate3d(0,-2%,90px)}100%{transform:translate3d(50px,140%,200px) rotateY(-70deg) rotateZ(22deg)}}
.flr{position:absolute;left:0;right:0;top:58%;bottom:0;perspective:1100px;perspective-origin:45% 10%;border-top:1px solid #ffffff12;background:linear-gradient(#ffffff06,transparent 60%)}
.fb{position:absolute;top:0;height:min(28vh,250px);aspect-ratio:.705;background:#1d1c1a center/cover no-repeat;box-shadow:1px 1px 0 #cfc9bd,2px 2px 0 #9c968a,3px 3px 0 #cfc9bd,4px 4px 0 #8a8478,14px 22px 30px #000d;opacity:0;transform-origin:50% 100%}
.fb.b1{left:37%;transform:rotateX(66deg) translateY(-420px) translateZ(220px) rotateZ(-50deg)}
.fb.b2{left:48.5%;transform:rotateX(66deg) translateY(-420px) translateZ(220px) rotateZ(40deg)}
.pubg.land .fb{opacity:1;transition:transform .32s cubic-bezier(.5,0,.75,0),opacity .08s}
.pubg.land .fb.b1{transform:rotateX(66deg) rotateZ(-9deg)}
.pubg.land .fb.b2{transform:rotateX(66deg) translate(10px,30px) rotateZ(14deg);transition-delay:.09s}
.pubg.thud .flr{animation:thd .3s ease-out}@keyframes thd{30%{transform:translateY(4px)}100%{transform:none}}
@media (max-width:860px){.shf{left:50%}.fb.b1{left:14%}.fb.b2{left:50%}}
.ptop{position:absolute;inset:0;opacity:0;transform:scale(1.22);transition:opacity .9s ease,transform 2.6s cubic-bezier(.2,.6,.2,1);background:repeating-linear-gradient(90deg,#1a1815 0 118px,#14120f 118px 120px),#171512;pointer-events:none}
.ptop::before{content:'';position:absolute;inset:0;background:radial-gradient(60% 60% at 40% 42%,#00000000 0%,#000000aa 100%)}
.pubg.top .ptop{opacity:1;transform:none}
.tb{opacity:0}.pubg.top .tb{animation:tland 1.1s cubic-bezier(.25,.9,.35,1) .15s both}.pubg.top .tb.t2{animation-delay:.35s}
@keyframes tland{0%{opacity:0;transform:translateY(-10px) scale(1.08) rotate(var(--r));box-shadow:40px 60px 60px #0008}30%{opacity:1}100%{opacity:1;transform:rotate(var(--r))}}.pubg.top .shf,.pubg.top .flr{opacity:0;transition:opacity .8s}
.tb{position:absolute;height:min(46vh,420px);aspect-ratio:.705;background:#1d1c1a center/cover no-repeat;box-shadow:2px 2px 0 #d8d2c6,4px 4px 0 #a39d90,6px 6px 0 #d8d2c6,8px 8px 0 #8a8478,26px 34px 40px #000c}
.tb.t1{left:22%;top:12%;--r:-13deg;transform:rotate(-13deg)}.tb.t2{left:38%;top:20%;--r:17deg;transform:rotate(17deg)}
.tcap{position:absolute;left:22%;top:5%;margin:0;font:11px 'JetBrains Mono',ui-monospace,monospace;letter-spacing:.08em;color:#cfc6b6;opacity:.7}
@media (max-width:860px){.tb.t1{left:6%}.tb.t2{left:36%}.tcap{left:8%}}
.bg.prag{background:radial-gradient(80% 60% at 36% 30%,#1c1d1b 0%,#121311 70%);filter:none}
.prag .scn{position:absolute;inset:0;will-change:transform}
.prag .rope{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}
.prag .rope path{fill:none;stroke:#ece8de;stroke-linecap:round}.prag .rope .r1{stroke-width:2.2;opacity:.85}.prag .rope .r2{stroke:#121311;stroke-width:1.2;stroke-dasharray:2 5}
.prag .cam{position:absolute;z-index:4;left:6%;top:30%;width:min(19vw,260px);transform-origin:50% 80%}
.prag .cam svg{width:100%;height:auto;display:block}
.pol{position:absolute;margin:0;padding:7px 7px 0;background:#f2eee6;box-shadow:0 10px 18px #0009;opacity:0;transform-origin:50% 0;border:1px solid #2a2926}
.pol.out,.pol.hung{opacity:1}
.pol img{display:block;width:100%;aspect-ratio:1/1;object-fit:cover;filter:grayscale(.15) contrast(1.02);border:1px solid #2a2926}
.pol figcaption{font:400 15px/1.2 'Nanum Pen Script',cursive;color:#2a2926;text-align:center;padding:5px 2px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pol:not(.hung) .pin{opacity:0}.pol .pin{transition:opacity .25s;position:absolute;left:50%;top:-22px;width:13px;height:30px;margin-left:-6px;z-index:2}
.pol.hung{animation:sw 2.6s ease-in-out infinite;animation-delay:calc(var(--d) * .3s)}
@keyframes sw{0%,100%{transform:rotate(calc(var(--d) * 2.5deg))}50%{transform:rotate(calc(var(--d) * -1.5deg))}}
@media (max-width:860px){.prag .cam{left:50%;top:44%;width:44vw;margin-left:-22vw}}
.bg .pdr{position:absolute;inset:0;pointer-events:none}
.bst{position:fixed;inset:0;z-index:120;display:grid;place-items:end center;padding-bottom:62px;pointer-events:none;perspective:1600px;perspective-origin:50% 30%}
.bst::before{content:'';position:absolute;inset:0;background:#141412;opacity:0;transition:opacity .4s}.bst::before{background:linear-gradient(to top,#141412 0%,#14141200 70%)}.bst.up::before{opacity:.7}
.bsk{position:relative;width:min(520px,80vw);aspect-ratio:9/5;transform-style:preserve-3d;transform-origin:50% 100%;transform:translateY(140%) rotateX(52deg);transition:transform .62s cubic-bezier(.18,1.3,.4,1)}
.bst.up .bsk{transform:translateY(0) rotateX(52deg);pointer-events:auto;cursor:pointer}
.bst.flat .bsk{transform:translateY(0) rotateX(0) rotateZ(0);transition:transform .36s cubic-bezier(.5,0,.2,1)}
.bsk .ly{position:absolute;inset:0;background:#ebe7de;transform:translateZ(calc(var(--z) * -3.4px));box-shadow:inset 0 0 0 1px #d4cec2;transition:transform .3s,opacity .3s}
.bsk .ly:nth-child(odd){background:#e4e0d6}.bsk .ly:first-child{box-shadow:inset 0 0 0 1px #c9c3b6,0 40px 70px #000b}
.bst.flat .ly{opacity:0;transform:translateZ(-60px)}
.bpk{position:absolute;inset:0;background:#f1efe8;color:#1d1c1a;display:grid;cursor:pointer;transform:translateZ(0);transition:transform .24s cubic-bezier(.2,.8,.2,1),box-shadow .24s;box-shadow:inset 0 0 0 1px #d4cec2}
.bst.lift .bpk{transform:translateZ(70px);box-shadow:0 30px 50px #0006}.bst.flat .bpk{transform:translateZ(0)}
.bpk{overflow:hidden;padding:20px 24px 18px;background:#a04d35;color:#f6ebe1;grid-template-rows:auto auto 1fr auto auto;justify-items:center;text-align:center;font-family:Inter,system-ui,sans-serif;text-transform:uppercase;letter-spacing:.24em;box-shadow:inset 0 0 0 1px #8b412b}
.bpk .k1{font-size:13px;font-weight:600;letter-spacing:.22em}.bpk .k1 span{color:#f0cdbb;font-weight:500;margin-left:.6em}
.bpk .k2{font-size:9.5px;font-weight:500;color:#f0cdbb;margin-top:5px}
.bpk .km{align-self:center;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px;width:100%}.bpk .km span{font-size:10px;font-weight:600;writing-mode:vertical-rl;transform:rotate(180deg);color:#f0cdbb}
.bpk .kh{width:100%;height:auto}
.bpk .k5{font-size:11.5px;font-weight:600;letter-spacing:.2em}.bpk .k6{font-size:9px;color:#f0cdbb;margin-top:4px;letter-spacing:.18em}
.bsk .ly{background:#97462f!important;box-shadow:inset 0 0 0 1px #7e3a26!important}.bsk .ly:nth-child(odd){background:#8d412b!important}.bsk .ly:first-child{box-shadow:inset 0 0 0 1px #6e3120,0 40px 70px #000b!important}
.cv0 .cad,.cv0 .bgs{transition:opacity .5s,filter .5s}.cv0.pk .cad{opacity:.25}.cv0.pk .cvh{opacity:.25;transition:opacity .5s}
.bfly{position:fixed;z-index:130;overflow:hidden;background:#a04d35;transition:all .65s cubic-bezier(.7,0,.2,1);box-shadow:0 30px 80px #000a}
@media (max-width:1100px){.bcs{grid-template-columns:1fr 1fr}.bcs .c1{grid-column:1/-1;margin-bottom:48px}}
@media (max-width:700px){.bcs{grid-template-columns:1fr;padding:44px 22px 64px;row-gap:44px}.bcs h1{margin:24px 0 0}.bcs .seal .kh{width:120px}.bcs .c1{margin:0}}
.acard .lio{display:none}
.acard .dmo{margin-left:auto;background:none;border:0;padding:0;font:11px var(--mono);color:var(--mute);cursor:pointer;display:flex;align-items:center;gap:6px}.acard .dmo:hover{color:#e6e3da}
.acard .dmo i{font-style:normal}.acard[data-mode=auto] .dmo i{width:6px;height:6px;border-radius:50%;background:#e0a15a;animation:dmo 1.4s ease-in-out infinite}
@keyframes dmo{50%{opacity:.25}}.acard header .dmo+a{margin-left:14px}.acard[data-mode=auto] .app{cursor:pointer}
.acard.live .lctl{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:0 22px;margin:0 0 10px;padding:10px 0 0;border-top:1px solid #2c2e2a}
.acard.live .lctl fieldset{margin:0 0 6px}.acard.live .lctl label{font-size:12px;grid-template-columns:96px 1fr 44px}.acard.live .lio{display:flex}

@media (max-width:900px){.app .lio{grid-column:1}}
"""


# ---- 명함 마크: 필지 → 대지안의 공지(점선) → 한 층씩 쌓인 매스 (표지 지적도와 같은 언어)
import random as _rnd
def _pts(ps): return ' '.join(f'{x:.1f},{y:.1f}' for x, y in ps)
def card_mark(size=64):
    P=[(6,16),(52,9),(58,50),(9,56)]; S=[(14,22),(45,17),(50,44),(17,48)]
    out=[f'<polygon points="{_pts(P)}" fill="none" stroke="currentColor" stroke-width="1.6"/>',
         f'<polygon points="{_pts(S)}" fill="none" style="stroke:var(--mka,#c8462e)" stroke-width="1" stroke-dasharray="2.5 2"/>']
    base=[(19,34),(41,31),(43,43),(21,46)]
    for i in range(4):
        dy=-i*5.2; q=[(x,y+dy) for x,y in base]
        if i: out.append(''.join(f'<line x1="{x:.1f}" y1="{y+5.2:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="currentColor" stroke-width=".8"/>' for x,y in q))
        out.append(f'<polygon points="{_pts(q)}" style="fill:var(--mkf,#f1efe8);stroke:{"var(--mka,#c8462e)" if i==3 else "currentColor"}" stroke-width="{1.4 if i==3 else 1}"/>')
    return f'<svg class="mk" viewBox="0 0 64 64" width="{size}" height="{size}" aria-hidden="true">{"".join(out)}</svg>'
def card_lines(seed=7, w=900, h=500):
    R=_rnd.Random(seed); L=[]
    for j in range(7):
        y=j*h/6+R.uniform(-25,25); L.append(f'M-20 {y:.0f} L{w+20} {y+R.uniform(-60,60):.0f}')
    for i in range(10):
        x=i*w/9+R.uniform(-30,30); L.append(f'M{x:.0f} -20 L{x+R.uniform(-80,80):.0f} {h+20}')
    return f'<svg class="cl" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><path d="{" ".join(L)}" fill="none" stroke="currentColor" stroke-width="1"/></svg>'

def card_holes():
    H=[[(50,14),(96,8),(100,54),(54,60)],[(128,10),(174,14),(170,58),(124,54)],[(202,8),(250,12),(246,60),(206,56)]]
    o=[]
    for q in H:
        o.append(f'<polygon points="{_pts(q)}" fill="#3b170e"/>')
        o.append(f'<polyline points="{_pts([q[0],q[1],q[2]])}" fill="none" stroke="#260d07" stroke-width="5" opacity=".7"/>')
        o.append(f'<polyline points="{_pts([q[2],q[3],q[0]])}" fill="none" stroke="#c97a5e" stroke-width="1.2"/>')
    return f'<svg class="kh" viewBox="0 0 300 68" aria-hidden="true">{"".join(o)}</svg>'
HOLES=card_holes()
MARK=card_mark(); LINES=card_lines()

JS = r"""
// 어디서든 About: 올리면 쌓인 명함 더미가 화면 가운데로 탁 올라오고, 누르면 맨 윗장이 떠올라 화면 가득 펼쳐진 뒤 이동
(function(){var rm=matchMedia('(prefers-reduced-motion:reduce)').matches,S=null,busy=false;
function el(){if(S)return S;var n=document.querySelector('header.top .name'),nm=n?n.innerHTML.replace(/^←\s*/,''):'',ly='';for(var i=34;i>=1;i--)ly+='<i class="ly" style="--z:'+i+'"></i>';
 S=document.createElement('div');S.className='bst';S.setAttribute('aria-hidden','true');
 S.innerHTML='<div class="bsk">'+ly+'<div class="bpk"><p class="k1">'+nm+'</p><p class="k2">Architectural Designer</p><div class="km"><span>S · H</span>__HOLES__<span>2 0 2 6</span></div><p class="k5">__EMAIL__</p><p class="k6">__PHONE__ · coin9563-max.github.io</p></div></div>';
 document.body.appendChild(S);return S;}
function go(e,href){if(e&&(e.metaKey||e.ctrlKey||e.shiftKey||e.button>0))return;if(rm||document.body.classList.contains('cardpg'))return;e&&e.preventDefault();if(busy)return;busy=true;
 var s=el(),up=s.classList.contains('up');if(!up){s.classList.add('up');void s.offsetWidth;}
 setTimeout(function(){s.classList.add('lift');
  setTimeout(function(){s.classList.add('flat');
   setTimeout(function(){var c=s.querySelector('.bpk'),r=c.getBoundingClientRect(),d=document.createElement('div');d.className='bfly';
    d.style.cssText='left:'+r.left+'px;top:'+r.top+'px;width:'+r.width+'px;height:'+r.height+'px';var cc=c.cloneNode(true);cc.style.cssText='position:absolute;inset:0;transform:none;box-shadow:none;transition:opacity .3s';d.appendChild(cc);document.body.appendChild(d);c.style.visibility='hidden';setTimeout(function(){cc.style.opacity=0;},120);
    requestAnimationFrame(function(){requestAnimationFrame(function(){d.style.cssText='left:0;top:0;width:100vw;height:100vh;box-shadow:none';});});
    try{sessionStorage.setItem('bcfly','1');}catch(x){}setTimeout(function(){location.href=href;},600);},360);},240);},up?0:560);}
window.BCard={el:el,go:go};
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href$="about.html"]');if(!a||a.target==='_blank')return;go(e,a.href);});
if(!document.body.classList.contains('cardpg')&&matchMedia('(hover:hover)').matches){var t,last=null,cv=function(){return document.querySelector('.cv0');};
 function on(a){clearTimeout(t);if(a)last=a;var s=el();s.classList.add('up');var v=cv();v&&v.classList.add('pk');}
 function off(){t=setTimeout(function(){if(busy)return;el().classList.remove('up');var v=cv();v&&v.classList.remove('pk');},160);}
 document.addEventListener('mouseover',function(e){var a=e.target.closest&&e.target.closest('a[href$="about.html"]');if(a)on(a);else if(e.target.closest&&e.target.closest('.bsk'))on(null);});
 document.addEventListener('mouseout',function(e){var a=e.target.closest&&(e.target.closest('a[href$="about.html"]')||e.target.closest('.bsk'));if(a&&!(e.relatedTarget&&a.contains(e.relatedTarget)))off();});
 document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('.bsk')&&last)go(e,last.href);});}
})();


// 표지 Publish 호버: 책장이 쿵 울리고 책 두 권이 떨어져 바닥에 놓임
(function(){var bg=document.querySelector('.cv0 .pubg');if(!bg)return;var PJ=JSON.parse(bg.dataset.p||'[]'),built=false,tm=[],rm=matchMedia('(prefers-reduced-motion:reduce)').matches;
function rnd(n){var x=Math.sin(n*91.3+7.1)*43758.5;return x-Math.floor(x);}
function build(){if(built)return;built=true;var C=['#2a2724','#3b3632','#d8d0c2','#1f1e1c','#5a4b3c','#8d7e69','#c9bfae','#44403a'],ord=[],h='';
 ['','',''].concat(PJ).concat(['','','','']).forEach(function(t){ord.push({t:t});});ord.splice(4,0,{t:'FROM CITY TO EARTH',f:1});ord.splice(8,0,{t:'UNWASHED',f:2});
 ord.forEach(function(o,i){var w=o.f==1?30:o.f==2?26:Math.round(16+rnd(i)*26),ht=o.f?96:Math.round(78+rnd(i+40)*20),cl=o.f==1?'#161514':o.f==2?'#1b1a17':C[Math.floor(rnd(i+9)*C.length)],tc=o.f==1?'#f2efe8':o.f==2?'#e9c43b':(parseInt(cl.slice(1,3),16)>150?'#3a352f':'#cfc6b6');
  h+='<div class="sp'+(o.f?' f'+o.f:'')+'" style="--bh:'+(ht/100*Math.min(innerHeight*.4,360))+'px;width:'+w+'px;height:'+ht+'%;background:'+cl+';color:'+tc+'"><b'+(/[가-힣]/.test(o.t)?' class="ko"':'')+'>'+(o.t||'')+'</b>'+(o.f?'<i class="cvr" style="background-image:url('+(o.f==1?bg.dataset.a:bg.dataset.b)+')"></i><i class="pgs"></i>':'')+'</div>';});
 bg.innerHTML='<div class="shf">'+h+'</div><div class="flr"><div class="fb b1" style="background-image:url('+bg.dataset.a+')"></div><div class="fb b2" style="background-image:url('+bg.dataset.b+')"></div></div><div class="ptop"><div class="tb t1" style="background-image:url('+bg.dataset.a+')"></div><div class="tb t2" style="background-image:url('+bg.dataset.b+')"></div><p class="tcap">FROM CITY TO EARTH · UNWASHED — 졸업전시 책자 2026</p></div>';}
function at(ms,fn){tm.push(setTimeout(fn,ms));}
function run(){tm.forEach(clearTimeout);tm=[];bg.classList.remove('shk','drop','land','thud','top');if(rm){bg.classList.add('drop','land','top');return;}
 void bg.offsetWidth;at(350,function(){bg.classList.add('shk');});at(620,function(){bg.classList.add('drop');});at(2000,function(){bg.classList.add('top');});}
var wason=false;new MutationObserver(function(){var on=bg.classList.contains('on');if(on===wason)return;wason=on;if(on){build();run();}}).observe(bg,{attributes:true,attributeFilter:['class']});
})();
// 표지 Practice 호버: 크게 잡힌 즉석카메라에서 D'EAU 사진이 천천히 나옴 → 바람에 날리듯 오른쪽 빨랫줄로 → 줌아웃, 전체 사진
(function(){var bg=document.querySelector('.cv0 .prag');if(!bg)return;var PH=JSON.parse(bg.dataset.p),built=false,tm=[],anims=[],scn,cam,ps=[],hero,rm=matchMedia('(prefers-reduced-motion:reduce)').matches;
function at(ms,fn){tm.push(setTimeout(fn,ms));}
function build(){if(built)return;built=true;var h='<div class="scn"><svg class="rope" aria-hidden="true"><path class="r1"/><path class="r2"/></svg><div class="cam">'+bg.dataset.cam+'</div>';
 PH.forEach(function(p,i){h+='<figure class="pol" style="--d:'+(i%2?1:-1)+'">'+bg.dataset.pin+'<img src="'+p[0]+'" alt="" loading="eager"><figcaption>'+p[1]+'</figcaption></figure>';});
 bg.innerHTML=h+'</div>';scn=bg.querySelector('.scn');cam=bg.querySelector('.cam');ps=[].slice.call(bg.querySelectorAll('.pol'));hero=ps[ps.length-1];}
function lay(){var R=bg.getBoundingClientRect(),W=R.width,H=R.height,narrow=W<860,x0=W*(narrow?.04:.05),x1=W*(narrow?.96:.64),y0=H*.1,y1=H*.085,cx=(x0+x1)/2,cy=H*.2,n=PH.length;
 var d='M'+x0+','+y0+' Q'+cx+','+cy+' '+x1+','+y1;bg.querySelector('.r1').setAttribute('d',d);bg.querySelector('.r2').setAttribute('d',d);
 var pw=Math.min(132,(x1-x0)/n*.92);ps.forEach(function(p,i){var t=(i+.5)/n,x=(1-t)*(1-t)*x0+2*(1-t)*t*cx+t*t*x1,y=(1-t)*(1-t)*y0+2*(1-t)*t*cy+t*t*y1;p.style.width=pw+'px';p.style.left=(x-pw/2)+'px';p.style.top=(y-6)+'px';p.dataset.x=x;p.dataset.y=y;});return {W:W,H:H};}
function stop(){tm.forEach(clearTimeout);tm=[];anims.forEach(function(a){a.cancel();});anims=[];}
function run(){stop();var S=lay();ps.forEach(function(p){p.classList.add('hung');p.style.clipPath='';p.style.opacity='';p.style.transition='';p.style.zIndex='';p.style.transformOrigin='';});bg.querySelector('.rope').style.opacity='';
 scn.style.transition='none';scn.style.transform='';
 if(rm){cam.style.opacity=0;return;}
 // 슬롯 위치(장면 좌표): 카메라 svg의 data-sx/sy(슬롯), data-ex/ey(배출 방향)
 var sv=cam.querySelector('svg'),cw=cam.offsetWidth,ch=cam.offsetHeight,sx=cam.offsetLeft+cw*(+sv.dataset.sx),sy=cam.offsetTop+ch*(+sv.dataset.sy),Z=S.W<860?1.5:1.6;
 var ex=+sv.dataset.ex,ey=+sv.dataset.ey,el=Math.hypot(ex,ey);ex/=el;ey/=el;var D=sv.dataset,ax=cam.offsetLeft+cw*(+D.ax),ay=cam.offsetTop+ch*(+D.ay),bx=cam.offsetLeft+cw*(+D.bx),by=cam.offsetTop+ch*(+D.by);
 scn.style.transformOrigin=sx+'px '+sy+'px';scn.style.transform='translate('+(S.W*.36-sx)+'px,'+(S.H*.5-sy)+'px) scale('+Z+')';
 cam.style.transition='none';cam.style.opacity='';
 var hx=+hero.dataset.x,hy=+hero.dataset.y,w=hero.offsetWidth,h=hero.offsetHeight,L0=hx-w/2,T0=hy-6;
 // 사진을 눕혀서(받침 평면 위) 슬롯 밖으로: 가로축 = 슬롯 방향, 세로축 = 배출 방향 → CSS matrix
 var abx=bx-ax,aby=by-ay,abl=Math.hypot(abx,aby),unx=abx/abl,uny=aby/abl,Wp=118*abl/166,k=Wp/w,Ux=unx*k,Uy=uny*k,Vx=ex*k*.825,Vy=ey*k*.825,lx=(ax+bx)/2-unx*Wp/2,ly=(ay+by)/2-uny*Wp/2;
 function pose(sd){var ox=lx-Vx*(h-sd),oy=ly-Vy*(h-sd);return {m:'matrix('+[Ux,Uy,Vx,Vy,ox-L0,oy-T0].map(function(v){return v.toFixed(4);}).join(',')+')',clip:'inset('+(h-sd).toFixed(1)+'px 0 0 0)'};}
 var A=pose(0),B=pose(h*.86),M=B.m;
 hero.classList.remove('hung');hero.style.opacity=1;hero.style.zIndex=6;hero.style.transformOrigin='0 0';ps.forEach(function(p){if(p!==hero){p.style.transition='none';p.style.opacity=0;}});bg.querySelector('.rope').style.opacity=0;
 // 1) 받침 위로 천천히 밀려 나옴
 var e=hero.animate([{transform:A.m,clipPath:A.clip},{transform:B.m,clipPath:B.clip}],{duration:2300,delay:350,easing:'cubic-bezier(.35,.1,.45,1)',fill:'both'});anims.push(e);
 // 2) 바람에 날리듯 오른쪽 위로 → 줄에 걸림
 at(2900,function(){var f=hero.animate([
   {transform:M,clipPath:B.clip},
   {transform:'translate('+((lx-L0)*.7)+'px,'+((ly-T0)*.55-70)+'px) rotate(-14deg)',clipPath:'inset(0px 0 0 0)',offset:.3},
   {transform:'translate('+((lx-L0)*.3)+'px,'+((ly-T0)*.2-50)+'px) rotate(12deg)',offset:.6},
   {transform:'translate(-14px,-26px) rotate(-7deg)',offset:.85},
   {transform:'translate(0,0) rotate(0)',clipPath:'inset(0px 0 0 0)'}],{duration:1500,easing:'cubic-bezier(.35,.05,.3,1)',fill:'forwards'});anims.push(f);
  e.cancel();f.onfinish=function(){f.cancel();hero.style.transformOrigin='';hero.classList.add('hung');};cam.style.transition='opacity 1s .2s';cam.style.opacity=0;
  // 3) 줌아웃
  scn.style.transition='transform 1.7s cubic-bezier(.45,.05,.25,1)';scn.style.transform='';var rp=bg.querySelector('.rope');rp.style.transition='opacity .8s .3s';rp.style.opacity='';ps.forEach(function(p,i){if(p!==hero){p.style.transition='opacity .6s '+(.45+i*.12)+'s';p.style.opacity='';}});});}
var wason=false;new MutationObserver(function(){var on=bg.classList.contains('on');if(on===wason)return;wason=on;if(on){build();run();}else stop();}).observe(bg,{attributes:true,attributeFilter:['class']});
addEventListener('resize',function(){if(built&&wason)lay();});})();
// 표지 Process 호버: 배경 그리드 위에 실험 도면(투라인 + 해치)이 칸에 맞춰 틱 단위로 생성됨
(function(){var cv0=document.querySelector('.cv0');if(!cv0)return;var lk=document.querySelector('.cvm a[href$="process.html"]');if(!lk)return;
var bgs=cv0.querySelectorAll('.bg'),bi=[].indexOf.call(document.querySelectorAll('.cvm a'),lk),bg=bgs[bi];if(!bg)return;
var c=document.createElement('canvas');c.className='pdr';bg.appendChild(c);var g=c.getContext('2d'),W,H,DP,G=48,raf=0,t0=0,still=matchMedia('(prefers-reduced-motion:reduce)').matches;
// 스타일: 0 선 1 빨강 2 파랑 3 점선 4 해치 5 파랑해치 6 바탕채움 7 글자 8 빨강점선 9 빨강해치
function Bd(name,flip){var e=[];return {e:e,l:name,flip:flip,
 L:function(p,st){e.push({k:'l',p:p,st:st||0});return this;},
 C:function(p,st){e.push({k:'l',p:p.concat([p[0]]),st:st||0});return this;},
 H:function(ps,sp,ang,st,ol){if(ol!==false)ps.forEach(function(p){e.push({k:'l',p:p.concat([p[0]]),st:0});});e.push({k:'h',ps:ps,sp:sp,a:ang,st:st||4});return this;},
 F:function(p){e.push({k:'f',p:p,st:6});return this;},
 T:function(t,x,y,st){e.push({k:'t',t:t,x:x,y:y,st:st||7});return this;}};}
function R(x,y,w,h){return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]];}
function pin(pt,po){var c=false;for(var i=0,j=po.length-1;i<po.length;j=i++){var a=po[i],b=po[j];if((a[1]>pt[1])!=(b[1]>pt[1])&&pt[0]<(b[0]-a[0])*(pt[1]-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;}
function hull(P){P=P.slice().sort(function(a,b){return a[0]-b[0]||a[1]-b[1];});function cr(o,a,b){return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);}var lo=[],up=[],i;for(i=0;i<P.length;i++){while(lo.length>1&&cr(lo[lo.length-2],lo[lo.length-1],P[i])<=0)lo.pop();lo.push(P[i]);}for(i=P.length-1;i>=0;i--){while(up.length>1&&cr(up[up.length-2],up[up.length-1],P[i])<=0)up.pop();up.push(P[i]);}lo.pop();up.pop();return lo.concat(up);}
function D(){var d=[],k,j,b;
 // LAB 08 처마와 시선 (단면, 위가 +)
 b=Bd('LAB 08  처마와 시선 · 바람',true);
 b.H([R(-0.6,-1,8.4,1)],7,Math.PI/4,4);
 for(k=0;k<4;k++)b.L([[7.9+k*0.05,-0.35-k*0.12],[12,-0.35-k*0.12]],2);
 b.H([R(0,0,0.3,3.2)],4,Math.PI/4,4).H([R(3.0,0,0.22,3.45)],4,Math.PI/4,4).H([[[-0.3,3.15],[5.4,4.1],[5.4,3.82],[-0.3,2.88]]],4,-Math.PI/4,4);
 b.H([R(0.3,0,2.7,0.15)],3,0,4,true);
 var ey=[1.8,1.55];b.C([[1.72,1.62],[1.88,1.62],[1.88,1.48],[1.72,1.48]]).L([[1.8,1.45],[1.8,0.75],[1.6,0.15]]).L([[1.8,0.75],[2.0,0.15]]).L([[1.8,1.25],[2.1,0.95]]);
 for(k=-3;k<=5;k++){var aa=k*6*Math.PI/180;b.L([ey,[ey[0]+10*Math.cos(aa),ey[1]+10*Math.sin(aa)]],2);}
 b.L([ey,[ey[0]+(5.4-ey[0])*1.8,ey[1]+(3.82-ey[1])*1.8]],1).T('EAVE +4.10',4.4,4.45).T('EYE 1.55',0.4,1.9,7);d.push(b);
 // LAB 03 프레임 3D (등각, 화면 좌표)
 b=Bd('LAB 03  그리드 → 프레임',false);var hh=1.55,tt=0.18,X=function(x,y,z){return [(x-y)*0.866,(x+y)*0.5-z];};
 for(k=0;k<5;k++){var z=k*hh;
  if(k>0)[0,2,4,6].forEach(function(x){[0,2,4].forEach(function(y){var z0=(k-1)*hh+tt;b.L([X(x-0.06,y+0.06,z0),X(x-0.06,y+0.06,z)]).L([X(x+0.06,y-0.06,z0),X(x+0.06,y-0.06,z)]);});});
  var T1=[X(0,0,z+tt),X(6,0,z+tt),X(6,4,z+tt),X(0,4,z+tt)],S1=[X(0,4,z+tt),X(6,4,z+tt),X(6,4,z),X(0,4,z)],S2=[X(6,0,z+tt),X(6,4,z+tt),X(6,4,z),X(6,0,z)];
  b.F(T1.concat([S2[3],S2[2],S1[3]])).H([S1,S2],3.2,Math.PI/4,4).C(T1);
  b.T((k?'+'+(k*3.6).toFixed(1):'±0.0'),X(6,0,z)[0]+0.35,X(6,0,z)[1]+0.1);}
 b.T('5F',X(6,0,4*hh)[0]+0.35,X(6,0,4*hh)[1]-0.5,1);d.push(b);
 // LAB 05 주차 찾기 (평면)
 b=Bd('LAB 05  주차 배치 찾기',true);var O=[[0,0],[34,0],[36,18],[4,22]],I=[[1.2,1.2],[32.9,1.2],[34.6,17],[4.9,20.7]];
 b.H([O,I],5,Math.PI/4,4).L([[0,10.5],[36,10.5]],3).L([[-2,9],[1.5,10.5],[-2,12]],1);
 var n=0;[[2.5,0],[13.5,1]].forEach(function(r){for(var x=1.4;x<36;x+=2.5){var q=R(x,r[0],2.5,5),ok=q.every(function(p){return pin(p,I);});
  if(ok){n++;b.C(q,0).T(String(n),x+0.6,r[0]+(r[1]?1:3.4),7);}else if(q.some(function(p){return pin(p,O);})){b.C(q,8).L([q[0],q[2]],1).L([q[1],q[3]],1);}}});
 b.T('P = '+n+'대',26,8.2,1);d.push(b);
 // LAB 02 정북일조사선 (단면)
 b=Bd('LAB 02  정북일조사선',true);b.H([R(-4,-1.2,17,1.2)],7,Math.PI/4,4).H([R(-3.6,0,2.6,7)],7,-Math.PI/4,4,true).L([[0,-1.2],[0,17]],3).L([[1.5,0],[1.5,10],[5,10],[8.5,17]],8);
 for(k=0;k<5;k++){var xs=Math.max(1.5,(3*(k+1))/2)+0.2,y0=3*k;b.H([R(xs,y0,10.5-xs,0.3)],3.2,Math.PI/4,4).H([R(xs,y0+0.3,0.25,2.7)],3.2,Math.PI/4,4).H([R(10.25,y0+0.3,0.25,2.7)],3.2,Math.PI/4,4);}
 b.H([R(7.7,15,2.8,0.3)],3.2,Math.PI/4,4).T('1.5m',0.1,10.8).T('H/2',6.6,13.5,1);d.push(b);
 // LAB 09 오피스 빛 · 열 (단면)
 b=Bd('LAB 09  오피스 주광률 · 부하',true);
 b.H([R(-0.3,-0.45,10.55,0.45)],3.2,Math.PI/4,4).H([R(-0.3,3.4,10.55,0.45)],3.2,Math.PI/4,4).H([R(-0.3,0,0.3,3.4)],3.2,Math.PI/4,4).H([R(10,0,0.25,0.9)],3.2,Math.PI/4,4).H([R(10,2.9,0.25,0.5)],3.2,Math.PI/4,4).H([R(10.25,3.05,1.3,0.15)],3.2,Math.PI/4,4);
 b.L([[10.08,0.9],[10.08,2.9]],2).L([[10.17,0.9],[10.17,2.9]],2);
 for(k=0;k<4;k++)b.L([[13.6+k*0.5,5.2],[10.2-(3.4-k*0.5)*0.1-3.4+k*0.5+0.6,0]],8);
 var cu=[];for(k=0;k<=40;k++){var x=k/4;cu.push([x,0.15+2.3*Math.exp(-(10-x)/2.3)]);}b.L(cu,2).L([[0,0.7],[10,0.7]],3).H([[[6.4,0],[10,0],[10,0.7],[6.4,0.7]]],5,-Math.PI/4,9,false).T('DF 2%',0.3,0.95).T('LIT 3.6m',6.6,1.25,1);d.push(b);
 // LAB 06 동지 일조 (평면)
 b=Bd('LAB 06  동지 일조 시간',true);var BL=[[3,3],[8,3],[8,5],[6,5],[6,8],[3,8]],v=[-3.2,4.2],sh=hull(BL.concat(BL.map(function(p){return [p[0]+v[0],p[1]+v[1]];})));
 for(k=0;k<3;k++){var ar=[];for(j=0;j<=24;j++){var an=(-25+j*230/24)*Math.PI/180;ar.push([5.5+(8.5-k*1.6)*Math.cos(an),5.5+(5-k*1.1)*Math.sin(an)*-1]);}b.L(ar,k?3:2);}
 b.H([sh],6,Math.PI/4,5).F(BL).H([BL],3,-Math.PI/4,4).L([[-1,11.5],[13,11.5]],3).L([[12.6,1.2],[8,3]],1).T('09–15h  일조 2h 40m',-0.5,12.4,1);d.push(b);
 return d;}
var DR=D(),OX=0,OY=0,SCAN=380,DRAW=3000,TK=34,PER=3,HOLD=1800,CLR=420,slots=[];
function rnd(n){var x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);}
function hatch(ps,sp,a){var cs=Math.cos(a),sn=Math.sin(a),R2=ps.map(function(p){return p.map(function(q){return [q[0]*cs+q[1]*sn,-q[0]*sn+q[1]*cs];});}),lo=1e9,hi=-1e9,out=[];
 R2.forEach(function(p){p.forEach(function(q){lo=Math.min(lo,q[1]);hi=Math.max(hi,q[1]);});});
 for(var v=lo+sp/2;v<hi;v+=sp){var xs=[];R2.forEach(function(p){for(var i=0;i<p.length;i++){var A=p[i],B=p[(i+1)%p.length];if((A[1]<=v)!=(B[1]<=v))xs.push(A[0]+(v-A[1])*(B[0]-A[0])/(B[1]-A[1]));}});xs.sort(function(x,y){return x-y;});
  for(var k=0;k+1<xs.length;k+=2)out.push([[xs[k]*cs-v*sn,xs[k]*sn+v*cs],[xs[k+1]*cs-v*sn,xs[k+1]*sn+v*cs]]);}return out;}
// 도면을 프레임 크기에 맞춰 픽셀 좌표 선 목록으로 변환
function comp(d,fw,fh){var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9,f=d.flip?-1:1;d.e.forEach(function(e){(e.p||(e.ps?[].concat.apply([],e.ps):[])).forEach(function(q){x0=Math.min(x0,q[0]);x1=Math.max(x1,q[0]);y0=Math.min(y0,q[1]*f);y1=Math.max(y1,q[1]*f);});});
 var pd=G*0.45,S=Math.min((fw-2*pd)/(x1-x0),(fh-2*pd)/(y1-y0)),ox=(fw-(x1-x0)*S)/2-x0*S,oy=(fh-(y1-y0)*S)/2-y0*S,P=function(q){return [ox+q[0]*S,oy+q[1]*f*S];},L=[];
 d.e.forEach(function(e){if(e.k=='l')L.push({st:e.st,p:e.p.map(P)});else if(e.k=='f')L.push({st:6,p:e.p.map(P),z:1});else if(e.k=='t')L.push({st:e.st,t:e.t,p:[P([e.x,e.y])],z:1});
  else{var ps=e.ps.map(function(p){return p.map(P);});hatch(ps,e.sp,e.a).forEach(function(s){L.push({st:e.st,p:s});});}});
 var T=0;L.forEach(function(s){s.L=0;for(var i=1;i<s.p.length;i++)s.L+=Math.hypot(s.p[i][0]-s.p[i-1][0],s.p[i][1]-s.p[i-1][1]);if(s.z)s.L=14;T+=s.L;});d.C=L;d.T=T;d.S=S;d.ox=ox;d.oy=oy;d.f=f;}
function size(){var r=bg.getBoundingClientRect();DP=Math.min(2,devicePixelRatio||1);W=r.width;H=r.height;c.width=W*DP;c.height=H*DP;c.style.width=W+'px';c.style.height=H+'px';
 var cols=Math.floor(W/G),n=cols>=28?3:cols>=19?2:1,sw=8,x0=Math.max(1,Math.floor((cols-(n*sw+(n-1)))/2));slots=[];for(var k=0;k<n;k++)slots.push({x:x0+k*(sw+1),y:2,w:sw,h:5});PER=n;OX=(W/2)%G;OY=(H/2)%G;
 DR.forEach(function(d){comp(d,sw*G,5*G);});}
var STY={0:['rgba(236,232,222,.85)',1.1],1:['rgba(255,110,80,.95)',1.5],2:['rgba(110,175,255,.85)',1],3:['rgba(236,232,222,.5)',1,[5,5]],4:['rgba(236,232,222,.5)',.6],5:['rgba(110,175,255,.4)',.6],8:['rgba(255,110,80,.8)',1,[4,4]],9:['rgba(255,110,80,.35)',.6]};
function prog(u,id){if(u<=0)return 0;if(u>=DRAW)return 1;function w(k){var r=rnd(id*997+k);return r<.18?0:r<.85?1:r<.96?3:7;}var n=Math.floor(u/TK),p=0,T=0,k;for(k=0;k<=n;k++)p+=w(k);for(k=0;k<Math.ceil(DRAW/TK);k++)T+=w(k);return Math.min(1,p/T);}
function frame(now){if(!t0)t0=now;var t=now-t0,pages=Math.ceil(DR.length/PER),PG=PER*(SCAN+DRAW)+HOLD+CLR,pg=Math.floor(t/PG)%pages,u=t%PG,gl=u>PG-CLR?(Math.floor((u-(PG-CLR))/70)%2?0:1)*(1-(u-(PG-CLR))/CLR):1;
 g.setTransform(DP,0,0,DP,0,0);g.clearRect(0,0,W,H);g.translate(OX-G,OY-G);g.lineCap='round';g.lineJoin='round';
 var live=null;
 slots.forEach(function(sl,si){var n=pg*PER+si;if(n>=DR.length)return;var d=DR[n],v=u-si*(SCAN+DRAW),X=sl.x*G,Y=sl.y*G,fw=sl.w*G,fh=sl.h*G;if(v<0&&!still)return;g.font="11px 'JetBrains Mono',ui-monospace,monospace";
  if(!still&&v<SCAN){var q=Math.floor(v/40);for(var k=0;k<10;k++){var cx=Math.floor(rnd(n*31+q*7+k)*sl.w),cy=Math.floor(rnd(n*53+q*11+k)*sl.h);g.fillStyle=k%3?'rgba(236,232,222,'+(.06+.08*rnd(q+k))+')':'rgba(255,110,80,.14)';g.fillRect(X+cx*G+1,Y+cy*G+1,G-1,G-1);}
   g.strokeStyle='rgba(236,232,222,.5)';g.setLineDash([2,4]);g.strokeRect(X+.5,Y+.5,Math.floor(v/SCAN*sl.w*4)/4*G,fh);g.setLineDash([]);g.fillStyle='rgba(255,110,80,.9)';g.fillText('SCAN '+String(Math.floor(v/SCAN*100)).padStart(2,'0')+'%',X,Y-10);return;}
  var pr=still?1:prog(v-SCAN,n);g.save();g.globalAlpha=gl;g.translate(X,Y);g.strokeStyle='rgba(236,232,222,.28)';g.lineWidth=1;g.strokeRect(.5,.5,fw,fh);g.beginPath();g.rect(0,0,fw,fh);g.clip();
  var want=pr*d.T,tip=null;
  for(var i=0;i<d.C.length&&want>0;i++){var s=d.C[i],dl=Math.min(want,s.L);want-=dl;
   if(s.st==6){g.fillStyle='#121311';g.beginPath();s.p.forEach(function(q,k){k?g.lineTo(q[0],q[1]):g.moveTo(q[0],q[1]);});g.fill();continue;}
   if(s.t!==undefined){if(dl>=s.L){g.fillStyle=s.st==1?'rgba(255,110,80,.95)':'rgba(236,232,222,.8)';g.font="10px 'JetBrains Mono',ui-monospace,monospace";g.fillText(s.t,s.p[0][0],s.p[0][1]);}continue;}
   var y=STY[s.st]||STY[0];g.strokeStyle=y[0];g.lineWidth=y[1];g.setLineDash(y[2]||[]);g.beginPath();g.moveTo(s.p[0][0],s.p[0][1]);var acc=0;
   for(var k=1;k<s.p.length;k++){var L1=Math.hypot(s.p[k][0]-s.p[k-1][0],s.p[k][1]-s.p[k-1][1]);if(acc+L1>=dl){var f=L1?(dl-acc)/L1:0,x=s.p[k-1][0]+(s.p[k][0]-s.p[k-1][0])*f,yy=s.p[k-1][1]+(s.p[k][1]-s.p[k-1][1])*f;g.lineTo(x,yy);tip=[x,yy];break;}g.lineTo(s.p[k][0],s.p[k][1]);acc+=L1;}g.stroke();}
  g.setLineDash([]);
  if(pr<1&&tip){var gx=Math.floor((tip[0]+X)/G),gy=Math.floor((tip[1]+Y)/G);g.fillStyle='rgba(255,110,80,.16)';g.fillRect(gx*G-X+1,gy*G-Y+1,G-1,G-1);g.strokeStyle='rgba(255,110,80,.5)';g.lineWidth=1;g.beginPath();g.moveTo(0,tip[1]+.5);g.lineTo(fw,tip[1]+.5);g.moveTo(tip[0]+.5,0);g.lineTo(tip[0]+.5,fh);g.stroke();
   g.fillStyle='rgba(255,110,80,1)';g.fillRect(tip[0]-2.5,tip[1]-2.5,5,5);live={x:tip[0]+X,y:tip[1]+Y,u:(tip[0]-d.ox)/d.S,w:(tip[1]-d.oy)/d.S*d.f};}
  g.restore();g.globalAlpha=gl;g.font="11px 'JetBrains Mono',ui-monospace,monospace";var nl=Math.round(d.l.length*Math.min(1,pr*1.5));g.fillStyle='rgba(236,232,222,.85)';g.fillText(d.l.slice(0,nl)+(pr<1&&Math.floor(t/120)%2?'▌':''),X,Y+fh+20);
  g.fillStyle=pr<1?'rgba(255,110,80,.9)':'rgba(236,232,222,.45)';g.fillText(pr<1?'GEN '+String(Math.floor(pr*100)).padStart(2,'0')+'%':'DONE',X+fw-(pr<1?48:32),Y+fh+20);g.globalAlpha=1;});
 if(live){g.fillStyle='rgba(255,110,80,.95)';g.font="11px 'JetBrains Mono',ui-monospace,monospace";g.fillText('x '+live.u.toFixed(2)+'  y '+live.w.toFixed(2),live.x+8,live.y-8);}
 raf=requestAnimationFrame(frame);}
function start(){if(raf)return;size();t0=0;raf=requestAnimationFrame(frame);}
function stop(){cancelAnimationFrame(raf);raf=0;g&&g.clearRect(0,0,c.width,c.height);}
new MutationObserver(function(){bg.classList.contains('on')?start():setTimeout(function(){if(!bg.classList.contains('on'))stop();},600);}).observe(bg,{attributes:true,attributeFilter:['class']});
addEventListener('resize',function(){if(raf)size();});})();

// 표지 인트로 (세션당 한 번, 누르면 건너뜀)
(function(){var c=document.querySelector('.cv0'),f=document.querySelector('.ifr');if(!c||!f)return;var im=[].slice.call(f.querySelectorAll('img')),b=document.body,h=document.documentElement,v=document.querySelector('.cvv');
var seen=false;try{seen=sessionStorage.getItem('intro');sessionStorage.setItem('intro','1');}catch(e){}
if(seen||matchMedia('(prefers-reduced-motion:reduce)').matches){f.remove();return;}
var r=c.getBoundingClientRect(),fw=Math.min(innerWidth*.22,innerHeight*.36),fh=innerHeight*.58,L0=innerWidth/2-fw/2-r.left,T0=innerHeight/2-fh/2-r.top;c.style.setProperty('--ic','inset('+T0+'px '+(r.width-L0-fw)+'px '+(r.height-T0-fh)+'px '+L0+'px)');
b.classList.add('cvi');h.classList.add('introing');var T=[],done=false;function at(ms,fn){T.push(setTimeout(fn,ms));}
function show(i){im.forEach(function(x,j){x.classList.toggle('on',j===i);});}
function end(){if(done)return;done=true;T.forEach(clearTimeout);b.classList.add('open');setTimeout(function(){b.classList.remove('cvi','open','w1','w2','w3');h.classList.remove('introing');f.classList.add('out');im.forEach(function(x){x.classList.remove('on');});setTimeout(function(){f.remove();},1100);},1200);if(v){try{v.currentTime=0;v.play();}catch(e){}}}
at(250,function(){b.classList.add('w1');});at(650,function(){b.classList.add('w2');});at(1050,function(){b.classList.add('w3');});
var n=im.length,t0=400,step=230;for(var i=0;i<n;i++)(function(i){at(t0+i*step,function(){show(i);});})(i);
at(t0+n*step+500,end);addEventListener('click',end,{once:true});addEventListener('keydown',end,{once:true});})();
// 표지 기본 화면: 지적도. 커서가 지나간 필지에서 대지 분석 → 정북 사선 → 매스가 한 층씩 쌓인다.
(function(){var cv=document.querySelector('.cv0 .cad');if(!cv)return;var g=cv.getContext('2d'),W,H,DP=1,P=[],B=[],hot=null,mx=-1,my=-1,auto=true,ax=0,ay=0,at=0,last=0,still=matchMedia('(prefers-reduced-motion:reduce)').matches,info=document.querySelector('.cdr');
var M=0.42,FH=7,ROT=-0.12,CS=Math.cos(ROT),SN=Math.sin(ROT);
function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function area(p){var s=0;for(var i=0;i<p.length;i++){var a=p[i],b=p[(i+1)%p.length];s+=a[0]*b[1]-b[0]*a[1];}return Math.abs(s)/2;}
function cen(p){var x=0,y=0;p.forEach(function(q){x+=q[0];y+=q[1];});return [x/p.length,y/p.length];}
function lerp(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];}
function inside(x,y,p){var c=false;for(var i=0,j=p.length-1;i<p.length;j=i++){var a=p[i],b=p[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])c=!c;}return c;}
// 볼록 다각형을 선분 a-b 기준 안쪽으로 d만큼 들인 반평면으로 자르기
function clipHalf(p,a,b,d,s){var dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy)||1,nx=-dy/L*s,ny=dx/L*s,f=function(q){return (q[0]-a[0])*nx+(q[1]-a[1])*ny-d;},o=[];
 for(var i=0;i<p.length;i++){var P1=p[i],P2=p[(i+1)%p.length],f1=f(P1),f2=f(P2);if(f1>=0)o.push(P1);if((f1>=0)!==(f2>=0))o.push(lerp(P1,P2,f1/(f1-f2)));}return o;}
function sgn(p){var s=0;for(var i=0;i<p.length;i++){var a=p[i],b=p[(i+1)%p.length];s+=a[0]*b[1]-b[0]*a[1];}return s>0?1:-1;}
function inset(p,d){var s=sgn(p),o=p;for(var i=0;i<p.length&&o.length>2;i++)o=clipHalf(o,p[i],p[(i+1)%p.length],d,s);return o;}
function clipY(p,yc){var o=[];for(var i=0;i<p.length;i++){var a=p[i],b=p[(i+1)%p.length],fa=a[1]-yc,fb=b[1]-yc;if(fa>=0)o.push(a);if((fa>=0)!==(fb>=0))o.push(lerp(a,b,fa/(fa-fb)));}return o;}
function split(q,R,out){var A=area(q);if(A<(1400+R()*2600)||q.length!==4){out.push(q);return;}
 var e0=Math.hypot(q[1][0]-q[0][0],q[1][1]-q[0][1])+Math.hypot(q[3][0]-q[2][0],q[3][1]-q[2][1]),e1=Math.hypot(q[2][0]-q[1][0],q[2][1]-q[1][1])+Math.hypot(q[0][0]-q[3][0],q[0][1]-q[3][1]),t=.32+R()*.36,u=t+(R()-.5)*.12;
 if(e0>=e1){var m1=lerp(q[0],q[1],t),m2=lerp(q[3],q[2],u);split([q[0],m1,m2,q[3]],R,out);split([m1,q[1],q[2],m2],R,out);}
 else{var n1=lerp(q[1],q[2],t),n2=lerp(q[0],q[3],u);split([q[0],q[1],n1,n2],R,out);split([n2,n1,q[2],q[3]],R,out);}}
function size(){var r=cv.getBoundingClientRect();DP=Math.min(2,devicePixelRatio||1);W=r.width;H=r.height;cv.width=W*DP;cv.height=H*DP;g.setTransform(DP,0,0,DP,0,0);
 var R=rng(11),S=Math.max(120,Math.min(190,W/8)),cols=Math.ceil(W*1.3/S)+2,rows=Math.ceil(H*1.3/S)+2,L=[],ox=-W*.15-S,oy=-H*.15-S;
 for(var j=0;j<=rows;j++){L[j]=[];for(var i=0;i<=cols;i++){var x=ox+i*S+(R()-.5)*S*.35,y=oy+j*S*.78+(R()-.5)*S*.3;L[j][i]=[W/2+(x-W/2)*CS-(y-H/2)*SN,H/2+(x-W/2)*SN+(y-H/2)*CS];}}
 P=[];B=[];var no=1;for(j=0;j<rows;j++)for(i=0;i<cols;i++){var blk=[L[j][i],L[j][i+1],L[j+1][i+1],L[j+1][i]],road=(i%3===0||j%4===0)?9:5,q=inset(blk,road);if(q.length<4)continue;q=q.slice(0,4);var out=[];split(q,R,out);
  out.forEach(function(p){var c=cen(p);if(c[0]<-60||c[0]>W+60||c[1]<-60||c[1]>H+60)return;P.push({p:p,c:c,a:area(p)*M*M,no:(100+((no*37)%900))+'-'+(1+no%23),b:null});no++;});}}
function line(p,close){g.beginPath();p.forEach(function(v,i){i?g.lineTo(v[0],v[1]):g.moveTo(v[0],v[1]);});if(close!==false)g.closePath();}
// 한 필지의 건물: 대지안의 공지 → 층마다 북쪽(화면 위)에서 정북 사선만큼 깎인 평면
function plan(o){var R=rng(o.no.length*97+Math.round(o.a)),sb=inset(o.p,4+R()*3);if(sb.length<3)return null;var ys=sb.map(function(q){return q[1];}),y0=Math.min.apply(null,ys),y1=Math.max.apply(null,ys),n=Math.max(2,Math.min(14,Math.round(o.a/45+R()*5))),fl=[];
 for(var f=0;f<n;f++){var cut=f<3?0:(f-2)*FH*.55,pl=clipY(sb,y0+cut);if(pl.length<3||area(pl)<area(sb)*.25)break;fl.push(pl);}return {fl:fl,y0:y0,y1:y1};}
function drawB(b,now){var k=Math.min(b.pl.fl.length,Math.floor((now-b.t0)/70)),live=b===hot&&now-b.t0<b.pl.fl.length*70+900,fade=live?1:.62;if(k<=0)return;
 for(var f=0;f<k;f++){var pl=b.pl.fl[f],z0=-f*FH,z1=-(f+1)*FH;
  for(var i=0;i<pl.length;i++){var a=pl[i],c=pl[(i+1)%pl.length];
   line([[a[0],a[1]+z0],[c[0],c[1]+z0],[c[0],c[1]+z1],[a[0],a[1]+z1]]);g.fillStyle='rgba(22,21,19,'+(.92*fade)+')';g.fill();g.strokeStyle='rgba(239,237,230,'+(.32*fade)+')';g.lineWidth=.7;g.stroke();}
  line(pl.map(function(q){return [q[0],q[1]+z1];}));g.fillStyle=f===k-1&&live?'rgba(255,107,74,.20)':'rgba(46,44,40,'+(.95*fade)+')';g.fill();g.strokeStyle=f===k-1&&live?'#ff6b4a':'rgba(239,237,230,'+(.7*fade)+')';g.lineWidth=f===k-1?1.1:.8;g.stroke();}}
function draw(now){g.clearRect(0,0,W,H);g.font='9px "JetBrains Mono",ui-monospace,monospace';g.textAlign='center';
 P.forEach(function(o){line(o.p);g.strokeStyle='rgba(239,237,230,.16)';g.lineWidth=.8;g.stroke();if(o.a>260){g.fillStyle='rgba(239,237,230,.16)';g.fillText(o.no,o.c[0],o.c[1]+3);}});
 if(hot){var o=hot.o,t=now-hot.t0;line(o.p);g.strokeStyle='#ff6b4a';g.lineWidth=1.4;g.stroke();g.fillStyle='rgba(255,107,74,.07)';g.fill();
  var sb=inset(o.p,5);if(sb.length>2){g.setLineDash([4,4]);line(sb);g.strokeStyle='rgba(255,107,74,.7)';g.lineWidth=.8;g.stroke();g.setLineDash([]);}
  g.textAlign='left';o.p.forEach(function(a,i){var c=o.p[(i+1)%o.p.length],L=Math.hypot(c[0]-a[0],c[1]-a[1])*M;if(L<9)return;g.fillStyle='rgba(77,163,255,.9)';g.fillText(L.toFixed(1),(a[0]+c[0])/2+4,(a[1]+c[1])/2-3);});
  var sc=Math.min(1,t/500);g.strokeStyle='rgba(255,107,74,'+(.5*(1-sc))+')';g.beginPath();var ys=o.p.map(function(q){return q[1];}),ya=Math.min.apply(null,ys),yb=Math.max.apply(null,ys);g.moveTo(o.c[0]-60,ya+(yb-ya)*sc);g.lineTo(o.c[0]+60,ya+(yb-ya)*sc);g.stroke();}
 B.sort(function(a,b){return a.pl.y1-b.pl.y1;}).forEach(function(b){drawB(b,now);});
 if(hot&&info){var n=hot.pl.fl.length,k=Math.min(n,Math.max(0,Math.floor((now-hot.t0)/70))),bc=hot.pl.fl.length?Math.round(area(hot.pl.fl[0])/area(hot.o.p)*100):0;
  info.textContent='지번 '+hot.o.no+' · 대지 '+Math.round(hot.o.a)+'㎡ · 건폐 '+bc+'% · '+k+'/'+n+'F';}}
function pick(x,y,now){for(var i=0;i<P.length;i++){var o=P[i];if(inside(x,y,o.p)){if(hot&&hot.o===o)return;if(!o.b){var pl=plan(o);if(!pl||!pl.fl.length)return;o.b={o:o,pl:pl,t0:now+420};B.push(o.b);if(B.length>70){var old=B.shift();old.o.b=null;}}else{o.b.t0=now+200;}hot=o.b;return;}}}
cv.parentNode.addEventListener('mousemove',function(e){var r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top;auto=false;at=performance.now();});
function loop(now){requestAnimationFrame(loop);if(now-last<30)return;last=now;
 if(auto||now-at>6000){ax=W*(.5+.38*Math.sin(now/5200))+W*.08*Math.sin(now/1300);ay=H*(.32+.24*Math.sin(now/3700+1));if(!document.body.classList.contains('cvi'))pick(ax,ay,now);}else if(mx>=0)pick(mx,my,now);
 draw(now);}
addEventListener('resize',function(){size();});size();if(still){draw(performance.now());}else requestAnimationFrame(loop);})();
(function(){var m=document.querySelector('.cvm');if(!m)return;var bg=document.querySelectorAll('.cv0 .bg'),a=m.querySelectorAll('a');
a.forEach(function(x,i){x.addEventListener('mouseenter',function(){bg.forEach(function(b,k){b.classList.toggle('on',k===i)});m.classList.add('hov');a.forEach(function(o){o.classList.toggle('on',o===x)});});});
m.addEventListener('mouseleave',function(){bg.forEach(function(b){b.classList.remove('on')});m.classList.remove('hov');a.forEach(function(o){o.classList.remove('on')});});})();
(function(){var pv=document.querySelector('.lpv');if(!pv)return;document.querySelectorAll('.lr.f').forEach(function(r){
r.addEventListener('mouseenter',function(){pv.src=r.dataset.img;pv.classList.add('on');});r.addEventListener('mouseleave',function(){pv.classList.remove('on');});
r.addEventListener('mousemove',function(e){pv.style.transform='translate('+(e.clientX+28)+'px,'+(e.clientY-120)+'px)';});});})();
(function(){var st=document.querySelector('.stg');if(!st)return;var sl=st.querySelectorAll('.sl'),li=document.querySelectorAll('.ixl li');
li.forEach(function(l){l.addEventListener('mouseenter',function(){var i=+l.dataset.i;sl.forEach(function(x,k){x.classList.toggle('on',k===i)});li.forEach(function(o){o.classList.toggle('on',o===l)});});});})();

const lb=document.getElementById('lb'),li=lb.querySelector('img'),lc=lb.querySelector('.c');let L=[],ix=0;
function show(i){ix=(i+L.length)%L.length;li.src=L[ix].src;const f=L[ix].closest('figure').querySelector('figcaption');lc.textContent=(f?f.textContent:'')+'  '+(ix+1)+' / '+L.length;}
document.addEventListener('click',e=>{
 if(e.target.closest('#lb button')){show(ix+(e.target.classList.contains('n')?1:-1));return}
 if(e.target.closest('#lb')){lb.classList.remove('on');return}
 const im=e.target.closest('figure img');if(im){L=[...document.querySelectorAll('figure img')];show(L.indexOf(im));lb.classList.add('on')}});
document.addEventListener('keydown',e=>{if(!lb.classList.contains('on'))return;if(e.key==='Escape')lb.classList.remove('on');if(e.key==='ArrowRight')show(ix+1);if(e.key==='ArrowLeft')show(ix-1)});
if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{rootMargin:'0px 0px -8% 0px'});
document.querySelectorAll('.blk,.txt,.work').forEach(el=>{el.classList.add('fade');io.observe(el)})}
""".replace('__HOLES__',HOLES).replace('__EMAIL__',SITE['email']).replace('__PHONE__',SITE['phone'])

def page(title, body, root, dark=False, on='', desc='', og='og-card.jpg'):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or SITE['name_ko']+' — 건축 포트폴리오')}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc or '건축 포트폴리오 2021–2026 · Architectural Designer · 홍익대학교 건축학과')}"><meta property="og:type" content="website"><meta property="og:site_name" content="{SITE['name_ko']} — Portfolio"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{root}style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect width=%2232%22 height=%2232%22 fill=%22%231d1c1a%22/%3E%3Ctext x=%2216%22 y=%2222%22 font-size=%2216%22 text-anchor=%22middle%22 fill=%22%23f6f5f2%22 font-family=%22sans-serif%22%3EH%3C/text%3E%3C/svg%3E">
<meta property="og:image" content="https://coin9563-max.github.io/{og}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
</head><body class="{dark if isinstance(dark, str) else ('dark' if dark else '')}">
<header class="top"><a class="name" href="{root}index.html">{SITE['name_ko']}<span>{SITE['name_en']}</span></a>
<nav><a href="{root}projects.html" class="{'on' if on=='w' else ''}">Projects</a><a href="{root}publish.html" class="{'on' if on=='b' else ''}">Publish</a><a href="{root}practice.html" class="{'on' if on=='r' else ''}">Practice</a><a href="{root}process.html" class="{'on' if on=='p' else ''}">Process</a><a href="{root}about.html" class="{'on' if on=='a' else ''}">About</a></nav></header>
<main>
{body}
<footer>© 2026 {SITE['name_ko']} {SITE['name_en']}</footer>
</main>
<div id="lb"><img alt=""><button class="p" aria-label="이전">‹</button><button class="n" aria-label="다음">›</button><div class="c"></div></div>
<script>{JS}</script>
</body></html>"""

def para(t):
    return ''.join(f'<p>{E(x)}</p>' for x in t.split('\n\n') if x.strip()).replace('\n', '<br>')

def block(b, root):
    k = b[0]
    if k == 'narrow':
        cap = f'<figcaption>{E(b[2])}</figcaption>' if b[2] else ''
        return f'<figure class="blk nr">{pic(b[1], root, alt=b[2])}{cap}</figure>'
    if k in ('img', 'wide'):
        cap = f'<figcaption>{E(b[2])}</figcaption>' if b[2] else ''
        return f'<figure class="blk {"w" if k=="wide" else ""}">{pic(b[1], root, alt=b[2])}{cap}</figure>'
    if k in ('pair', 'grid'):
        ids = b[1]; cols = b[3] if k == 'grid' else 2
        if k == 'pair':
            # 높이를 맞추도록 비율 기반 열 폭
            rs = [use(i)[1] / use(i)[2] for i in ids]
            tmpl = ' '.join(f'{r:.3f}fr' for r in rs)
        else:
            tmpl = f'repeat({cols},1fr)'
        imgs = ''.join(f'<div>{pic(i, root)}</div>' for i in ids)
        cap = f'<figcaption>{E(b[2])}</figcaption>' if b[2] else ''
        return f'<figure class="blk"><div class="row {"g" if k=="grid" else ""}" style="grid-template-columns:{tmpl}">{imgs}</div>{cap}</figure>'
    if k == 'video':
        for ext in ('mp4', 'jpg'):
            d = f'{OUT}/vid/{b[1]}.{ext}'
            if not os.path.exists(d): shutil.copy(f'{VID}/{b[1]}.{ext}', d)
        cap = f'<figcaption>{E(b[2])}</figcaption>' if len(b) > 2 and b[2] else ''
        return f'<figure class="blk vid"><video src="{root}vid/{b[1]}.mp4" poster="{root}vid/{b[1]}.jpg" muted loop playsinline autoplay preload="metadata" controls></video>{cap}</figure>'
    if k == 'text':
        en = f'<small>{E(b[3])}</small>' if len(b) > 3 and b[3] else ''
        return f'<section class="txt"><h2>{E(b[1])}{en}</h2><div class="b">{para(b[2])}</div></section>'
    if k == 'list':
        return '<ol class="leg">' + ''.join(f'<li>{E(x)}</li>' for x in b[2]) + '</ol>'
    raise ValueError(k)

# ---- style
open(f'{OUT}/style.css', 'w').write(CSS)
open(f'{OUT}/.nojekyll', 'w').write('')


def cardgrid(items):
    out=[]
    for it in items:
        if it.get('img') is not None:
            s,w,h=use(it['img'],thumb=True); im=f'<img src="{s}" width="{w}" height="{h}" loading="lazy" alt="{E(it["title"])}">'
        else: im='<em>이미지 준비 중</em>'
        inner=f'<div class="im">{im}</div><div class="t">{E(it["title"])}</div><div class="k">{E(it["kind"])} · {it["year"]}{" · 책 펼쳐보기 →" if it.get("slug") else ""}</div>'
        out.append(f'<a class="card" href="publish/{it["slug"]}.html">{inner}</a>' if it.get('slug') else f'<div class="card">{inner}</div>')
    return '<section class="cards"><p class="cnote">졸업전시 때 만든 책 두 권이에요. 표지를 누르면 실제 책처럼 펼쳐서 넘겨볼 수 있어요.</p>'+''.join(out)+'</section>'
def practice():
    cards=[]
    for i in PRACTICE:
        if not i.get('slug'): continue
        s,w,h=use(i['thumb'],thumb=True)
        cards.append(f'<a class="work" href="practice/{i["slug"]}.html"><div class="ph"><img src="{s}" width="{w}" height="{h}" loading="lazy" alt="{E(i["title"])}" style="object-position:{i.get("pos","50% 50%")}"></div><div class="cap"><span class="t">{E(i["title"])}</span><span class="k">{E(i["kind"])} · {i["year"]}</span></div></a>')
    rows=''.join(f'<li><span class="y">{E(i["year"])}</span><span class="t">{E(i["org"] if i.get("org") else i["title"])}</span><span class="k">{E(i["role"] if i.get("role") else i["kind"])}</span></li>' for i in PRACTICE if not i.get('hide_in_list') and not i.get('slug'))
    return ('<section class="works pw">'+''.join(cards)+'</section>' if cards else '')+'<ul class="plist">'+rows+'</ul>'
# ---- index
rows, pvs = [], []
for k, p in enumerate(PROJECTS):
    src, w, h = use(p['hero'], thumb=True)
    pos = p.get("pos", "50% 50%")
    ds, dw_, dh = use(p['dwg'], thumb=True) if p.get('dwg') else (src, w, h)
    lz = '' if k == 0 else 'loading="lazy"'
    rows.append(f'''<li data-i="{k}" class="{"on" if k==0 else ""}"><a href="works/{p["slug"]}.html"><span class="n">{p["no"]}</span><span class="t">{E(p["title"])}</span><span class="k">{E(p["kind"])} · {p["year"]}</span><img class="mt" src="{src}" width="{w}" height="{h}" alt="" loading="lazy" style="object-position:{pos}"><span class="ms">{E(p.get("statement",""))}</span></a></li>''')
    pvs.append(f'''<a class="sl{" on" if k==0 else ""}" href="works/{p["slug"]}.html"><div class="r"><img src="{src}" width="{w}" height="{h}" alt="{E(p["title"])}" style="object-position:{pos}" {lz}></div><div class="d"><img src="{ds}" width="{dw_}" height="{dh}" alt="{E(p["title"])} 도면" {lz}></div>
<div class="cd" style="background:{p.get('tone','#d8b04a')}"><span class="cn">{p["no"]} — {E(p["kind"])} · {p["year"]}</span><b>{E(p["title"])}</b><p>{E(p.get("statement",""))}</p><span class="go">프로젝트 보기 →</span></div></a>''')
body = f'''<section class="ix" id="projects"><div class="ixh"><p class="pk">01 — Projects</p><h1>Selected Works <span>2021–2026</span></h1><p class="sub">{SITE["school"]} · 설계 스튜디오 · 졸업설계</p></div>
<ul class="ixl">{"".join(rows)}</ul><div class="stg">{"".join(pvs)}</div></section>'''
open(f'{OUT}/projects.html', 'w').write(page(f'Projects — {SITE["name_ko"]}', body, '', on='w'))

# ---- Publish: 서가
def shelf():
    out=[]
    for it in PUBLISH:
        s_,w,h=use(it['img'],thumb=True)
        out.append(f'''<a class="bk{' paper' if it.get('paper') else ''}" href="publish/{it["slug"]}.html"><div class="obj"><img src="{s_}" width="{w}" height="{h}" alt="{E(it["title"])}"><i></i></div>
<div class="meta"><span>{E(it["kind"])} · {it["year"]}</span><b>{E(it["title"])}</b><em>{E(it.get("desc",""))}</em><u>펼쳐 읽기 →</u></div></a>''')
    return ''.join(out)
body = f'''<section class="shelfh"><p class="pk">02 — Publish</p><h1>Books</h1><p>졸업전시를 위해 만든 책 두 권과 학술대회 논문 한 편. 표지를 누르면 실제 책처럼 넘겨 볼 수 있다.</p></section><section class="shelf">{shelf()}</section>'''
open(f'{OUT}/publish.html', 'w').write(page(f'Publish — {SITE["name_ko"]}', body, '', dark='pubpg', on='b'))

# ---- Practice: 원장(Ledger)
def ledger():
    rows=[]
    for i in PRACTICE:
        if i.get('hide_in_list'): continue
        if i.get('slug'):
            s_,w,h=use(i['thumb'],thumb=True)
            rows.append(f'''<a class="lr f" href="practice/{i["slug"]}.html" ><span class="y">{E(i["year"])}</span><span class="th"><img src="{s_}" alt="" loading="lazy"></span><span class="t"><b>{E(i["title"])}</b><small>{E(i.get("org") or i["kind"])}</small></span><span class="r">{E(i.get("role") or i["kind"])}</span><span class="go">→</span></a>''')
        else:
            rows.append(f'''<div class="lr"><span class="y">{E(i["year"])}</span><span class="th"></span><span class="t"><b>{E(i.get("org") or i["title"])}</b><small>{E(i["title"] if i.get("org") and i["title"]!=i["org"] else i["kind"])}</small></span><span class="r">{E(i.get("role") or i["kind"])}</span><span class="go"></span></div>''')
    return ''.join(rows)
body = f'''<section class="ledh"><p class="pk">03 — Practice &amp; Activities</p><h1>Practice<br>&amp; Activities</h1><div class="lcol"><span>Year</span><span></span><span>Project · Office</span><span>Role</span></div></section><section class="ledger">{ledger()}</section>'''
open(f'{OUT}/practice.html', 'w').write(page(f'Practice — {SITE["name_ko"]}', body, '', dark='ledpg', on='r'))

# ---- 표지
def cover():
    INTRO=[use(i,thumb=True)[0] for i in [643,298,3101,280,2966,87,307]]
    feat=[i for i in PRACTICE if i.get('slug')]
    items=[('01','Projects','projects.html',f'설계 작업 {len(PROJECTS)}','PRJ'),
           ('02','Publish','publish.html',f'책 {sum(1 for x in PUBLISH if not x.get("paper"))} · 논문 {sum(1 for x in PUBLISH if x.get("paper"))}','PUB'),
           ('03','Practice','practice.html',f'실무 · 활동 {len(PRACTICE)}','PRA'),
           ('04','Process','process.html','AI와 설계하기',''),
           ('05','About','about.html','소개 · 연락처','ABT')]
    import json as _j, html as _h
    rows=[[i.get('year',''),i['title'],i.get('org',''),(i.get('role','') or '').split(' · ')[0]] for i in PRACTICE if not i.get('hide_in_list')]
    FOLDER_B='<svg class="fb0" viewBox="0 0 160 120" aria-hidden="true"><path d="M4 14 Q4 8 10 8 H56 Q60 8 63 12 L68 18 H150 Q156 18 156 24 V112 Q156 116 152 116 H8 Q4 116 4 112 Z"/></svg>'
    FOLDER_F='<svg class="ff0" viewBox="0 0 160 120" aria-hidden="true"><path d="M2 50 Q2 44 8 44 H152 Q158 44 158 50 L154 112 Q154 116 150 116 H10 Q6 116 6 112 Z"/><path class="ln" d="M14 106 H60"/></svg>'
    PRJ_BG='<div class="bg prjg"><div class="fdg">'+''.join(f'<a class="fd" href="works/{p["slug"]}.html" tabindex="-1" style="--i:{k}">'+FOLDER_B+f'<img src="{use(p["hero"],thumb=True)[0]}" alt="">'+FOLDER_F+f'<span class="fn">{p["title"]}</span></a>' for k,p in enumerate(PROJECTS[:6]))+'</div></div>'
    PUB_BG='<div class="bg pubg" data-a="book/from-city-to-earth/01.jpg" data-b="book/unwashed/01.jpg" data-p="'+_h.escape(_j.dumps([p['title'] for p in PROJECTS],ensure_ascii=False))+'"></div>'
    LAB={'mvsf-neom':'JAdU · 정림 2025','salmgut':'삶것 · 인턴 2024','deau-hannam':"SLA · D'EAU 2026",'mungyeong':'문경 · RA 2025','d5-seminar':'D5 세미나 2025','udongwoo':'우동우 · 2024–'}
    phs=[[use(i['thumb'],thumb=True)[0],LAB.get(i['slug'],i['title'])] for i in PRACTICE if i.get('slug') and i.get('thumb')]
    phs.sort(key=lambda r: r[1].startswith('SLA'))
    PRA_BG='<div class="bg prag" data-p="'+_h.escape(_j.dumps(phs,ensure_ascii=False))+'" data-cam="'+_h.escape(open(os.path.join(os.path.dirname(__file__),'cover_cam.svg')).read())+'" data-pin="'+_h.escape(open(os.path.join(os.path.dirname(__file__),'cover_pin.svg')).read())+'"></div>'
    ABT_BG='<div class="bg grid abtg">'+open(os.path.join(os.path.dirname(__file__),'cover_seoul.svg')).read()+'</div>'
    li=''.join(f'<li><a href="{h}" data-bg="{b}"><span class="n">{n}</span><span class="w">{t}</span></a></li>' for n,t,h,c,b in items)
    return f'''<section class="cv0"><canvas class="cad" aria-hidden="true"></canvas><div class="cvo" aria-hidden="true"></div><div class="ifr" aria-hidden="true">{"".join(f'<img src="{u}" alt="">' for u in INTRO)}</div><div class="bgs">{"".join(f'<div class="bg" style="background-image:url({b})"></div>' if b and b not in ('PUB','PRA','PRJ','ABT') else (PRJ_BG if b=='PRJ' else PRA_BG if b=='PRA' else ABT_BG if b=='ABT' else '<div class="bg grid"></div>' if b!='PUB' else PUB_BG) for k,(*_,b) in enumerate(items))}</div>
<div class="cvh"><p>Portfolio 2021–2026</p><h1>{SITE["name_ko"]}<span>{SITE["name_en"]}</span></h1></div>
<ol class="cvm">{li}</ol><p class="cvf"><a href="mailto:{SITE["email"]}">{SITE["email"]}</a><span class="cdr"></span><span>{SITE["school"]}</span></p></section><p class="iwd" aria-hidden="true"><span>Land</span><span>Material</span><span>Structure</span></p>'''
open(f'{OUT}/index.html', 'w').write(page(f'{SITE["name_ko"]} — Portfolio', cover(), '', dark='coverpg', on=''))

# ---- projects / practice detail pages
def detail(p, prv, nxt, folder, back):
    r = '../'
    meta = ''.join(f'<dt>{E(a)}</dt><dd>' + (f'<a href="{E(b)}" target="_blank" rel="noopener">{E(b.split("//")[-1].rstrip("/"))} ↗</a>' if b.startswith('http') else E(b)) + '</dd>' for a, b in p['meta'])
    en = f'<p class="en">{E(p["intro_en"])}</p>' if p.get('intro_en') else ''
    sub = f'<small>{E(p["sub"])}</small>' if p.get('sub') else ''
    hero = block(('video', p['hero_video']), r).replace('class="blk vid"', 'class="hero"') if p.get('hero_video') else f'<div class="hero">{pic(p["hero"], r, alt=p["title"])}</div>'
    no = f'{p["no"]} — ' if p.get('no') else ''
    head = f'''{hero}
<section class="phead"><div><div class="no">{no}{E(p["kind"])}</div><h1>{E(p["title"])}{sub}</h1><dl>{meta}</dl></div>
<div><p class="st">{E(p["statement"])}</p><div class="body">{"".join(f"<p>{E(x)}</p>" for x in p["intro"])}{en}</div></div></section>'''
    blocks = '\n'.join(block(b, r) for b in p['blocks'])
    nav = '<nav class="pnav">'
    nav += f'<a href="{prv["slug"]}.html"><span>← 이전</span>{E(prv["title"])}</a>' if prv else f'<a href="../{back}.html"><span>←</span>Index</a>'
    nav += f'<a href="{nxt["slug"]}.html"><span>다음 →</span>{E(nxt["title"])}</a>' if nxt else f'<a href="../{back}.html"><span>→</span>Index</a>'
    nav += '</nav>'
    og = use(p['hero'], thumb=True)[0] if p.get('hero') is not None else 'img/t_307.jpg'
    open(f'{OUT}/{folder}/{p["slug"]}.html', 'w').write(
        page(f'{p["title"]} — {SITE["name_ko"]}', head + blocks + nav, r, dark=p.get('dark', False), on=('r' if folder=='practice' else 'w'), desc=p['statement'], og=og))

for n, p in enumerate(PROJECTS):
    detail(p, PROJECTS[n-1] if n else None, PROJECTS[n+1] if n+1 < len(PROJECTS) else None, 'works', 'projects')
FEAT = [i for i in PRACTICE if i.get('slug')]
for n, p in enumerate(FEAT):
    detail(p, FEAT[n-1] if n else None, FEAT[n+1] if n+1 < len(FEAT) else None, 'practice', 'practice')

# ---- about
A = ABOUT
def tbl(rows):
    def nm(b): return f'<a href="{E(LINKS[b])}" target="_blank" rel="noopener">{E(b)} ↗</a>' if b in LINKS else E(b)
    return '<table>' + ''.join(f'<tr><td>{E(a)}</td><td>{nm(b)}' + (f' <span class="r">· {E(c)}</span>' if c else '') + '</td></tr>' for a, b, c in rows) + '</table>'
LINKS={'D5 Render Student Ambassador':'https://www.d5render.com/ko/d5-campus-ambassador'}
lead = f'<p class="lead">{E(A["intro"])}</p>' if A.get('intro') else ''
def bc_sec(no, label, rows):
    return f'<section><h3><b>{no}</b>{label}</h3>' + ''.join(f'<div class="it">' + (f'<span>{E(a)}</span>' if a else '') + f'<strong>{E(b)}</strong>' + (f'<em>{E(c)}</em>' if c else '') + '</div>' for a, b, c in rows) + '</section>'
body = f'''<section class="bc" aria-label="명함"><div class="bcs">
<p class="t1">Portfolio 2021–2026<span>Architectural Designer · {SITE["school"]}</span></p><i class="seal" aria-hidden="true">{HOLES}</i>{LINES}
<h1>{SITE["name_ko"]}<span>{SITE["name_en"]}</span></h1>
<dl class="ct" id="contact"><div><dt>E</dt><dd><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></dd></div><div><dt>T</dt><dd><a href="tel:{SITE["phone"].replace("-","")}">{SITE["phone"]}</a></dd></div><div><dt>W</dt><dd><a href="index.html">coin9563-max.github.io</a></dd></div></dl>
<div class="c1"><p class="lead">{E(A.get("intro",""))}</p><div class="c1s">{bc_sec('01','Education',A['education'])}{bc_sec('02','Interests',[('',A.get('interests',''),'')])}</div></div>
<div class="c2">{bc_sec('03','Experience',A['experience'])}</div>
<div class="c3">{bc_sec('04','Awards &amp; Activities',A['activities'])}{bc_sec('05','Skills',[(a,b,'') for a,b in A['skills']])}</div>
<p class="sz">90 × 50 mm</p><i class="cm" aria-hidden="true"></i></div></section>
<script>try{{if(sessionStorage.getItem('bcfly')){{sessionStorage.removeItem('bcfly');document.body.classList.add('flyin');}}}}catch(x){{}}</script>'''
open(f'{OUT}/about.html', 'w').write(page(f'About — {SITE["name_ko"]}', body, '', dark='cardpg', on='a', desc=A.get('intro','')))
print('ok', len(os.listdir(OUT + '/img')), 'images')

# ---- PUBLISH 플립북
BOOKJS=open(os.path.join(os.path.dirname(__file__),'book.js')).read()
os.makedirs(f'{OUT}/publish', exist_ok=True)
for it in PUBLISH:
    if not it.get('slug'): continue
    sd=os.path.join(BK, it['pages']); dd=f'{OUT}/book/{it["slug"]}'; os.makedirs(dd, exist_ok=True)
    files=sorted(f for f in os.listdir(sd) if f.endswith('.jpg'))
    for k,f in enumerate(files,1):
        dst=f'{dd}/{k:02d}.jpg'
        if not os.path.exists(dst): shutil.copy(os.path.join(sd,f), dst)
    w,h=Image.open(f'{dd}/01.jpg').size
    pdfa=''
    if it.get('pdf'):
        shutil.copy(os.path.join(os.path.dirname(__file__),it['pdf']), f'{dd}/{it["pdf"]}')
        pdfa=f' <a class="pdfl" href="../book/{it["slug"]}/{it["pdf"]}" download>PDF ↓</a>'
    cfg=json.dumps(dict(n=len(files), ar=round(w/h,4), dir=f'../book/{it["slug"]}/', back='../publish.html'))
    open(f'{OUT}/publish/{it["slug"]}.html','w').write(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(it['title'])} — {SITE['name_ko']}</title>
<meta name="description" content="{E(it['desc'])}"><meta property="og:title" content="{E(it['title'])}">
<meta property="og:image" content="https://coin9563-max.github.io/book/{it['slug']}/01.jpg">
<link rel="stylesheet" href="../style.css"></head>
<body class="dark bookpg">
<header class="top"><a class="name" href="../publish.html">← {SITE['name_ko']}<span>Publish</span></a><span class="bt">{E(it['title'])} <em>{E(it['kind'])} · {it['year']}</em>{pdfa}</span></header>
<div class="stage"><div id="book"><div class="pg L"></div><div class="pg R"></div><i class="spine"></i></div></div>
<div class="bctl"><button id="pv" aria-label="이전">‹</button><span id="cnt"></span><button id="nx" aria-label="다음">›</button></div>
<p class="bhint">클릭 · 방향키 · 스와이프로 넘기기</p>
<script>window.BOOK={cfg};</script><script>{BOOKJS}</script>
</body></html>""")

# ---- Process page
SRC = os.path.dirname(__file__)
LABS = {
  'plan': dict(no='01', cat='PLANNING', t='평면 대안 생성기', js='lab_plan.js',
    d='실 6개의 면적 · 채광 · 인접 조건에 가중치를 주고, 평면 대안 수백 개 중 기준을 넘으면서 서로 다른 안만 골라낸다.',
    long='실 6개를 대지에 나눠 넣는 평면을 수백 개 만들고, 형태 · 채광(남쪽) · 인접 · 현관(북쪽) 점수에 가중치를 곱해 합산한다. 기준 점수를 넘으면서 서로 충분히 다른 안만 위에 남는다.',
    body='<div class="lbody"><div class="lctl"></div><div class="lout"><p class="lsum"></p><div class="lhist"></div><div class="lpick"></div><p class="k">점수순 상위 96개 · 흐린 칸은 기준 미달, 테두리는 선택된 안</p><div class="lgrid"></div></div></div>'),
  'northlight': dict(no='02', cat='REGULATION', en='NORTH SETBACK ENVELOPE', ko='정북 일조사선 매스', t='정북 일조사선 매스', js='lab_northlight.js',
    d='대지 꼭짓점을 끌면 정북 일조사선 · 대지안의 공지 · 건폐율 · 용적률로 허용 볼륨과 실제 가능한 연면적이 바로 나온다.',
    long='전용 · 일반주거지역에서는 정북 방향 경계로부터 높이 10m까지는 1.5m, 그 위로는 높이의 절반만큼 떨어져야 한다(건축법 시행령 제86조). 대지 모양을 직접 그리면 이 사선과 건폐율 · 용적률을 함께 걸어, 어느 법규가 연면적을 결정하는지 보여 준다. 도로 사선 · 높이 제한 완화 등은 반영하지 않은 스터디용 계산이다.'),
  'frame': dict(no='03', cat='STRUCTURE', en='STRUCTURAL GRID → FRAME', ko='구조 그리드 · 골조', t='구조 그리드 → 골조', js='lab_frame.js',
    d='그리드 축선을 끌어 스팬을 바꾸면 기둥 · 보 · 슬래브 분해 아이소와 개략 부재 크기 · 물량이 바로 나온다.',
    long='평면에서 축선을 끌어 스팬을 바꾸고, 구조 방식과 층수를 고르면 골조가 층별로 분해된 아이소로 그려진다. 보 춤은 스팬비, 기둥은 가장 큰 부담 면적의 축력으로 잡은 계획 단계 개략치다. 스팬과 기둥 수, 보 춤 사이의 맞바꿈을 눈으로 확인하는 도구.'),
  'stair': dict(no='04', cat='CIRCULATION', en='STAIR DESIGN', ko='계단 설계', t='계단 설계', js='lab_stair.js',
    d='층고를 끌면 단 수 · 단높이 · 디딤판 · 계단참이 다시 잡히고 용도별 법규 OK/NG가 나온다.',
    long='층고와 용도를 정하면 단높이를 목표값 이하로 맞춰 단 수를 정하고, 보행 공식(2R+T ≈ 63cm)으로 단너비를 잡는다. 3m마다 계단참, 용도별 단높이 · 단너비 · 폭 기준(피난·방화구조 규칙 제15조 등)을 함께 판정하고 계단실 크기를 낸다.'),
  'catenary': dict(no='07', cat='FORM FINDING', en='FORM FINDING', ko='현수선 형태 찾기', t='현수선 형태 찾기', js='lab_catenary.js',
    d='그물을 대지 경계에 매달아 자중으로 늘어뜨린 뒤 뒤집어, 압축만 받는 흙 셸을 얻는다.',
    long='대지 경계를 지점으로 삼아 그물을 매달고 힘 밀도법으로 반복 이완해 자중에 늘어진 형태를 찾는다. 이를 뒤집으면 같은 하중에 압축만 받는 셸이 된다. 지점과 천창을 옮기면 형태가 다시 계산되고, 셸 면적 · 흙 물량 · 무게가 나온다. MOSSCAPE 흙 셸을 찾을 때 쓴 방법이다.'),
  'eave': dict(no='08', cat='SIGHT · WIND', en='EAVE · SIGHT · WIND', ko='처마와 시선 · 바람', t='처마와 시선 · 바람', js='lab_eave.js',
    d='해측 처마 높이와 지붕 경사를 바꾸면 앉은 눈높이에서 하늘이 잘리는 각, 남는 바다 띠, 작업 자리 천장고, 처마 끝 바람이 함께 바뀐다.',
    long='굴 작업은 몇 시간씩 앉아 손끝을 보는 일이라, 시야에 밝은 하늘이 들어오면 눈이 부시다. 처마 끝과 눈을 잇는 선으로 하늘이 잘리는 각을 구하고, 안벽 모서리까지의 선으로 바다가 보이는 띠를 구한다. 처마를 낮출수록 바람을 받는 높이도 내려가지만 작업 자리의 천장고가 모자라지므로 경사와 자리를 함께 조정한다. 비어가는 마을 굴막 단면을 정할 때 쓴 논리다.'),
  'office': dict(no='09', cat='DAYLIGHT · ENERGY', en='DAYLIGHT · HEAT', ko='오피스 빛 · 열', t='오피스 빛 · 열', js='lab_office.js',
    d='방위 · 창 면적비 · 평면 깊이 · 차양 · 유리를 바꾸면 주광률 분포와 주광 영역, 여름 시간별 냉방 부하, 겨울 난방 부하가 다시 계산된다.',
    long='창을 키우면 안쪽까지 밝아지지만 일사로 냉방 피크가 오른다. 단면에서는 BRE 평균 주광률식으로 깊이별 주광률과 DF 2% 이상인 주광 영역을, 오른쪽에서는 서울 7월 맑은 날의 태양 위치로 창면 일사와 차양 그림자를 30분마다 구해 일사 · 전도 · 내부 발열 부하를 쌓는다. 오피스 평면 깊이와 입면 창 비율을 정할 때 쓰는 판단이다.'),
  'parking': dict(no='05', cat='OPTIMIZATION', en='PARKING LAYOUT', ko='주차 배치', t='주차 배치', js='lab_parking.js',
    d='대지 꼭짓점을 끌면 주차 모듈을 36개 각도로 깔아 보고 가장 많이 들어가는 배치와 법정 대수 충족 여부가 나온다.',
    long='직각주차 모듈(구획 + 차로 + 구획)을 5° 간격 36개 각도, 오프셋, 세로 연결 차로 위치를 바꿔 가며 깔아 보고 가장 많이 들어가는 안을 고른다. 오른쪽 그래프는 각도별 최대 대수이고, 막대를 누르면 그 각도의 배치를 볼 수 있다. 용도별 시설면적으로 법정 대수와 비교한다.'),
  'sun': dict(no='06', cat='SIMULATION', en='SOLAR ACCESS', ko='동지 일조 시간', t='동지 일조 시간', js='lab_sun.js',
    d='건물을 끌어 옮기면 대지 1m 격자마다 동지 09~15시 연속 일조 시간과 시각별 그림자가 다시 계산된다.',
    long='위도와 날짜로 태양 위치를 구하고, 1m 격자마다 해 쪽으로 광선을 쏘아 건물에 막히는지 10분 간격으로 확인한다. 왼쪽은 09~15시 연속 일조 시간 지도와 2시간 경계선, 오른쪽은 선택 시각의 그림자와 태양 궤적이다. 배치 단계에서 동 간격과 높이를 정할 때 쓴다.'),
}
STEPT = {}
def lab_page(k):
    L = LABS[k]; st = L['stage']
    head = f'<section class="lab" id="lab-{k}"><div class="lh"><p class="k"><a href="../process.html">← AI와 설계하기</a> · LAB {L["no"]} · {L["cat"]}</p><h3>{E(L["t"])}</h3><p>{E(L["long"])}</p></div>'
    body = head + L.get('body', '<div class="app"></div>') + '</section>'
    js = open(os.path.join(SRC, 'lab_ui.js')).read() + open(os.path.join(SRC, L['js'])).read()
    open(f'{OUT}/lab/{k}.html', 'w').write(page(f'LAB {L["no"]} {L["t"]} — {SITE["name_ko"]}', body + f'<script>{js}</script>', '../', dark='dark labpg', on='p', desc=L['d']))
CARDS = ['eave', 'office', 'catenary', 'northlight', 'sun', 'parking', 'frame', 'stair']
def process_page():
    P = PROCESS
    os.makedirs(f'{OUT}/lab', exist_ok=True)
    for k, L in LABS.items():
        L.setdefault('stage', '00'); lab_page(k)
    cards = ''.join(f'''<article class="acard lab" id="lab-{k}"><header><b>{E(LABS[k]["en"])}</b><span>{E(LABS[k]["ko"])}</span><a href="lab/{k}.html" title="크게 열기 · 조절하기">↗</a></header><div class="app"></div></article>''' for k in CARDS)
    js = open(os.path.join(SRC, 'lab_ui.js')).read() + ''.join(open(os.path.join(SRC, LABS[k]['js'])).read() for k in CARDS)
    DEMO = "\n// 카드 자동 시연: 보이는 카드만 매개변수가 혼자 움직이고, 누르면 멈추고 직접 조절\n(function(){var still=matchMedia('(prefers-reduced-motion:reduce)').matches,vis=new Set(),cards=[].slice.call(document.querySelectorAll('.acard.lab'));\nvar io=new IntersectionObserver(function(es){es.forEach(function(e){e.isIntersecting?vis.add(e.target):vis.delete(e.target);});},{rootMargin:'80px'});\ncards.forEach(function(c){io.observe(c);var app=c.querySelector('.app'),h=c.querySelector('header'),b=document.createElement('button');b.type='button';b.className='dmo';h.insertBefore(b,h.querySelector('a'));c._t=0;\n function set(m){c.dataset.mode=m;c.classList.toggle('live',m==='live');b.innerHTML=m==='live'?'<i>▶</i> 자동 재생':'<i></i> 자동 재생 중 · 눌러서 직접 조절';if(m==='live'&&app.demo)app.demo.stop();}\n set(still||!app.demo?'live':'auto');\n app.addEventListener('pointerdown',function(){if(c.dataset.mode==='auto')set('live');},true);\n b.addEventListener('click',function(){set(c.dataset.mode==='live'?'auto':'live');});});\nif(still)return;var last=0;function loop(ts){requestAnimationFrame(loop);var dt=ts-last;if(dt<40)return;last=ts;dt=Math.min(dt,100)/1000;\n cards.forEach(function(c){var a=c.querySelector('.app');if(c.dataset.mode!=='auto'||!vis.has(c)||!a.demo)return;c._t+=dt;a.demo.step(c._t);});}\nrequestAnimationFrame(loop);})();\n"
    body = f'''<section class="phd"><p class="k">LAB — 설계를 스킬로</p><h1>{E(P["title"])}<small>{E(P["sub"])}</small></h1><p class="lead">{E(P["lead"])}</p></section>
<section class="agrid">{cards}</section><script>{js}{DEMO}</script>'''
    open(f'{OUT}/process.html', 'w').write(page(f'Process — {SITE["name_ko"]}', body, '', dark='dark labpg', on='p', desc=P['lead']))
process_page()
