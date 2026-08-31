from pathlib import Path
import json, hashlib, shutil, sys
if len(sys.argv)!=3: raise SystemExit('usage: upgrade_r75.py <source-dir> <font-file>')
root=Path(sys.argv[1]).resolve(); font_src=Path(sys.argv[2]).resolve()
(root/'assets/fonts').mkdir(parents=True,exist_ok=True)
shutil.copyfile(font_src,root/'assets/fonts/IRANSansXVF.ttf')
app=(root/'renderer/app.js').read_text()
css=(root/'renderer/app.css').read_text()
main=(root/'main.js').read_text()
pre=(root/'preload.js').read_text()
inst=(root/'installer/main.go').read_text()
test=(root/'tests/desktop_contract_test.js').read_text()
pkg=json.loads((root/'package.json').read_text())

def rep(s,a,b,label):
    c=s.count(a)
    if c!=1: raise RuntimeError(f'{label}: expected 1 found {c}')
    return s.replace(a,b,1)

def replace_function(src,name,new):
    start=src.index('function '+name+'(')
    nxt=src.find('\nfunction ', start+10)
    if nxt<0: raise RuntimeError(f'no next function after {name}')
    return src[:start]+new+src[nxt:]

# versions
main=main.replace("const VERSION = '0.7.4';","const VERSION = '0.7.5';").replace("const PRODUCT_STAGE = 'R7.4-COZY-UI';","const PRODUCT_STAGE = 'R7.5-FUNCTIONAL-PARITY';").replace('R7.4//EN','R7.5//EN')
app=app.replace('PlanJoy · R7.4 Cozy Desktop','PlanJoy · R7.5 Functional Cozy Desktop')
inst=inst.replace('const version = "0.7.4"','const version = "0.7.5"').replace('PlanJoy R7.4','PlanJoy R7.5')
pkg['version']='0.7.5';pkg['description']='PlanJoy R7.5 — functional parity, complete desktop widgets, IRANSans Persian UI and cozy animated Windows edition';pkg['build']['artifactName']='PlanJoyR75-${version}-${arch}.${ext}'

# settings defaults
main=rep(main,"      widgetPrivacy:false, compactMode:false, autoBackup:true, autoBackupHours:24, lockMode:'off',\n      aiEnabled:false, aiConsent:false, aiEndpoint:'', updateManifest:'', syncConfigured:false","      widgetPrivacy:false, widgetSize:'medium', widgetOpacity:1, compactMode:false, autoBackup:true, autoBackupHours:24, lockMode:'off',\n      aiEnabled:false, aiConsent:false, aiEndpoint:'', updateManifest:'', syncConfigured:false",'settings defaults')
main=rep(main,"    diagnostics:{createdUtc:n,lastLaunchUtc:n,launchCount:0,migration:'none'}","    diagnostics:{createdUtc:n,lastLaunchUtc:n,launchCount:0,migration:'none',lastAutoBackupUtc:0,lastAutoBackupPath:''}",'diagnostics defaults')

# font and root classes
app=rep(app,"function applyRoot(){document.body.classList.toggle('fa',fa());document.documentElement.dir=fa()?'rtl':'ltr';document.documentElement.lang=fa()?'fa':'en';document.body.className=(fa()?'fa ':'')+`theme-${state.settings.theme||'cloud'} wallpaper-${state.settings.wallpaper||'none'}`;document.body.dataset.route=route;document.documentElement.style.setProperty('--font-scale',String(state.settings.fontScale||1));}","function applyRoot(){document.documentElement.dir=fa()?'rtl':'ltr';document.documentElement.lang=fa()?'fa':'en';document.body.className=[fa()?'fa':'',`theme-${state.settings.theme||'cloud'}`,`wallpaper-${state.settings.wallpaper||'none'}`,state.settings.compactMode?'compact-mode':''].filter(Boolean).join(' ');document.body.dataset.route=route;document.documentElement.style.setProperty('--font-scale',String(state.settings.fontScale||1));document.documentElement.style.setProperty('--widget-opacity',String(state.settings.widgetOpacity??1));}",'applyRoot')
if not css.startswith("@font-face{font-family:'IRANSansXV'"):
    css="@font-face{font-family:'IRANSansXV';src:url('../assets/fonts/IRANSansXVF.ttf') format('truetype');font-weight:100 900;font-style:normal;font-display:swap}\n"+css
css += "\nbody.fa{font-family:'IRANSansXV',Tahoma,'Segoe UI',sans-serif}\n"
css += '''\n/* R7.5 — Functional Parity UI */
.compact-mode .page{padding:16px 18px 72px}.compact-mode .card{border-radius:18px}.compact-mode .task-row{padding:9px 10px}.compact-mode .grid{gap:9px}.compact-mode .setting-card{padding:13px}.compact-mode .page-head{margin-bottom:11px}
.widget-card{opacity:var(--widget-opacity,1)}
.widget-card.widget-calendar .widget-big{font-size:24px}.widget-card.widget-week .widget-big{font-size:22px}.widget-card.widget-quadrant .widget-big{font-size:22px}.widget-card.widget-mood .widget-big{font-size:36px}.widget-card.widget-joy .widget-big{font-size:25px}.widget-card.widget-stats .widget-big{font-size:27px}
.widget-mini-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:5px;margin-top:8px}.widget-mini-grid span{background:var(--surface2);border-radius:9px;padding:5px;text-align:center;font-size:9px;color:var(--muted)}
.widget-toolbar{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0}.widget-size-chip{border:1px solid var(--border);background:var(--surface);padding:7px 10px;border-radius:999px;font-size:10px}.widget-size-chip.active{background:var(--primary);color:#fff;border-color:var(--primary)}
.setting-inline{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.setting-inline .select,.setting-inline .input{max-width:260px}
.inline-check{display:flex;align-items:center;gap:8px;padding:10px;border:1px solid var(--border);background:var(--surface2);border-radius:13px}.inline-check input{width:16px;height:16px;accent-color:var(--primary)}
body.fa input,body.fa textarea,body.fa select,body.fa button{font-family:'IRANSansXV',Tahoma,'Segoe UI',sans-serif}
'''

