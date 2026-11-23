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
"""

JS = r"""
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
</head><body class="{'dark' if dark else ''}">
<header class="top"><a class="name" href="{root}index.html">{SITE['name_ko']}<span>{SITE['name_en']}</span></a>
<nav><a href="{root}index.html#projects" class="{'on' if on=='w' else ''}">Projects</a><a href="{root}index.html#publish">Publish</a><a href="{root}index.html#practice">Practice</a><a href="{root}process.html" class="{'on' if on=='p' else ''}">Process</a><a href="{root}about.html" class="{'on' if on=='a' else ''}">About</a><a href="{root}index.html#contact">Contact</a></nav></header>
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
body = f'''<section class="ix" id="projects"><div class="ixh"><h1>{SITE["name_ko"]} <span>{SITE["name_en"]}</span></h1><p class="sub">Selected Works 2021–2026 · {SITE["school"]}</p><p class="lead">{E(ABOUT.get("intro") or "")}</p></div>
<ul class="ixl">{"".join(rows)}</ul><div class="stg">{"".join(pvs)}</div></section>
<div class="sec" id="publish"><h2>Publish</h2><span>출판 · 책자</span></div>{cardgrid(PUBLISH)}
<div class="sec" id="practice"><h2>Practice &amp; Activities</h2><span>인턴 · 대외활동</span></div>{practice()}
<section class="contact" id="contact"><div class="sec"><h2>Contact</h2><span>연락처</span></div><div class="ct"><a class="big" href="mailto:{SITE["email"]}">{SITE["email"]}</a><a class="big" href="tel:{SITE["phone"].replace('-','')}">{SITE["phone"]}</a><p>인턴, 협업, 포트폴리오 문의 모두 메일로 연락 주세요.</p></div></section>'''
open(f'{OUT}/index.html', 'w').write(page(f'{SITE["name_ko"]} — Portfolio', body, '', on='w'))

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
    nav += f'<a href="{prv["slug"]}.html"><span>← 이전</span>{E(prv["title"])}</a>' if prv else f'<a href="../index.html#{back}"><span>←</span>Index</a>'
    nav += f'<a href="{nxt["slug"]}.html"><span>다음 →</span>{E(nxt["title"])}</a>' if nxt else f'<a href="../index.html#{back}"><span>→</span>Index</a>'
    nav += '</nav>'
    og = use(p['hero'], thumb=True)[0] if p.get('hero') is not None else 'img/t_307.jpg'
    open(f'{OUT}/{folder}/{p["slug"]}.html', 'w').write(
        page(f'{p["title"]} — {SITE["name_ko"]}', head + blocks + nav, r, dark=p.get('dark', False), on='w', desc=p['statement'], og=og))

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
{f'<h3>Areas of Interest</h3><p>{E(A["interests"])}</p>' if A.get("interests") else ''}<h3>Contact</h3><table><tr><td>E-mail</td><td><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></td></tr><tr><td>Phone</td><td><a href="tel:{SITE["phone"].replace('-','')}">{SITE["phone"]}</a></td></tr></table>
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
    cfg=json.dumps(dict(n=len(files), ar=round(w/h,4), dir=f'../book/{it["slug"]}/', back='../index.html#publish'))
    open(f'{OUT}/publish/{it["slug"]}.html','w').write(f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(it['title'])} — {SITE['name_ko']}</title>
<meta name="description" content="{E(it['desc'])}"><meta property="og:title" content="{E(it['title'])}">
<meta property="og:image" content="https://coin9563-max.github.io/book/{it['slug']}/01.jpg">
<link rel="stylesheet" href="../style.css"></head>
<body class="dark bookpg">
<header class="top"><a class="name" href="../index.html#publish">← {SITE['name_ko']}<span>Publish</span></a><span class="bt">{E(it['title'])} <em>{E(it['kind'])} · {it['year']}</em></span></header>
<div class="stage"><div id="book"><div class="pg L"></div><div class="pg R"></div><i class="spine"></i></div></div>
<div class="bctl"><button id="pv" aria-label="이전">‹</button><span id="cnt"></span><button id="nx" aria-label="다음">›</button></div>
<p class="bhint">클릭 · 방향키 · 스와이프로 넘기기</p>
<script>window.BOOK={cfg};</script><script>{BOOKJS}</script>
</body></html>""")

# ---- Process page
def process_page():
    P = PROCESS
    stats = ''.join(f'<div><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in P['stats'])
    out = []
    for st in P['steps']:
        if st.get('note'):
            flow = '<ol class="flow">' + ''.join(f'<li><b>{E(a)}</b><span>{E(b)}</span></li>' for a, b in st['flow']) + '</ol>' if st.get('flow') else ''
            out.append(f'<aside class="pnote"><h3>{E(st["t"])}</h3>{flow}<ul>' + ''.join(f'<li>{E(x)}</li>' for x in st['items']) + '</ul></aside>')
            continue
        code = f'<pre class="code"><span class="f">{E(st["file"])}</span>{E(st["code"])}</pre>' if st.get('code') else f'<p class="f2">{E(st["file"])}</p>'
        fig = f'<figure class="pfig">{pic(st["img"], "", alt=st["cap"])}<figcaption>{E(st["cap"])}</figcaption></figure>' if st.get('img') else ''
        out.append(f'''<section class="pstep"><div class="ph"><span class="no">{st["no"]}</span><h2>{E(st["t"])}<small>{E(st["en"])}</small></h2></div>
<div class="pb"><div class="cmp"><div><h4>기존</h4><p>{E(st["before"])}</p></div><div class="ai"><h4>AI와 함께</h4><p>{E(st["ai"])}</p></div></div>
<p class="hm"><b>사람의 몫</b> {E(st["human"])}</p>{code}{fig}</div></section>''')
    body = f'''<section class="phd"><p class="k">Process</p><h1>{E(P["title"])}<small>{E(P["sub"])}</small></h1><p class="lead">{E(P["lead"])}</p><div class="stats">{stats}</div></section>{"".join(out)}'''
    open(f'{OUT}/process.html', 'w').write(page(f'Process — {SITE["name_ko"]}', body, '', on='p', desc=P['lead']))
process_page()
