
# R7.5.1 interaction hardening: one delegated event layer survives all DOM re-renders.
start=app.index('function bindGlobal(){')
end=app.index('\nasync function persist', start)
delegated=r'''let delegatedEventsBound=false;
function bindGlobal(){
  if(delegatedEventsBound)return;
  delegatedEventsBound=true;
  document.addEventListener('click',async e=>{
    const routeBtn=e.target.closest?.('[data-route]');
    if(routeBtn){route=routeBtn.dataset.route;selectedTasks.clear();shell();return;}
    const viewBtn=e.target.closest?.('[data-view]');
    if(viewBtn){plannerView=viewBtn.dataset.view;renderPage();return;}
    const sectionBtn=e.target.closest?.('[data-settings-section]');
    if(sectionBtn){settingsSection=sectionBtn.dataset.settingsSection;renderPage();return;}
    const settingSwitch=e.target.closest?.('[data-setting-switch]');
    if(settingSwitch){toggleSetting(settingSwitch.dataset.settingSwitch);return;}
    const themeBtn=e.target.closest?.('[data-theme]');
    if(themeBtn){state.settings.theme=themeBtn.dataset.theme;persist();return;}
    const wallBtn=e.target.closest?.('[data-wallpaper]');
    if(wallBtn){state.settings.wallpaper=wallBtn.dataset.wallpaper;persist();return;}
    const langBtn=e.target.closest?.('[data-lang]');
    if(langBtn){state.settings.language=langBtn.dataset.lang;persist();return;}
    const calBtn=e.target.closest?.('[data-calendar]');
    if(calBtn){state.settings.calendar=calBtn.dataset.calendar;persist();return;}
    const widgetSize=e.target.closest?.('[data-widget-size]');
    if(widgetSize){state.settings.widgetSize=widgetSize.dataset.widgetSize;persist();return;}
    const dateBtn=e.target.closest?.('[data-date]');
    if(dateBtn){selectedDate=new Date(dateBtn.dataset.date);renderPage();return;}
    const actionBtn=e.target.closest?.('[data-action]');
    if(actionBtn){
      if(actionBtn.dataset.action==='modal-backdrop'&&e.target!==actionBtn)return;
      try{await onAction({currentTarget:actionBtn,target:e.target,preventDefault:()=>e.preventDefault(),stopPropagation:()=>e.stopPropagation()});}
      catch(err){console.error('PlanJoy action failure',actionBtn.dataset.action,err);toast(err?.message||String(err),'error');}
    }
  });
  document.addEventListener('input',e=>{
    const t=e.target;
    if(t.matches?.('[data-search]')){search=t.value;renderPage();queueMicrotask(()=>{const s=$('[data-search]');if(s){s.focus();s.setSelectionRange(s.value.length,s.value.length)}});return;}
    if(t.matches?.('[data-smart]')){smartText=t.value;renderPage();queueMicrotask(()=>{const x=$('[data-smart]');if(x){x.focus();x.setSelectionRange(x.value.length,x.value.length)}});return;}
    if(t.matches?.('[data-widget-opacity]')){state.settings.widgetOpacity=Number(t.value);persist(false);return;}
    if(t.matches?.('[data-font-scale]')){state.settings.fontScale=Number(t.value);persist(false);return;}
  });
  document.addEventListener('change',e=>{
    const t=e.target;
    if(t.matches?.('[data-backup-hours]')){state.settings.autoBackupHours=Number(t.value);persist();return;}
    if(t.matches?.('[data-ai-endpoint]')){state.settings.aiEndpoint=t.value.trim();persist();return;}
  });
  document.addEventListener('keydown',e=>{
    const t=e.target;
    if(t.matches?.('[data-quick-add]')&&e.key==='Enter'){e.preventDefault();quickAdd(t.value);}
  });
}
function bindPage(){
  $$('[draggable=true]').forEach(row=>{
    if(row.dataset.dragBound==='1')return;
    row.dataset.dragBound='1';
    row.addEventListener('dragstart',e=>{row.classList.add('dragging');e.dataTransfer.setData('text/plain',row.dataset.taskRow)});
    row.addEventListener('dragend',()=>row.classList.remove('dragging'));
    row.addEventListener('dragover',e=>e.preventDefault());
    row.addEventListener('drop',e=>{e.preventDefault();reorderTask(e.dataTransfer.getData('text/plain'),row.dataset.taskRow)});
  });
}
'''
app=app[:start]+delegated+app[end:]

# Shell navigation must update route/theme/direction classes before rebuilding the DOM.
shell_old="function shell(){\n  if(widgetMode)return renderWidget();"
shell_new="function shell(){\n  applyRoot();\n  if(widgetMode)return renderWidget();"
if shell_old in app:
    app=app.replace(shell_old,shell_new,1)
elif shell_new not in app:
    raise RuntimeError('shell root update marker missing')

