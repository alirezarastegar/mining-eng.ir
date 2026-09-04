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

# 2) Migrate inherited 57-check static contract from either R7.8.23 or R7.8.24 semantics.
t = Path("android_native/tests/r7821_android_static_contract.py")
x = t.read_text(encoding="utf-8")
for old_code in ("78023", "78024"):
    x = x.replace(f"versionCode\\s*=\\s*{old_code}", "versionCode\\s*=\\s*78025")
    x = x.replace(f"VERSION_CODE={old_code}", "VERSION_CODE=78025")
for old_ver in ("0.7.8+23", "0.7.8+24"):
    x = x.replace(f'versionName="{old_ver}"', 'versionName="0.7.8+25"')
    x = x.replace(f'VERSION="{old_ver}"', 'VERSION="0.7.8+25"')
for old_stage in (
    'R7.8.23-WINDOWS-PARITY-INSTALL-SAFE',
    'R7.8.24-MOBILE-UI-RESTORE-REWARD-PARITY',
):
    x = x.replace(old_stage, 'R7.8.25-SETTINGS-NAV-LANGUAGE-POLISH')
x = x.replace(
    "'R78ExtendedSettings(a,f,cal,includeProfile=false)' in app and 'R78ProfileSettings' in r78",
    "'Language & calendar' in app and 'SettingsChoice(cal==1' in app and 'SettingsChoice(cal==0' in app and 'SettingsChoice(cal==2' in app and 'R78ProfileSettings' in r78"
)
t.write_text(x, encoding="utf-8")
print("R7.8.25 compile/static-contract migration applied for R7.8.23/R7.8.24 baselines")
