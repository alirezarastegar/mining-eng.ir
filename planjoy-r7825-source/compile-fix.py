from pathlib import Path

p = Path("android_native/app/src/main/java/com/planjoy/r7/AppUi.kt")
s = p.read_text(encoding="utf-8")
old = 'if(msg.isNotBlank())Text(msg,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)}\n            9->{'
new = 'if(msg.isNotBlank())Text(msg,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)}}\n            9->{'
if old not in s:
    if new in s:
        print("R7.8.25 compile fix already applied")
        raise SystemExit(0)
    raise SystemExit("R7.8.25 compile-fix target not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("R7.8.25 compile fix applied: closed settings data branch before sync section")