# Functional runtime certification exercises the exact navigation and tabs reported broken on a real Windows machine.
if 'planner tab click failed' not in main:
    cert_start=main.index('async function certifyFunctionalFlows(){')
    old_exec="  const exec=code=>mainWindow.webContents.executeJavaScript(code,true);"
    safe_exec="  const exec=async code=>{const wrapped=`(async()=>{try{return {__pjok:true,value:await (async()=>{${code}})()}}catch(e){return {__pjok:false,error:String(e?.message||e),stack:String(e?.stack||'')}}})()`;const result=await mainWindow.webContents.executeJavaScript(wrapped,true);if(!result?.__pjok)throw new Error('renderer certification error '+JSON.stringify(result));return result.value};"
    if old_exec not in main: raise RuntimeError('functional exec helper missing')
    main=main.replace(old_exec,safe_exec,1)
    exec_pos=main.index('  const exec=async code=>',cert_start)
    exec_end=main.index('\n',exec_pos)+1
    nav_cert="""  // Real click navigation must survive repeated complete DOM re-renders.\n  const navigation=await exec(`let stage='start';try{stage='routes';const routes=['today','calendar','goals','focus','review','stats','countdown','widgets','joy','smart','settings'];for(const r of routes){stage='route:'+r;const b=document.querySelector('[data-route=\\\"'+r+'\\\"]');if(!b)throw new Error('route missing '+r);b.click();await new Promise(x=>setTimeout(x,90));const active=document.querySelector('[data-route=\\\"'+r+'\\\"].active');const page=document.querySelector('.page-'+r);if(!active||!page||document.body.dataset.route!==r)throw new Error('route click failed '+r)}stage='planner-open';document.querySelector('[data-route=\\\"today\\\"]').click();await new Promise(x=>setTimeout(x,90));for(const v of ['list','today','quadrant','timeline']){stage='planner:'+v;const b=document.querySelector('[data-view=\\\"'+v+'\\\"]');if(!b)throw new Error('planner tab missing '+v);b.click();await new Promise(x=>setTimeout(x,90));if(!document.querySelector('[data-view=\\\"'+v+'\\\"].active'))throw new Error('planner tab click failed '+v)}stage='settings-open';document.querySelector('[data-route=\\\"settings\\\"]').click();await new Promise(x=>setTimeout(x,100));for(const s of ['general','appearance','language','notifications','data','sync','privacy','updates']){stage='settings:'+s;const b=document.querySelector('[data-settings-section=\\\"'+s+'\\\"]');if(!b)throw new Error('settings tab missing '+s);b.click();await new Promise(x=>setTimeout(x,75));if(!document.querySelector('.settings-section[data-section=\\\"'+s+'\\\"].active'))throw new Error('settings tab click failed '+s)}stage='restore-list';document.querySelector('[data-route=\\\"today\\\"]').click();await new Promise(x=>setTimeout(x,90));document.querySelector('[data-view=\\\"list\\\"]')?.click();await new Promise(x=>setTimeout(x,90));return {ok:true,stage:'done'}}catch(e){return {ok:false,stage,error:String(e?.message||e),stack:String(e?.stack||'')}}`);if(!navigation?.ok)throw new Error('navigation certification failed '+JSON.stringify(navigation));\n"""
    main=main[:exec_end]+nav_cert+main[exec_end:]

# Recurrence certification must explicitly select the list view, because the user can leave the planner on any tab.
old_recur="await exec(`document.querySelector('[data-route=\\\"today\\\"]').click();await new Promise(r=>setTimeout(r,150));const row=[...document.querySelectorAll('[data-task-row]')].find(x=>x.dataset.taskRow==='${tid}');if(!row)throw new Error('cert recurrence row missing');row.querySelector('[data-action=\\\"toggle-task\\\"]').click();await new Promise(r=>setTimeout(r,220));return true`);"
new_recur="await exec(`document.querySelector('[data-route=\\\"today\\\"]').click();await new Promise(r=>setTimeout(r,100));document.querySelector('[data-view=\\\"list\\\"]')?.click();await new Promise(r=>setTimeout(r,100));const row=[...document.querySelectorAll('[data-task-row]')].find(x=>x.dataset.taskRow==='${tid}');if(!row)throw new Error('cert recurrence row missing');row.querySelector('[data-action=\\\"toggle-task\\\"]').click();await new Promise(r=>setTimeout(r,220));return true`);"
if old_recur in main:
    main=main.replace(old_recur,new_recur,1)

test=test.replace("console.log(`DESKTOP_CONTRACT_PASS ${pass}`);","ok(app.includes('delegatedEventsBound'),'delegated event layer');ok(app.includes(\"closest?.('[data-route]')\"),'delegated route click handling');ok(app.includes('function shell(){')&&app.includes('applyRoot();')&&app.includes('if(widgetMode)return renderWidget()'),'shell root route update');ok(main.includes('planner tab click failed'),'runtime planner tab click certification');ok(main.includes('settings tab click failed'),'runtime settings tab click certification');ok(main.includes('renderer certification error'),'functional renderer diagnostics');\nconsole.log(`DESKTOP_CONTRACT_PASS ${pass}`);",1)

(root/'renderer/app.js').write_text(app)
(root/'main.js').write_text(main)
(root/'tests/desktop_contract_test.js').write_text(test)
