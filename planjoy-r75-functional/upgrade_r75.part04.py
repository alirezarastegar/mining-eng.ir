
# Expand the Windows widget family to cover the observed PlanJoy widget categories independently.
widget_cards=r'''function widgetCards(){const g=currentGoal(),today=todayTasks(),allOpen=state.tasks.filter(t=>!t.completed).sort((a,b)=>(a.startUtc||0)-(b.startUtc||0)),next=allOpen[0],cd=state.countdowns.slice().sort((a,b)=>a.targetUtc-b.targetUtc)[0],latest=state.reviews.slice().sort((a,b)=>b.dateKey.localeCompare(a.dateKey))[0],done=completedToday().length,total=Math.max(1,today.length+done),mood=['','😞','🙁','😐','🙂','😄'][clamp(latest?.mood||3,1,5)],q=[1,2,3,4].map(n=>state.tasks.filter(t=>!t.completed&&(t.quadrant||2)===n).length),weekFocus=focusMinutes(7),monthOpen=state.tasks.filter(t=>!t.completed&&t.startUtc>=now()&&t.startUtc<=now()+31*day).length,goalMiles=g?state.milestones.filter(m=>m.goalId===g.id):[],reviewText=(latest?.diary||latest?.title||tr('No review yet','هنوز مروری نیست')).slice(0,64),fortune=tr('Small steps count.','قدم‌های کوچک هم حساب می‌شوند.');return [
['today',tr('Today plans','برنامه‌های امروز'),`${digits(today.length)} ${tr('plans','برنامه')}`,today[0]?.title||tr('A calm day','یک روز آرام'),`✓ ${digits(done)}`],
['next',tr('Next plan','برنامه بعدی'),next?fmtTime(next.startUtc):'—',next?.title||tr('Nothing queued','چیزی در صف نیست'),next?fmtDate(next.startUtc,true):'—'],
['focus',tr('Focus today','تمرکز امروز'),`${digits(focusMinutes(1))} ${tr('min','دقیقه')}`,tr('today','امروز'),'25 · 45 · 60'],
['focusweek',tr('Focus week','تمرکز هفتگی'),`${digits(weekFocus)} ${tr('min','دقیقه')}`,`${digits(state.focusSessions.filter(x=>x.endedUtc>=now()-7*day).length)} ${tr('sessions','جلسه')}`,tr('last 7 days','۷ روز گذشته')],
['goal',tr('Goal','هدف'),`${digits(g?.progress||0)}%`,g?.title||tr('No active goal','بدون هدف فعال'),`${digits(goalMiles.filter(m=>m.completed).length)}/${digits(goalMiles.length)} ${tr('milestones','مایلستون')}`],
['countdown',tr('Countdown','شمارش‌معکوس'),cd?`${digits(Math.ceil((cd.targetUtc-now())/day))} ${tr('days','روز')}`:'—',cd?.title||tr('No countdown','موردی نیست'),fmtDate(cd?.targetUtc||0,true)],
['calendar',tr('Calendar','تقویم'),fmtDate(now(),true),`${digits(today.length)} ${tr('today','امروز')}`,state.settings.calendar],
['week',tr('Week planner','برنامه هفته'),`${digits(state.tasks.filter(t=>!t.completed&&t.startUtc>=now()-day&&t.startUtc<=now()+7*day).length)} ${tr('plans','برنامه')}`,tr('Next 7 days','۷ روز آینده'),tr('weekly overview','نمای هفتگی')],
['month',tr('Month planner','برنامه ماه'),`${digits(monthOpen)} ${tr('plans','برنامه')}`,fmtDate(now(),false),tr('next 31 days','۳۱ روز آینده')],
['quadrant',tr('Quadrant','چهارخانه'),`Q1 ${digits(q[0])} · Q2 ${digits(q[1])}`,`Q3 ${digits(q[2])} · Q4 ${digits(q[3])}`,tr('priority map','نقشه اولویت')],
['mood',tr('Mood','حال‌وهوا'),mood,latest?.title||tr('No check-in yet','هنوز ثبت نشده'),latest?.dateKey||'—'],
['review',tr('Daily review','مرور روز'),mood,reviewText,latest?.dateKey||'—'],
['stats',tr('Statistics','آمار'),`${digits(Math.round(done/total*100))}%`,tr('completion today','تکمیل امروز'),`${digits(weekFocus)}m focus`],
['joy','JOY',`Lv ${digits(state.joy.level||1)} · ${digits(state.joy.coins||0)}◇`,`${digits(state.joy.energy||0)}% ${tr('energy','انرژی')}`,state.joy.mood||'happy'],
['clock',tr('Cozy clock','ساعت کیوت'),fmtTime(now()),fmtDate(now(),true),tr('local time','زمان محلی')],
['fortune',tr('Tiny note','یادداشت کوچک'),'✦',fortune,tr('a gentle nudge','یک یادآوری دوستانه')]
]}
'''
app=replace_function(app,'widgetCards',widget_cards.rstrip())

