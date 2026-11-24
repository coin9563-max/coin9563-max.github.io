const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
await p.goto('file:///home/user/coin9563-max.github.io/projects.html');await p.waitForTimeout(600);
await p.addStyleTag({content:`body>*:not(.bst){display:none!important}html,body{background:radial-gradient(120% 90% at 30% 20%,#efebe3,#cfc8bb)!important}
.bst::before{display:none}.bst{background:radial-gradient(120% 90% at 30% 20%,#efebe3,#cbc3b5)!important;place-items:center!important;padding:0!important;perspective-origin:50% 0%!important}
.bsk{width:600px!important;transition:none!important}.bst.up .bsk{transform:translateY(-70px) rotateX(52deg) rotateZ(-18deg)!important}
.bsk .ly:first-child{box-shadow:inset 0 0 0 1px #6e3120,30px 60px 60px #0005!important}`});
await p.evaluate(()=>{BCard.el().classList.add('up')});await p.waitForTimeout(400);
await p.screenshot({path:'/home/user/coin9563-max.github.io/og-card.jpg',type:'jpeg',quality:88});await b.close();})();
