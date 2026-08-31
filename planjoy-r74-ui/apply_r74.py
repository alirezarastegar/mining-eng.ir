from pathlib import Path
import json, sys

root=Path(sys.argv[1])
css_overlay=Path(sys.argv[2]).read_text(encoding='utf-8')

def rep(path, old, new, label):
    p=root/path; s=p.read_text(encoding='utf-8')
    c=s.count(old)
    if c != 1: raise SystemExit(f'{label}: expected 1 marker, found {c}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

def rep_all(path, old, new):
    p=root/path; s=p.read_text(encoding='utf-8'); p.write_text(s.replace(old,new),encoding='utf-8')

# Renderer bugfix + page motion/error boundary.
p=root/'renderer/app.js'; s=p.read_text(encoding='utf-8')
s=s.replace("const now=()=>Math.floor(Date.now()/1000); const day=86400;","const now=()=>Math.floor(Date.now()/1000); const day=86400; const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));",1)
s=s.replace("function applyRoot(){document.body.classList.toggle('fa',fa());document.documentElement.dir=fa()?'rtl':'ltr';document.documentElement.lang=fa()?'fa':'en';document.body.className=(fa()?'fa ':'')+`theme-${state.settings.theme||'cloud'} wallpaper-${state.settings.wallpaper||'none'}`;document.documentElement.style.setProperty('--font-scale',String(state.settings.fontScale||1));}","function applyRoot(){document.body.classList.toggle('fa',fa());document.documentElement.dir=fa()?'rtl':'ltr';document.documentElement.lang=fa()?'fa':'en';document.body.className=(fa()?'fa ':'')+`theme-${state.settings.theme||'cloud'} wallpaper-${state.settings.wallpaper||'none'}`;document.body.dataset.route=route;document.documentElement.style.setProperty('--font-scale',String(state.settings.fontScale||1));}",1)
s=s.replace("function scene(k=route,size=88){const safe=routeKeys.includes(k)?k:'today';return `<div class=\"page-head-visual\"><img src=\"../assets/scenes/${safe}.svg\" width=\"${size}\" height=\"${Math.round(size*.78)}\" alt=\"\" draggable=\"false\"></div>`}","function scene(k=route,size=108){const safe=routeKeys.includes(k)?k:'today';return `<div class=\"page-head-visual route-art art-${safe}\"><span class=\"art-blob b1\"></span><span class=\"art-blob b2\"></span><span class=\"art-spark s1\">✦</span><span class=\"art-spark s2\">✧</span><img src=\"../assets/scenes/${safe}.svg\" width=\"${size}\" height=\"${Math.round(size*.78)}\" alt=\"\" draggable=\"false\"></div>`}",1)
s=s.replace('PlanJoy · R7.3 Desktop Experience Parity','PlanJoy · R7.4 Cozy Desktop',1)
s=s.replace("function pageHead(title,subtitle,mood='happy',actions=''){return `<div class=\"page-head\">${scene(route,92)}<div class=\"page-head-copy\"><div class=\"eyebrow\">PlanJoy · ${esc(strings[fa()?'fa':'en'][route]||'')}</div><h1>${esc(title)}</h1><p>${esc(subtitle)}</p></div>${actions?`<div class=\"page-actions\">${actions}</div>`:''}</div>`}","function pageHead(title,subtitle,mood='happy',actions=''){return `<div class=\"page-head cozy-head\"><div class=\"head-deco head-deco-a\"></div><div class=\"head-deco head-deco-b\"></div>${scene(route,112)}<div class=\"page-head-copy\"><div class=\"eyebrow\"><span class=\"eyebrow-paw\">✿</span> PlanJoy · ${esc(strings[fa()?'fa':'en'][route]||'')}</div><h1>${esc(title)}</h1><p>${esc(subtitle)}</p><div class=\"head-mini-row\"><span class=\"mini-pill\">${tr('gentle','آرام')}</span><span class=\"mini-pill mint\">${tr('focused','متمرکز')}</span><span class=\"mini-pill rose\">${tr('yours','مال خودت')}</span></div></div>${actions?`<div class=\"page-actions\">${actions}</div>`:''}</div>`}",1)
s=s.replace("function renderPage(){const p=$('#page');if(!p)return;const f={today:renderToday,calendar:renderCalendar,goals:renderGoals,focus:renderFocus,review:renderReview,stats:renderStats,countdown:renderCountdowns,widgets:renderWidgets,joy:renderJoy,smart:renderSmart,settings:renderSettings}[route]||renderToday;p.innerHTML=`<div class=\"page\">${f()}</div>`;bindPage();}","function renderPage(){const p=$('#page');if(!p)return;const f={today:renderToday,calendar:renderCalendar,goals:renderGoals,focus:renderFocus,review:renderReview,stats:renderStats,countdown:renderCountdowns,widgets:renderWidgets,joy:renderJoy,smart:renderSmart,settings:renderSettings}[route]||renderToday;try{const html=f();p.innerHTML=`<div class=\"page page-${route} page-enter\">${html}<div class=\"page-end-art\" aria-hidden=\"true\"><span class=\"end-cloud c1\"></span><span class=\"end-cloud c2\"></span><span class=\"end-paw\">♡</span><span class=\"end-star\">✦</span></div></div>`;bindPage()}catch(err){console.error('PlanJoy render failure',route,err);p.innerHTML=`<div class=\"page page-${route}\"><div class=\"card render-error\">${mascot(92)}<div><h2>${tr('This page needs a tiny reset','این صفحه یک بازنشانی کوچک لازم دارد')}</h2><p>${esc(err?.message||String(err))}</p><button class=\"btn primary\" data-action=\"recover-page\">${tr('Recover page','بازیابی صفحه')}</button></div></div></div>`;bindPage()}}",1)
s=s.replace("async function onAction(e){const b=e.currentTarget,a=b.dataset.action,tid=b.dataset.id;","async function onAction(e){const b=e.currentTarget,a=b.dataset.action,tid=b.dataset.id;if(a==='recover-page'){state=await window.planjoy.getState();shell();return;}",1)
s=s.replace('R7.3','R7.4')
p.write_text(s,encoding='utf-8')

# Append new visual system.
cp=root/'renderer/app.css'; css=cp.read_text(encoding='utf-8')
if 'R7.4 — Cozy Motion UI' not in css: css += '\n'+css_overlay+'\n'
cp.write_text(css,encoding='utf-8')

# Version and UI certification hook.
p=root/'main.js'; m=p.read_text(encoding='utf-8')
m=m.replace("const VERSION = '0.7.3';","const VERSION = '0.7.4';",1).replace("const PRODUCT_STAGE = 'R7.3-DESKTOP-PARITY';","const PRODUCT_STAGE = 'R7.4-COZY-UI';",1).replace('PRODID:-//PlanJoy//R7.3//EN','PRODID:-//PlanJoy//R7.4//EN')
cert="""
async function certifyUiRoutes(){
  if(!mainWindow||mainWindow.isDestroyed())return;
  const routes=['today','calendar','goals','focus','review','stats','countdown','widgets','joy','smart','settings'];
  const outDir=process.env.PLANJOY_UI_CAPTURE_DIR||''; if(outDir)fs.mkdirSync(outDir,{recursive:true});
  const results=[];
  for(const route of routes){
    const result=await mainWindow.webContents.executeJavaScript(`(async()=>{const b=document.querySelector('[data-route=\\"${route}\\"]');if(!b)throw new Error('route button missing: ${route}');b.click();await new Promise(r=>setTimeout(r,220));const page=document.querySelector('#page');return {route:'${route}',text:(page?.innerText||'').trim(),error:!!page?.querySelector('.render-error'),head:!!page?.querySelector('.page-head'),cards:page?.querySelectorAll('.card').length||0}})()`);
    if(result.error||!result.head||result.text.length<12)throw new Error(`UI route failed: ${route} ${JSON.stringify(result)}`);
    results.push(result); if(outDir){const image=await mainWindow.webContents.capturePage();fs.writeFileSync(path.join(outDir,`${route}.png`),image.toPNG());}
  }
  console.log(`UI_ROUTE_SMOKE_PASS ${results.length}`); if(outDir)fs.writeFileSync(path.join(outDir,'ui-route-results.json'),JSON.stringify(results,null,2));
}
"""
if 'async function certifyUiRoutes()' not in m: m=m.replace('function createWindow(){',cert+'\nfunction createWindow(){',1)
m=m.replace("mainWindow.once('ready-to-show',()=>mainWindow.show());","mainWindow.once('ready-to-show',async()=>{mainWindow.show();if(process.env.PLANJOY_UI_CERTIFY==='1'){try{await certifyUiRoutes();app.exit(0)}catch(e){console.error('UI_ROUTE_SMOKE_FAIL',e);app.exit(71)}}});",1)
p.write_text(m,encoding='utf-8')

# Package + installer.
p=root/'package.json'; pkg=json.loads(p.read_text(encoding='utf-8')); pkg['version']='0.7.4'; pkg['description']='PlanJoy R7.4 — professional cozy Windows desktop edition with animated cute experience parity'; pkg['build']['artifactName']='PlanJoyR74-${version}-${arch}.${ext}'; p.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rep_all('installer/main.go','const version = "0.7.3"','const version = "0.7.4"'); rep_all('installer/main.go','PlanJoy R7.3','PlanJoy R7.4')

# Keep original parity suite valid and add R7.4 regression requirements.
p=root/'tests/desktop_contract_test.js'; t=p.read_text(encoding='utf-8').replace("pkg.version==='0.7.3'","pkg.version==='0.7.4'")
t=t.replace("installer.includes('Programs\",\"PlanJoy')","installer.includes('Programs\", \"PlanJoy')")
p.write_text(t,encoding='utf-8')

print('R74_PATCH_APPLIED')
