from pathlib import Path
import re

root = Path('android_native/app/src/main/java/com/planjoy/r7')

p = root / 'AppUi.kt'
s = p.read_text(encoding='utf-8')
if 'import androidx.compose.foundation.BorderStroke' not in s:
    s = s.replace('import androidx.compose.foundation.Canvas\n', 'import androidx.compose.foundation.BorderStroke\nimport androidx.compose.foundation.Canvas\n')
p.write_text(s, encoding='utf-8')

p = root / 'R7824OriginalParity.kt'
s = p.read_text(encoding='utf-8')
if 'import androidx.compose.foundation.verticalScroll' not in s:
    s = s.replace('import androidx.compose.foundation.rememberScrollState\n', 'import androidx.compose.foundation.rememberScrollState\nimport androidx.compose.foundation.verticalScroll\n')

marker = '        item{if(rev<0)Text("")}\n'
if marker in s and '        }\n' + marker not in s:
    s = s.replace(marker, '        }\n' + marker, 1)

stripped = re.sub(r'"(?:\\.|[^"\\])*"', '', s)
if stripped.count('{') - stripped.count('}') == 1:
    s = s.rstrip() + '\n}\n'

p.write_text(s, encoding='utf-8')

# Fail closed if the structural fixes did not land.
assert 'import androidx.compose.foundation.BorderStroke' in (root/'AppUi.kt').read_text(encoding='utf-8')
final = p.read_text(encoding='utf-8')
assert 'import androidx.compose.foundation.verticalScroll' in final
stripped = re.sub(r'"(?:\\.|[^"\\])*"', '', final)
assert stripped.count('{') == stripped.count('}'), 'R7824OriginalParity.kt brace imbalance'
print('R7.8.24 final compile fix applied')
