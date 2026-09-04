from pathlib import Path

p = Path("android_native/app/src/main/java/com/planjoy/r7/R7826Parity.kt")
s = p.read_text(encoding="utf-8")

old_header = '        PageHeader(fa,r7826tr(fa,"Calendar","تقویم"),r7826tr(fa,"Tap any active date to see or add its plans — the same flow as Windows.","روی هر تاریخ فعال بزن؛ برنامه‌های همان روز را ببین یا مستقیم اضافه کن."),CatMood.CALM)\n'
new_header = '        R7826PageHeader(fa,r7826tr(fa,"Calendar","تقویم"),r7826tr(fa,"Tap any active date to see or add its plans — the same flow as Windows.","روی هر تاریخ فعال بزن؛ برنامه‌های همان روز را ببین یا مستقیم اضافه کن."))\n'
if old_header in s:
    s = s.replace(old_header, new_header, 1)
elif new_header not in s:
    raise SystemExit("R7.8.26 calendar header target not found")

start_marker = '@Composable private fun R7826WidgetPreview'
end_marker = '\n@Composable fun R7826WidgetStore'
start = s.find(start_marker)
end = s.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("R7.8.26 widget preview block not found")

replacement = '''@Composable private fun R7826PageHeader(fa:Boolean,title:String,subtitle:String){
    Column(Modifier.fillMaxWidth(), verticalArrangement=Arrangement.spacedBy(3.dp)){
        Text(title,style=MaterialTheme.typography.headlineSmall,fontWeight=FontWeight.ExtraBold)
        Text(subtitle,style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable private fun R7826WidgetPreview(c:Context,fa:Boolean,s:R7826WidgetSpec){
    val d=R7826WidgetRuntime.data(c,s.id)
    Surface(
        Modifier.width(190.dp).height(220.dp),
        shape=androidx.compose.foundation.shape.RoundedCornerShape(20.dp),
        color=when(s.bg){
            R.drawable.widget_ref_yellow_bg->Color(0xFFFFF2B6)
            R.drawable.widget_ref_blue_bg->Color(0xFFBFE8FF)
            R.drawable.widget_ref_pink_bg->Color(0xFFFFC2D9)
            R.drawable.widget_ref_green_bg->Color(0xFFDDEEBB)
            R.drawable.widget_ref_beige_bg->Color(0xFFF5EBDD)
            else->Color(0xFFFFFDFB)
        },
        border=BorderStroke(2.dp,Color(0xFF34343A))
    ){
        Box(Modifier.fillMaxSize().padding(12.dp)){
            if(s.fresh){
                Surface(
                    Modifier.align(Alignment.TopStart),
                    color=Color(0xFFFF5B5B),
                    shape=androidx.compose.foundation.shape.RoundedCornerShape(5.dp)
                ){
                    Text("NEW",Modifier.padding(horizontal=6.dp,vertical=3.dp),fontSize=9.sp,color=Color.White,fontWeight=FontWeight.ExtraBold)
                }
            }
            Column(
                Modifier.fillMaxSize(),
                horizontalAlignment=Alignment.CenterHorizontally,
                verticalArrangement=Arrangement.SpaceBetween
            ){
                Row(Modifier.fillMaxWidth()){
                    Text(if(fa)s.fa else s.en,Modifier.weight(1f),fontWeight=FontWeight.Bold,fontSize=12.sp)
                    Text("♛",color=Color(0xFFD7AC00))
                }
                Image(painterResource(s.art),null,Modifier.fillMaxWidth().height(78.dp),contentScale=ContentScale.Fit)
                Text(d.value,fontSize=29.sp,fontWeight=FontWeight.ExtraBold)
                Text(d.hint,fontSize=10.sp,textAlign=TextAlign.Center,maxLines=2)
                if(d.progress>=0) LinearProgressIndicator(progress={d.progress/100f},Modifier.fillMaxWidth())
                Text(d.meta,fontSize=9.sp,color=MaterialTheme.colorScheme.onSurfaceVariant,maxLines=1)
            }
        }
    }
}
'''

s = s[:start] + replacement + s[end:]
p.write_text(s, encoding="utf-8")
print("R7.8.26 compile fix applied: self-contained calendar header and balanced widget preview")