render_widget=r'''function renderWidget(){applyRoot();const type=widgetMode,cards=widgetCards(),row=cards.find(x=>x[0]===type)||cards[0],[k,h,v,n,meta]=row;let extra='';if(k==='quadrant'){const q=[1,2,3,4].map(x=>(state.tasks||[]).filter(t=>!t.completed&&(t.quadrant||2)===x).length);extra=`<div class="widget-mini-grid">${q.map((x,i)=>`<span>Q${i+1}: ${digits(x)}</span>`).join('')}</div>`}if(k==='week'||k==='focusweek'){const days=[0,1,2,3,4,5,6].map(off=>{const d=new Date();d.setDate(d.getDate()+off);return k==='week'?(state.tasks||[]).filter(t=>!t.completed&&sameDateSec(t.startUtc,d)).length:Math.round((state.focusSessions||[]).filter(x=>sameDateSec(x.endedUtc,d)).reduce((s,x)=>s+(x.actualSeconds||0),0)/60)});extra=`<div class="widget-mini-grid">${days.map((x,i)=>`<span>+${i} · ${digits(x)}</span>`).join('')}</div>`}if(k==='month'){const weeks=[0,1,2,3].map(w=>(state.tasks||[]).filter(t=>!t.completed&&t.startUtc>=now()+w*7*day&&t.startUtc<now()+(w+1)*7*day).length);extra=`<div class="widget-mini-grid">${weeks.map((x,i)=>`<span>W${i+1} · ${digits(x)}</span>`).join('')}</div>`}if(k==='today'){const list=todayTasks().slice(0,3);extra=list.length?`<div class="widget-mini-grid">${list.map(t=>`<span>${esc(t.title)}</span>`).join('')}</div>`:''}const privacy=state.settings.widgetPrivacy;$('#app').innerHTML=`<div class="widget-shell"><div class="widget-card widget-${esc(k)}"><div class="widget-drag"></div><button class="widget-close" data-widget-close>×</button><h3>PlanJoy · ${esc(h)}</h3><div class="widget-big">${esc(privacy?'•••':v)}</div><div class="widget-note">${esc(privacy?tr('Details hidden','جزئیات مخفی است'):n)}</div>${privacy?'':extra}<div class="widget-note">${esc(meta||'')}</div></div></div>`;$('[data-widget-close]')?.addEventListener('click',()=>window.close())}
'''
app=replace_function(app,'renderWidget',render_widget.rstrip())

old="  const allowed=['today','focus','goal','countdown','calendar','week','quadrant','mood','stats','joy']; if(!allowed.includes(type))return false;"
new="  const allowed=['today','next','focus','focusweek','goal','countdown','calendar','week','month','quadrant','mood','review','stats','joy','clock','fortune']; if(!allowed.includes(type))return false;"
if old not in main: raise RuntimeError('openWidget allowed list marker missing')
main=main.replace(old,new,1)
main=main.replace("if(count!==10)throw new Error(`widget gallery count ${count}`);","if(count!==16)throw new Error(`widget gallery count ${count}`);",1)
main=main.replace("const widgetTypes=['today','focus','goal','countdown','calendar','week','quadrant','mood','stats','joy'];","const widgetTypes=['today','next','focus','focusweek','goal','countdown','calendar','week','month','quadrant','mood','review','stats','joy','clock','fortune'];",1)

old_widget_assert="ok(main.includes(\"['today','focus','goal','countdown','calendar','week','quadrant','mood','stats','joy']\"),'ten widgets');"
new_widget_assert="ok(main.includes(\"['today','next','focus','focusweek','goal','countdown','calendar','week','month','quadrant','mood','review','stats','joy','clock','fortune']\"),'sixteen widgets');"
if old_widget_assert in test:
    test=test.replace(old_widget_assert,new_widget_assert,1)

test=test.replace("console.log(`DESKTOP_CONTRACT_PASS ${pass}`);","ok(app.includes(\"['month',tr('Month planner'\"),'month planner widget');ok(app.includes(\"['focusweek',tr('Focus week'\"),'weekly focus widget');ok(main.includes(\"'clock','fortune'\"),'extended widget process allowlist');\nconsole.log(`DESKTOP_CONTRACT_PASS ${pass}`);",1)

(root/'renderer/app.js').write_text(app)
(root/'main.js').write_text(main)
(root/'tests/desktop_contract_test.js').write_text(test)
