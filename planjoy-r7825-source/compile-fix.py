from pathlib import Path

# 1) Close the R7.8.25 settings data branch before the sync section.
p = Path("android_native/app/src/main/java/com/planjoy/r7/AppUi.kt")
s = p.read_text(encoding="utf-8")
old = 'if(msg.isNotBlank())Text(msg,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)}\n            9->{'
new = 'if(msg.isNotBlank())Text(msg,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)}}\n            9->{'
if old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
elif new not in s:
    raise SystemExit("R7.8.25 compile-fix target not found")

# 2) Migrate the inherited 57-check static contract from R7.8.24 semantics.
t = Path("android_native/tests/r7821_android_static_contract.py")
x = t.read_text(encoding="utf-8")
x = (x.replace("versionCode\\s*=\\s*78024", "versionCode\\s*=\\s*78025")
       .replace('versionName="0.7.8+24"', 'versionName="0.7.8+25"')
       .replace('VERSION="0.7.8+24"', 'VERSION="0.7.8+25"')
       .replace('VERSION_CODE=78024', 'VERSION_CODE=78025')
       .replace('R7.8.24-MOBILE-UI-RESTORE-REWARD-PARITY', 'R7.8.25-SETTINGS-NAV-LANGUAGE-POLISH')
       .replace("'R78ExtendedSettings(a,f,cal,includeProfile=false)' in app and 'R78ProfileSettings' in r78",
                "'Language & calendar' in app and 'SettingsChoice(cal==1' in app and 'SettingsChoice(cal==0' in app and 'SettingsChoice(cal==2' in app and 'R78ProfileSettings' in r78"))
t.write_text(x, encoding="utf-8")
print("R7.8.25 compile/static-contract migration applied")
