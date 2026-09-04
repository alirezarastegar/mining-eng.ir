#!/usr/bin/env python3
from pathlib import Path
import hashlib, re, sys
ROOT=Path(__file__).resolve().parents[1]
passed=[]
def ok(name, cond):
    if not cond:
        raise AssertionError(name)
    passed.append(name)
def read(rel): return (ROOT/rel).read_text(encoding='utf-8')
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()

gradle=read('app/build.gradle.kts')
core=read('app/src/main/java/com/planjoy/r7/R78Core.kt')
bi=read('app/src/main/java/com/planjoy/r7/BuildInfo.kt')
app=read('app/src/main/java/com/planjoy/r7/AppUi.kt')
date=read('app/src/main/java/com/planjoy/r7/R7821DatePicker.kt')
forms=read('app/src/main/java/com/planjoy/r7/R7821DateForms.kt')
r72=read('app/src/main/java/com/planjoy/r7/R72Features.kt')
r78=read('app/src/main/java/com/planjoy/r7/R78Features.kt')
stats=read('app/src/main/java/com/planjoy/r7/R7821FocusStats.kt')
wf=read('.github/workflows/r78-native.yml')
repro=read('tools/build_android_reproducible.sh')

ok('gradle-version-code', re.search(r'versionCode\s*=\s*78025',gradle) is not None)
ok('gradle-version-name', 'versionName="0.7.8+25"' in gradle)
ok('core-version', 'VERSION="0.7.8+25"' in core and 'VERSION_CODE=78025' in core)
ok('build-info-version', 'VERSION="0.7.8+25"' in bi and 'VERSION_CODE=78025' in bi)
ok('release-stage', 'R7.8.25-SETTINGS-NAV-LANGUAGE-POLISH' in bi)

kt='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'app/src/main/java').rglob('*.kt'))
for token in ['android.app.DatePickerDialog','MaterialDatePicker','CalendarView','android.widget.DatePicker']:
    ok('no-native-'+token.split('.')[-1], token not in kt)
ok('central-picker-field', 'fun R7821DateTimeField' in date)
ok('central-picker-dialog', 'fun R7821DateTimePickerDialog' in date)
ok('jalali-primary-mode', 'val primaryCal = if (cal == 0) 0 else 1' in date)
ok('jalali-saturday-first', 'listOf("ش","ی","د","س","چ","پ","ج")' in date and 'listOf("Sa","Su","Mo","Tu","We","Th","Fr")' in date)
ok('gregorian-sunday-first', 'listOf("ی","د","س","چ","پ","ج","ش")' in date and 'listOf("Su","Mo","Tu","We","Th","Fr","Sa")' in date)
ok('dual-secondary-date', 'if (cal == 2)' in date and 'Jalali.display(first, 0, fa)' in date)
ok('true-jalali-month-engine', 'Jalali.monthStart' in date and 'Jalali.monthLen' in date and 'Jalali.shiftMonth' in date)

ok('today-route-advanced', '@Composable private fun Today(c:Context,f:Boolean,cal:Int)=R72TodayScreen(c,f,cal)' in app)
ok('goals-route-r7821', 'S.GOALS->R7821GoalsScreen(a,fa,cal)' in app)
ok('stats-route-r7824', 'S.STATS->R7824FocusAnalyticsScreen(a,fa,cal)' in app)
ok('countdown-route-r7821', 'S.COUNTDOWN->R7821CountdownScreen(a,fa,cal)' in app)
ok('calendar-dual-jalali-primary', 'val primary=if(cal==2)1 else cal' in app)
ok('core-calendar-controls-week-order', 'val primary=if(calendar==2)1 else calendar' in core and 'if(primary==1)' in core)
ok('gregorian-fa-sunday-label', 'listOf("ی","د","س","چ","پ","ج","ش")' in core)
ok('onboarding-central-calendar', 'R78OnboardingGate(a,fa,cal)' in app and 'R7821DateTimeField' in r78)
ok('settings-central-calendar', 'Language & calendar' in app and 'SettingsChoice(cal==1' in app and 'SettingsChoice(cal==0' in app and 'SettingsChoice(cal==2' in app and 'R78ProfileSettings' in r78)

