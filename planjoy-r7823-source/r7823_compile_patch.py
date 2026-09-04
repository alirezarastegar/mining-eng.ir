from pathlib import Path

ROOT = Path('android_native/app/src/main/java/com/planjoy/r7')

def replace_once(path: Path, old: str, new: str):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly one match, found {count}: {old!r}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

app = ROOT / 'AppUi.kt'
r78 = ROOT / 'R78Features.kt'
r72 = ROOT / 'R72Features.kt'

replace_once(app, 'private object CutePalette {', 'object CutePalette {')
replace_once(app, '@Composable private fun Focus(c:Context,f:Boolean)=R78FocusScreen(c,f)\n', '')
replace_once(r78, 'import java.time.LocalDate\n', 'import java.time.Instant\nimport java.time.LocalDate\n')

old_art = 'listOf(R.drawable.pj_original_focus_scene,R.drawable.pj_original_task_ducks,R.drawable.pj_original_today_header,R.drawable.pj_original_task_ducks)'
new_art = 'listOf(R.drawable.pj_priority_clock_duck,R.drawable.pj_priority_focus_duck,R.drawable.pj_priority_first_plan,R.drawable.pj_priority_analysis)'
text = r72.read_text(encoding='utf-8')
count = text.count(old_art)
if count != 2:
    raise SystemExit(f'{r72}: expected two priority artwork lists, found {count}')
r72.write_text(text.replace(old_art, new_art), encoding='utf-8')

print('R7.8.23 compile patch applied: CutePalette visibility, Instant import, obsolete Focus wrapper removed, four unique priority artworks bound.')
