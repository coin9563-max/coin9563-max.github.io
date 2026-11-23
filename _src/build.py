# -*- coding: utf-8 -*-
"""정적 사이트 생성기: python3 build.py <이미지폴더> <출력폴더>
이미지폴더에는 <id>.jpg (포트폴리오 asset) 와 pg_<id>.jpg (페이지 렌더)가 있어야 함."""
import os, sys, shutil, html, json
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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Noto+Serif+KR:wght@500&display=swap');
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
.bookpg .bt{font-size:14px;font-weight:600}.bookpg .bt em{font-style:normal;font-weight:400;color:var(--mute);margin-left:.6em}
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
.nls .hi b{color:#b6d36b}
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
.cvf{grid-column:1/-1;display:flex;justify-content:space-between;font-size:13px;color:var(--mute)}.cvf a{color:inherit}
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
@media (max-width:760px){.shelf{grid-template-columns:1fr;gap:10vh}}

/* ===== Practice: 원장 */
.ledpg{--bg:#f4f3ef;--fg:#111;--mute:#7b7a75;--line:#111}
.ledh{max-width:var(--max);margin:12vh auto 0}
.ledh h1{font-size:clamp(48px,8vw,124px);font-weight:600;letter-spacing:-.045em;line-height:.95;margin:16px 0 8vh}
.lcol,.lr{display:grid;grid-template-columns:150px 1.3fr 1fr 30px;gap:24px;align-items:baseline}
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
@media (max-width:760px){.lcol{display:none}.lr{grid-template-columns:70px 1fr 20px}.lr .r{grid-column:2}.lr .go{grid-row:1;grid-column:3}.lpv{display:none}}
"""

JS = r"""
(function(){var m=document.querySelector('.cvm');if(!m)return;var bg=document.querySelectorAll('.cv0 .bg'),a=m.querySelectorAll('a');
a.forEach(function(x,i){x.addEventListener('mouseenter',function(){bg.forEach(function(b,k){b.classList.toggle('on',k===i)});m.classList.add('hov');a.forEach(function(o){o.classList.toggle('on',o===x)});});});
m.addEventListener('mouseleave',function(){bg.forEach(function(b,k){b.classList.toggle('on',k===0)});m.classList.remove('hov');a.forEach(function(o){o.classList.remove('on')});});})();
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
"""

def page(title, body, root, dark=False, on='', desc='', og='img/t_307.jpg'):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or SITE['name_ko']+' — 건축 포트폴리오')}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc or '')}">
<link rel="stylesheet" href="{root}style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect width=%2232%22 height=%2232%22 fill=%22%231d1c1a%22/%3E%3Ctext x=%2216%22 y=%2222%22 font-size=%2216%22 text-anchor=%22middle%22 fill=%22%23f6f5f2%22 font-family=%22sans-serif%22%3EH%3C/text%3E%3C/svg%3E">
<meta property="og:image" content="https://coin9563-max.github.io/{og}">
</head><body class="{dark if isinstance(dark, str) else ('dark' if dark else '')}">
<header class="top"><a class="name" href="{root}index.html">{SITE['name_ko']}<span>{SITE['name_en']}</span></a>
<nav><a href="{root}projects.html" class="{'on' if on=='w' else ''}">Projects</a><a href="{root}publish.html" class="{'on' if on=='b' else ''}">Publish</a><a href="{root}practice.html" class="{'on' if on=='r' else ''}">Practice</a><a href="{root}process.html" class="{'on' if on=='p' else ''}">Process</a><a href="{root}about.html" class="{'on' if on=='a' else ''}">About</a><a href="{root}about.html#contact">Contact</a></nav></header>
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
        out.append(f'''<a class="bk" href="publish/{it["slug"]}.html"><div class="obj"><img src="{s_}" width="{w}" height="{h}" alt="{E(it["title"])}"><i></i></div>
<div class="meta"><span>{E(it["kind"])} · {it["year"]}</span><b>{E(it["title"])}</b><em>{E(it.get("desc",""))}</em><u>펼쳐 읽기 →</u></div></a>''')
    return ''.join(out)
body = f'''<section class="shelfh"><p class="pk">02 — Publish</p><h1>Books</h1><p>졸업전시를 위해 만든 책 두 권. 표지를 누르면 실제 책처럼 넘겨 볼 수 있다.</p></section><section class="shelf">{shelf()}</section>'''
open(f'{OUT}/publish.html', 'w').write(page(f'Publish — {SITE["name_ko"]}', body, '', dark='pubpg', on='b'))

# ---- Practice: 원장(Ledger)
def ledger():
    rows=[]
    for i in PRACTICE:
        if i.get('hide_in_list'): continue
        if i.get('slug'):
            s_,w,h=use(i['thumb'],thumb=True)
            rows.append(f'''<a class="lr f" href="practice/{i["slug"]}.html" data-img="{s_}"><span class="y">{E(i["year"])}</span><span class="t"><b>{E(i["title"])}</b><small>{E(i.get("org") or i["kind"])}</small></span><span class="r">{E(i.get("role") or i["kind"])}</span><span class="go">→</span></a>''')
        else:
            rows.append(f'''<div class="lr"><span class="y">{E(i["year"])}</span><span class="t"><b>{E(i.get("org") or i["title"])}</b><small>{E(i["title"] if i.get("org") and i["title"]!=i["org"] else i["kind"])}</small></span><span class="r">{E(i.get("role") or i["kind"])}</span><span class="go"></span></div>''')
    return ''.join(rows)
body = f'''<section class="ledh"><p class="pk">03 — Practice &amp; Activities</p><h1>Practice<br>&amp; Activities</h1><div class="lcol"><span>Year</span><span>Project · Office</span><span>Role</span></div></section><section class="ledger">{ledger()}</section><img class="lpv" alt="">'''
open(f'{OUT}/practice.html', 'w').write(page(f'Practice — {SITE["name_ko"]}', body, '', dark='ledpg', on='r'))

# ---- 표지
def cover():
    feat=[i for i in PRACTICE if i.get('slug')]
    items=[('01','Projects','projects.html',f'설계 작업 {len(PROJECTS)}',use(PROJECTS[0]['hero'],thumb=True)[0]),
           ('02','Publish','publish.html',f'책 {len(PUBLISH)}',use(PUBLISH[0]['img'],thumb=True)[0]),
           ('03','Practice','practice.html',f'실무 · 활동 {len(PRACTICE)}',use(feat[0]['thumb'],thumb=True)[0] if feat else ''),
           ('04','Process','process.html','AI와 설계하기',''),
           ('05','About','about.html','소개 · 연락처','')]
    li=''.join(f'<li><a href="{h}" data-bg="{b}"><span class="n">{n}</span><span class="w">{t}</span><span class="c">{c}</span></a></li>' for n,t,h,c,b in items)
    return f'''<section class="cv0"><div class="bgs">{"".join(f'<div class="bg{" on" if k==0 else ""}" style="background-image:url({b})"></div>' if b else '<div class="bg grid"></div>' for k,(*_,b) in enumerate(items))}</div>
<div class="cvh"><p>Portfolio 2021–2026</p><h1>{SITE["name_ko"]}<span>{SITE["name_en"]}</span></h1><p class="tag">{E(ABOUT.get("intro") or "")}</p></div>
<ol class="cvm">{li}</ol><p class="cvf"><a href="mailto:{SITE["email"]}">{SITE["email"]}</a><span>{SITE["school"]}</span></p></section>'''
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
src, w, h = use(405)
body = f'''<section class="about"><div><img src="{src}" width="{w}" height="{h}" alt="D5 Render 공개 강연"></div>
<div><h1>{SITE["name_ko"]}<small>{SITE["name_en"]} · {SITE["school"]}</small></h1>{lead}
{f'<h3>Areas of Interest</h3><p>{E(A["interests"])}</p>' if A.get("interests") else ''}<h3 id="contact">Contact</h3><table><tr><td>E-mail</td><td><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></td></tr><tr><td>Phone</td><td><a href="tel:{SITE["phone"].replace('-','')}">{SITE["phone"]}</a></td></tr></table>
<h3>Education</h3>{tbl(A["education"])}
<h3>Experience</h3>{tbl(A["experience"])}
<h3>Awards &amp; Activities</h3>{tbl(A["activities"])}
<h3>Skills</h3><table>{"".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a,b in A["skills"])}</table>
</div></section>'''
open(f'{OUT}/about.html', 'w').write(page(f'About — {SITE["name_ko"]}', body, '', on='a'))
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
    cfg=json.dumps(dict(n=len(files), ar=round(w/h,4), dir=f'../book/{it["slug"]}/', back='../publish.html'))
    open(f'{OUT}/publish/{it["slug"]}.html','w').write(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(it['title'])} — {SITE['name_ko']}</title>
<meta name="description" content="{E(it['desc'])}"><meta property="og:title" content="{E(it['title'])}">
<meta property="og:image" content="https://coin9563-max.github.io/book/{it['slug']}/01.jpg">
<link rel="stylesheet" href="../style.css"></head>
<body class="dark bookpg">
<header class="top"><a class="name" href="../publish.html">← {SITE['name_ko']}<span>Publish</span></a><span class="bt">{E(it['title'])} <em>{E(it['kind'])} · {it['year']}</em></span></header>
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
}
STEPT = {}
def lab_page(k):
    L = LABS[k]; st = L['stage']
    head = f'<section class="lab" id="lab-{k}"><div class="lh"><p class="k"><a href="../process.html">← AI와 설계하기</a> · LAB {L["no"]} · {L["cat"]}</p><h3>{E(L["t"])}</h3><p>{E(L["long"])}</p></div>'
    body = head + L.get('body', '<div class="app"></div>') + '</section>'
    js = open(os.path.join(SRC, 'lab_ui.js')).read() + open(os.path.join(SRC, L['js'])).read()
    open(f'{OUT}/lab/{k}.html', 'w').write(page(f'LAB {L["no"]} {L["t"]} — {SITE["name_ko"]}', body + f'<script>{js}</script>', '../', dark='dark labpg', on='p', desc=L['d']))
CARDS = ['northlight', 'frame']
def process_page():
    P = PROCESS
    os.makedirs(f'{OUT}/lab', exist_ok=True)
    for k, L in LABS.items():
        L.setdefault('stage', '00'); lab_page(k)
    cards = ''.join(f'''<article class="acard lab" id="lab-{k}"><header><b>{E(LABS[k]["en"])}</b><span>{E(LABS[k]["ko"])}</span><a href="lab/{k}.html" title="크게 열기 · 조절하기">↗</a></header><div class="app"></div></article>''' for k in CARDS)
    js = open(os.path.join(SRC, 'lab_ui.js')).read() + ''.join(open(os.path.join(SRC, LABS[k]['js'])).read() for k in CARDS)
    body = f'''<section class="phd"><p class="k">LAB — 설계를 스킬로</p><h1>{E(P["title"])}<small>{E(P["sub"])}</small></h1><p class="lead">{E(P["lead"])}</p></section>
<section class="agrid">{cards}</section><script>{js}</script>'''
    open(f'{OUT}/process.html', 'w').write(page(f'Process — {SITE["name_ko"]}', body, '', dark='dark labpg', on='p', desc=P['lead']))
process_page()
