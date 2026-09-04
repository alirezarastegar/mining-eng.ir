from pathlib import Path
import shutil

# Close the R7.8.25 settings data branch before the sync section.
p = Path("android_native/app/src/main/java/com/planjoy/r7/AppUi.kt")
s = p.read_text(encoding="utf-8")
old = 'if(msg.isNotBlank())Text(msg,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)}\n            9->{'
new = 'if(msg.isNotBlank())Text(msg,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)}}\n            9->{'
if old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
elif new not in s:
    raise SystemExit("R7.8.25 compile-fix target not found")

# Replace the inherited R7821/R7823 static contract with the canonical
# R7.8.25 57-check regression contract that is also used locally.
src = Path("planjoy-r7825-source/r7821_android_static_contract.py")
dst = Path("android_native/tests/r7821_android_static_contract.py")
if not src.is_file():
    raise SystemExit("canonical R7.8.25 static contract missing")
shutil.copyfile(src, dst)
print("R7.8.25 compile fix + canonical 57-check static contract applied")
