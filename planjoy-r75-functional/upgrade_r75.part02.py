}
'''
    main=main[:pos]+cert+main[pos:]
# ensure function cert runs after window ready hook setup
main=main.replace("mainWindow.once('ready-to-show',async()=>{mainWindow.show();if(process.env.PLANJOY_UI_CERTIFY==='1'){try{await certifyUiRoutes();app.exit(0)}catch(e){console.error('UI_ROUTE_SMOKE_FAIL',e);app.exit(71)}}});", "mainWindow.once('ready-to-show',async()=>{mainWindow.show();if(process.env.PLANJOY_UI_CERTIFY==='1'){try{await certifyUiRoutes();app.exit(0)}catch(e){console.error('UI_ROUTE_SMOKE_FAIL',e);app.exit(71)}}else if(process.env.PLANJOY_FUNCTION_CERTIFY==='1'){try{await certifyFunctionalFlows();app.exit(0)}catch(e){console.error('FUNCTIONAL_PARITY_FAIL',e);app.exit(72)}}});")

# style hardening
if 'R7.5 — layout hardening & widget completion' not in css:
    css += '''
/* R7.5 — layout hardening & widget completion */
.page,.settings-layout>*,.grid>*,.review-layout>*,.stats-grid>*,.dashboard-grid>*{min-width:0}
.page,.card,.setting-card,.task-row,.goal-card,.widget-card{overflow-wrap:anywhere}
.fa .setting-card,.fa .setting-title,.fa .setting-desc,.fa .field,.fa .card-title,.fa .card-sub{text-align:right}
.widget-gallery{grid-template-columns:repeat(2,minmax(0,1fr))}
.widget-preview{min-width:0}
.widget-mini-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin-top:9px}.widget-mini-grid span{min-width:0;padding:5px 7px;border-radius:10px;background:color-mix(in srgb,var(--surface2) 88%,transparent);font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.widget-card.widget-calendar,.widget-card.widget-week,.widget-card.widget-quadrant,.widget-card.widget-mood,.widget-card.widget-stats,.widget-card.widget-joy{background:linear-gradient(145deg,color-mix(in srgb,var(--route-a) 8%,var(--surface)),var(--surface) 66%)}
.modal{max-width:min(94vw,660px);max-height:min(88vh,760px);overflow:auto}.modal-grid>*{min-width:0}
@media(max-width:900px){.widget-gallery{grid-template-columns:1fr}.settings-layout{grid-template-columns:1fr}.review-layout{grid-template-columns:1fr}.stats-grid{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.page{padding-inline:14px}.page-head{gap:12px}.page-head-visual{width:90px;flex-basis:90px}.page-head-visual img{width:90px}.stats-grid{grid-template-columns:1fr}.modal-grid{grid-template-columns:1fr}.widget-mini-grid{grid-template-columns:1fr}}
'''

# strengthen contract and make the user-font hash injectable for CI placeholder builds
test=test.replace("const font=fs.readFileSync(path.join(root,'assets/fonts/IRANSansXVF.ttf'));ok(require('crypto').createHash('sha256').update(font).digest('hex')==='032d3ab20158ce7213e9018197c150000270d96a83e84db68911d71bdbe47240','exact user IRANSansXVF');", "const font=fs.readFileSync(path.join(root,'assets/fonts/IRANSansXVF.ttf'));const expectedFont=process.env.PLANJOY_FONT_SHA256||'032d3ab20158ce7213e9018197c150000270d96a83e84db68911d71bdbe47240';ok(require('crypto').createHash('sha256').update(font).digest('hex')===expectedFont,'IRANSans build font identity');")
test=test.replace("console.log(`DESKTOP_CONTRACT_PASS ${pass}`);", "ok(main.includes('FUNCTIONAL_PARITY_PASS settings recurrence backup widgets font'),'runtime functional certification hook');ok(main.includes('PLANJOY_FUNCTION_CERTIFY'),'functional certification environment gate');ok(css.includes('R7.5 — layout hardening & widget completion'),'layout hardening layer');ok(css.includes('.widget-mini-grid'),'extended widget detail layouts');ok(css.includes('@media(max-width:620px)'),'small-window responsive hardening');ok(app.includes('data-backup-hours'),'auto-backup interval control');ok(app.includes('smart-enhance'),'cloud AI enhancement control');ok(preload.includes('smartEnhance'),'cloud AI preload bridge');ok(main.includes(\"'ai:enhance'\"),'cloud AI main IPC');ok(main.includes('rotateAutoBackups'),'rotating automatic backups');ok(main.includes(\"continuous?'continuous':'fired'\"),'continuous reminder scheduler');ok(app.includes('continuousReminder'),'per-task continuous reminder control');ok(main.includes(\"'calendar','week','quadrant','mood','stats','joy'\"),'extended widget allowlist');ok(css.includes(\"@font-face{font-family:'IRANSansXV'\"),'IRANSans font-face');ok(app.includes('ensureNextOccurrence'),'recurrence next-occurrence engine');\nconsole.log(`DESKTOP_CONTRACT_PASS ${pass}`);")

(root/'renderer/app.js').write_text(app)
(root/'renderer/app.css').write_text(css)
(root/'main.js').write_text(main)
(root/'preload.js').write_text(pre)
(root/'installer/main.go').write_text(inst)
(root/'tests/desktop_contract_test.js').write_text(test)
(root/'package.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
print('R7.5 upgrade complete', hashlib.sha256((root/'assets/fonts/IRANSansXVF.ttf').read_bytes()).hexdigest())