# recurrence helpers before renderSmart
smart_idx=app.index('function renderSmart(){')
helpers='''function repeatAdvance(t){const start=new Date((t.startUtc||now())*1000),end=new Date((t.endUtc||t.startUtc||now())*1000),duration=Math.max(60,Math.floor((end-start)/1000));const next=new Date(start),kind=t.repeat||'none';let occurrence=Number(t.occurrenceIndex||0)+1;if(kind==='daily')next.setDate(next.getDate()+1);else if(kind==='weekdays'){do{next.setDate(next.getDate()+1)}while(next.getDay()===0||next.getDay()===6)}else if(kind==='weekly')next.setDate(next.getDate()+7);else if(kind==='monthly')next.setMonth(next.getMonth()+1);else if(kind==='ebbinghaus'){const gaps=[1,2,4,7,15,30];if(occurrence>gaps.length)return null;next.setDate(next.getDate()+gaps[occurrence-1])}else return null;return {startUtc:Math.floor(next.getTime()/1000),endUtc:Math.floor(next.getTime()/1000)+duration,occurrenceIndex:occurrence}}
function ensureNextOccurrence(t){if(!t||!t.completed||!t.repeat||t.repeat==='none')return null;const adv=repeatAdvance(t);if(!adv)return null;const series=t.recurrenceId||t.id;if(state.tasks.some(x=>x.id!==t.id&&(x.recurrenceId||x.id)===series&&x.startUtc===adv.startUtc))return null;const next={...t,id:id('task_'),completed:false,completedUtc:0,startUtc:adv.startUtc,endUtc:adv.endUtc,deadlineUtc:adv.endUtc,recurrenceId:series,occurrenceIndex:adv.occurrenceIndex,sortOrder:Math.max(0,...state.tasks.map(x=>x.sortOrder||0))+10};state.tasks.push(next);return next}
'''
app=app[:smart_idx]+helpers+app[smart_idx:]
app=rep(app,"if(a==='toggle-task'){const t=state.tasks.find(x=>x.id===tid);if(t){t.completed=!t.completed;t.completedUtc=t.completed?now():0;if(t.completed){reward('complete','task',t.id,10,2);playSound('pop')} updateChallenges();persist()}}","if(a==='toggle-task'){const t=state.tasks.find(x=>x.id===tid);if(t){t.completed=!t.completed;t.completedUtc=t.completed?now():0;if(t.completed){reward('complete','task',t.id,10,2);playSound('pop');ensureNextOccurrence(t)} updateChallenges();persist()}}",'toggle repeat')
app=rep(app,"if(a==='batch-complete'){for(const x of state.tasks)if(selectedTasks.has(x.id)&&!x.completed){x.completed=true;x.completedUtc=now();reward('complete','task',x.id,10,2)}selectedTasks.clear();updateChallenges();persist()}","if(a==='batch-complete'){for(const x of [...state.tasks])if(selectedTasks.has(x.id)&&!x.completed){x.completed=true;x.completedUtc=now();reward('complete','task',x.id,10,2);ensureNextOccurrence(x)}selectedTasks.clear();updateChallenges();persist()}",'batch repeat')

# task modal and persistence
needle="<div class=\"field\"><label>${tr('Parent plan','برنامه مادر')}</label><select class=\"select\" name=\"parentId\"><option value=\"\">${tr('None','ندارد')}</option>${parents.map(x=>`<option value=\"${esc(x.id)}\" ${t.parentId===x.id?'selected':''}>${esc(x.title)}</option>`).join('')}</select></div></div><div class=\"modal-actions\">"
repl="<div class=\"field\"><label>${tr('Parent plan','برنامه مادر')}</label><select class=\"select\" name=\"parentId\"><option value=\"\">${tr('None','ندارد')}</option>${parents.map(x=>`<option value=\"${esc(x.id)}\" ${t.parentId===x.id?'selected':''}>${esc(x.title)}</option>`).join('')}</select></div><label class=\"inline-check full\"><input type=\"checkbox\" name=\"continuousReminder\" ${t.continuousReminder?'checked':''}><span><strong>${tr('Repeat reminder until I act','یادآوری را تا انجام کار تکرار کن')}</strong><br><small>${tr('Uses the global continuous reminder policy.','از سیاست سراسری یادآوری پیوسته استفاده می‌کند.')}</small></span></label></div><div class=\"modal-actions\">"
app=rep(app,needle,repl,'continuous modal')
app=rep(app,"continuousReminder:false,sortOrder:t?.sortOrder??(Math.max(0,...state.tasks.map(x=>x.sortOrder||0))+10)};","continuousReminder:!!$('.modal [name=continuousReminder]')?.checked,occurrenceIndex:t?.occurrenceIndex||0,sortOrder:t?.sortOrder??(Math.max(0,...state.tasks.map(x=>x.sortOrder||0))+10)};",'continuous save')

# widgets