ok('task-original-bottom-sheet', 'ModalBottomSheet' in r72 and 'pj_original_task_ducks' in r72)
ok('task-start-end-central-picker', r72.count('R7821DateTimeField') >= 2)
ok('task-priority-matrix', 'matrixRows' in r72 and 'R784Priority.priorityForQuadrant(q)' in r72)
ok('task-reminder', 'reminderLead=lead' in r72)
ok('task-recurrence', 'recurrenceFrequency=rep' in r72)
ok('task-dual-source-jalali', 'sourceY=if(cal!=0)j.y else d.year' in r72)
ok('goal-date-pickers', forms.count('R7821DateTimeField') >= 4)
ok('goal-calendar-persisted', 'calendarSystem=cal' in forms)
ok('milestone-dual-source-jalali', 'sourceY=if(cal!=0)j.y else d.year' in forms)
ok('countdown-date-time-picker', 'Target date & time' in forms and 'R7821DateTimeField' in forms)

ok('focus-original-scene', 'pj_original_focus_scene' in r78)
ok('focus-25-minute-default', '25*60' in r78 or '1500' in r78 or 'presetSeconds:Int=1500' in r78)
ok('focus-large-timer', ('54.sp' in r78 or '66.sp' in r78) and '360f*pct' in r78)
ok('focus-intention', 'focus_intention' in r78)
ok('focus-session-persistence', 'FocusModel' in r78 and 'PlanJoyDb.get(c).save("focus"' in r78)
ok('focus-stats-real-db', 'db.rows("focus")' in stats and 'Codec.focus' in stats)
ok('focus-stats-today-donut', 'Today\'s focus' in stats and 'drawArc' in stats)
ok('focus-stats-category', 'Focus by category' in stats and 'categories.take(8)' in stats)
ok('focus-stats-weekly-trend', 'R7821WeeklyTrend' in stats)
ok('focus-stats-time-of-day', 'R7821TimeOfDay' in stats)

expected={
 'app/src/main/res/drawable/pj_original_today_header.png':'c73988887cf3f7033c6e51a5ec2e5af14d65524e4ce255ead4bd9a91633754fb',
 'app/src/main/res/drawable/pj_original_calendar.png':'e749941257577e20a6906e5352895fcb3fccbf674ad4215d4f3f8a7eef516cad',
 'app/src/main/res/drawable/pj_original_focus_scene.webp':'735973c5f01c88a6a85b81668e077e5aa39abdc11f523eb8628fb2745d8b9dc3',
 'app/src/main/res/drawable/pj_original_focus_stats.png':'746d865ed85ce0f9b6d60b790d2685e7e217e205de537c23d6e2eb12f4fb46b7',
 'app/src/main/res/drawable/pj_original_task_ducks.webp':'1eff77f0c7c065fd518e41116abf2377182d0d564aa165e8745cca90c60b1c48',
}
for rel,h in expected.items(): ok('exact-original-'+Path(rel).stem, (ROOT/rel).is_file() and sha(rel)==h)
ok('bounded-original-content-scale', 'ContentScale.Fit' in r72 and 'ContentScale.Fit' in r78 and 'ContentScale.Fit' in app)

raw_fonts=list(ROOT.rglob('*.ttf'))+list(ROOT.rglob('*.otf'))+list(ROOT.rglob('*.woff'))+list(ROOT.rglob('*.woff2'))
ok('iransans-font-resource', any(p.name=='iransans_xv.ttf' for p in raw_fonts) or 'R.font.iransans_xv' in app)
ok('iransans-source-binding', 'R.font.iransans_xv' in app)
keys=list(ROOT.rglob('*.p12'))+list(ROOT.rglob('*.jks'))+list(ROOT.rglob('*.keystore'))
ok('no-private-signing-key', not keys)
ok('workflow-baseline-artifact', 'PlanJoyR7823-Android-v0.7.8.23.apk' in wf and 'PlanJoy-R7823-Android-native' in wf)
ok('workflow-signer-gate', 'fd23be91dd847ae2046b1fb926001958fe5721ca1aa082e9ab8994e0eff68509' in wf)
ok('repro-baseline-artifact', 'PlanJoyR7823-Android-v0.7.8.23.apk' in repro and 'R7823_ANDROID_REPRODUCIBLE_PASS' in repro)

print(f'R7823_ANDROID_STATIC_CONTRACT_PASS {len(passed)}')
