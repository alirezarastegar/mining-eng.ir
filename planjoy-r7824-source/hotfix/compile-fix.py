from pathlib import Path
root=Path('android_native/app/src/main/java/com/planjoy/r7')
app=root/'AppUi.kt'
r72=root/'R72Features.kt'

s=app.read_text()
old='''            items(entries){x->val selected=current==x;Surface(Modifier.fillMaxWidth().clickable{onGo(x)},shape=RoundedCornerShape(16.dp),color=if(selected)MaterialTheme.colorScheme.secondaryContainer else Color.Transparent){Row(Modifier.padding(horizontal=10.dp,vertical=8.dp),verticalAlignment=Alignment.CenterVertically){if(x in listOf(S.TODAY,S.CALENDAR,S.FOCUS,S.WIDGETS,S.SETTINGS))PrimaryTabIcon(x,selected) else Box(Modifier.size(38.dp),contentAlignment=Alignment.Center){Canvas(Modifier.size(23.dp)){drawSecondaryTabIcon(if(selected)MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onSurfaceVariant,x)}};Spacer(Modifier.width(10.dp));Text(name(x,fa),fontWeight=if(selected)FontWeight.Bold else FontWeight.Medium)}}}'''
new='''            items(entries){x->
                val selected=current==x
                val secondaryIconColor=if(selected)MaterialTheme.colorScheme.onSecondaryContainer else MaterialTheme.colorScheme.onSurfaceVariant
                Surface(Modifier.fillMaxWidth().clickable{onGo(x)},shape=RoundedCornerShape(16.dp),color=if(selected)MaterialTheme.colorScheme.secondaryContainer else Color.Transparent){
                    Row(Modifier.padding(horizontal=10.dp,vertical=8.dp),verticalAlignment=Alignment.CenterVertically){
                        if(x in listOf(S.TODAY,S.CALENDAR,S.FOCUS,S.WIDGETS,S.SETTINGS))PrimaryTabIcon(x,selected)
                        else Box(Modifier.size(38.dp),contentAlignment=Alignment.Center){Canvas(Modifier.size(23.dp)){drawSecondaryTabIcon(secondaryIconColor,x)}}
                        Spacer(Modifier.width(10.dp));Text(name(x,fa),fontWeight=if(selected)FontWeight.Bold else FontWeight.Medium)
                    }
                }
            }'''
if old in s:
    s=s.replace(old,new,1)
elif 'val secondaryIconColor=' not in s:
    raise SystemExit('AppUi drawer target not found')
app.write_text(s)

s=r72.read_text()
if 'import androidx.compose.ui.graphics.StrokeCap' not in s:
    marker='import androidx.compose.ui.graphics.Path\n'
    if marker not in s: raise SystemExit('R72 import marker missing')
    s=s.replace(marker,marker+'import androidx.compose.ui.graphics.StrokeCap\n',1)
r72.write_text(s)
print('R7.8.24 compile hotfix applied')
