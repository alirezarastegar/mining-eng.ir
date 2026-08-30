package com.planjoy.r7

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.media.MediaPlayer
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.Crossfade
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.res.fontResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID
import kotlin.math.max
import kotlin.math.min

private enum class Screen { TODAY, CALENDAR, GOALS, FOCUS, REVIEW, STATS, COUNTDOWN, WIDGETS, JOY, SMART, SETTINGS }
private enum class CalendarMode { GREGORIAN, JALALI, DUAL }

data class PTask(
    val id: String,
    val title: String,
    val done: Boolean = false,
    val epochDay: Long = LocalDate.now().toEpochDay(),
    val category: String = "Inbox",
    val priority: Int = 1,
    val note: String = "",
    val repeat: String = "None"
)

data class PGoal(val id: String, val title: String, val progress: Int = 0, val target: Int = 100)
data class PReview(val id: String, val epochDay: Long, val mood: Int, val note: String)
data class PCountdown(val id: String, val title: String, val targetEpochDay: Long, val style: Int = 0)

private class PStore(ctx: Context) {
    val p = ctx.getSharedPreferences("planjoy_r713", Context.MODE_PRIVATE)

    fun tasks(): List<PTask> = runCatching {
        val a = JSONArray(p.getString("tasks", "[]"))
        (0 until a.length()).map { i ->
            val o = a.getJSONObject(i)
            PTask(o.getString("id"), o.getString("title"), o.optBoolean("done"), o.optLong("day", LocalDate.now().toEpochDay()), o.optString("cat", "Inbox"), o.optInt("priority", 1), o.optString("note"), o.optString("repeat", "None"))
        }
    }.getOrDefault(emptyList())

    fun saveTasks(v: List<PTask>) {
        val a = JSONArray(); v.forEach { t -> a.put(JSONObject().put("id", t.id).put("title", t.title).put("done", t.done).put("day", t.epochDay).put("cat", t.category).put("priority", t.priority).put("note", t.note).put("repeat", t.repeat)) }
        p.edit().putString("tasks", a.toString()).apply()
    }

    fun goals(): List<PGoal> = runCatching {
        val a = JSONArray(p.getString("goals", "[]")); (0 until a.length()).map { i -> val o=a.getJSONObject(i); PGoal(o.getString("id"),o.getString("title"),o.optInt("progress"),o.optInt("target",100)) }
    }.getOrDefault(emptyList())
    fun saveGoals(v: List<PGoal>) { val a=JSONArray(); v.forEach { a.put(JSONObject().put("id",it.id).put("title",it.title).put("progress",it.progress).put("target",it.target)) }; p.edit().putString("goals",a.toString()).apply() }

    fun reviews(): List<PReview> = runCatching {
        val a=JSONArray(p.getString("reviews","[]")); (0 until a.length()).map { i -> val o=a.getJSONObject(i); PReview(o.getString("id"),o.getLong("day"),o.getInt("mood"),o.optString("note")) }
    }.getOrDefault(emptyList())
    fun saveReviews(v: List<PReview>) { val a=JSONArray(); v.forEach { a.put(JSONObject().put("id",it.id).put("day",it.epochDay).put("mood",it.mood).put("note",it.note)) }; p.edit().putString("reviews",a.toString()).apply() }

    fun countdowns(): List<PCountdown> = runCatching {
        val a=JSONArray(p.getString("countdowns","[]")); (0 until a.length()).map { i -> val o=a.getJSONObject(i); PCountdown(o.getString("id"),o.getString("title"),o.getLong("target"),o.optInt("style")) }
    }.getOrDefault(emptyList())
    fun saveCountdowns(v: List<PCountdown>) { val a=JSONArray(); v.forEach { a.put(JSONObject().put("id",it.id).put("title",it.title).put("target",it.targetEpochDay).put("style",it.style)) }; p.edit().putString("countdowns",a.toString()).apply() }

    fun int(k:String,d:Int)=p.getInt(k,d)
    fun bool(k:String,d:Boolean)=p.getBoolean(k,d)
    fun string(k:String,d:String)=p.getString(k,d) ?: d
    fun putInt(k:String,v:Int)=p.edit().putInt(k,v).apply()
    fun putBool(k:String,v:Boolean)=p.edit().putBoolean(k,v).apply()
    fun putString(k:String,v:String)=p.edit().putString(k,v).apply()

    fun fullBackup(): String = JSONObject()
        .put("format","planjoy-r713-backup-v1")
        .put("created", Instant.now().toString())
        .put("tasks", JSONArray(p.getString("tasks","[]")))
        .put("goals", JSONArray(p.getString("goals","[]")))
        .put("reviews", JSONArray(p.getString("reviews","[]")))
        .put("countdowns", JSONArray(p.getString("countdowns","[]")))
        .put("focusMinutes", int("focusMinutes",0))
        .toString(2)
}

class R713MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { PlanJoyR713() }
    }
}

@Composable
private fun PlanJoyR713() {
    val ctx = LocalContext.current
    val store = remember { PStore(ctx) }
    var fa by remember { mutableStateOf(store.bool("fa", false)) }
    var calMode by remember { mutableStateOf(CalendarMode.entries.getOrElse(store.int("calendarMode",0)){CalendarMode.GREGORIAN}) }
    var themeId by remember { mutableIntStateOf(store.int("theme",0)) }
    var screen by remember { mutableStateOf(Screen.TODAY) }
    var tasks by remember { mutableStateOf(store.tasks()) }
    var goals by remember { mutableStateOf(store.goals()) }
    var reviews by remember { mutableStateOf(store.reviews()) }
    var countdowns by remember { mutableStateOf(store.countdowns()) }
    var addTask by remember { mutableStateOf(false) }
    var addGoal by remember { mutableStateOf(false) }
    var addReview by remember { mutableStateOf(false) }
    var addCountdown by remember { mutableStateOf(false) }

    val colors = remember(themeId) { scheme(themeId) }
    val faFont = runCatching { fontResource(R.font.iransans_xv) }.getOrNull()
    val family = if (fa && faFont != null) FontFamily(faFont) else FontFamily.Default
    val typography = Typography(
        titleLarge = LocalTextStyle.current.copy(fontFamily=family,fontWeight=FontWeight.Bold,fontSize=24.sp),
        titleMedium = LocalTextStyle.current.copy(fontFamily=family,fontWeight=FontWeight.Bold,fontSize=18.sp),
        bodyLarge = LocalTextStyle.current.copy(fontFamily=family,fontSize=15.sp),
        bodyMedium = LocalTextStyle.current.copy(fontFamily=family,fontSize=13.sp),
        labelLarge = LocalTextStyle.current.copy(fontFamily=family,fontWeight=FontWeight.SemiBold,fontSize=13.sp)
    )

    CompositionLocalProvider(LocalLayoutDirection provides if (fa) LayoutDirection.Rtl else LayoutDirection.Ltr) {
        MaterialTheme(colorScheme = colors, typography = typography) {
            Surface(Modifier.fillMaxSize()) {
                BoxWithConstraints {
                    val wide = maxWidth >= 760.dp
                    if (wide) {
                        Row(Modifier.fillMaxSize()) {
                            SideRail(screen,fa,{screen=it},Modifier.width(216.dp).fillMaxHeight())
                            VerticalDivider()
                            AppBody(screen,fa,calMode,themeId,tasks,goals,reviews,countdowns,store,
                                onTasks={tasks=it;store.saveTasks(it)}, onGoals={goals=it;store.saveGoals(it)}, onReviews={reviews=it;store.saveReviews(it)}, onCountdowns={countdowns=it;store.saveCountdowns(it)},
                                onFa={fa=it;store.putBool("fa",it)}, onCal={calMode=it;store.putInt("calendarMode",it.ordinal)}, onTheme={themeId=it;store.putInt("theme",it)},
                                onAddTask={addTask=true},onAddGoal={addGoal=true},onAddReview={addReview=true},onAddCountdown={addCountdown=true}, modifier=Modifier.weight(1f))
                        }
                    } else {
                        Scaffold(
                            bottomBar={BottomNav(screen,fa){screen=it}},
                            floatingActionButton={ if(screen==Screen.TODAY) FloatingActionButton(onClick={addTask=true}){Text("＋",fontSize=24.sp)} }
                        ) { pad ->
                            AppBody(screen,fa,calMode,themeId,tasks,goals,reviews,countdowns,store,
                                onTasks={tasks=it;store.saveTasks(it)}, onGoals={goals=it;store.saveGoals(it)}, onReviews={reviews=it;store.saveReviews(it)}, onCountdowns={countdowns=it;store.saveCountdowns(it)},
                                onFa={fa=it;store.putBool("fa",it)}, onCal={calMode=it;store.putInt("calendarMode",it.ordinal)}, onTheme={themeId=it;store.putInt("theme",it)},
                                onAddTask={addTask=true},onAddGoal={addGoal=true},onAddReview={addReview=true},onAddCountdown={addCountdown=true}, modifier=Modifier.padding(pad))
                        }
                    }
                }
            }
        }
    }

    if(addTask) TaskDialog(fa){ t -> if(t!=null){tasks=tasks+t;store.saveTasks(tasks); SoundFx.play(ctx, store, R.raw.soft_pop)}; addTask=false }
    if(addGoal) TextDialog(if(fa)"هدف تازه" else "New goal", if(fa)"عنوان هدف" else "Goal title",fa){ v -> if(v!=null){goals=goals+PGoal(UUID.randomUUID().toString(),v);store.saveGoals(goals);SoundFx.play(ctx,store,R.raw.reward_chime)};addGoal=false }
    if(addReview) ReviewDialog(fa){ mood,note -> if(mood!=null){reviews=reviews+PReview(UUID.randomUUID().toString(),LocalDate.now().toEpochDay(),mood,note);store.saveReviews(reviews);SoundFx.play(ctx,store,R.raw.soft_pop)};addReview=false }
    if(addCountdown) CountdownDialog(fa){ title,days -> if(title!=null){countdowns=countdowns+PCountdown(UUID.randomUUID().toString(),title,LocalDate.now().plusDays(days.toLong()).toEpochDay(),countdowns.size%3);store.saveCountdowns(countdowns)};addCountdown=false }
}

@Composable
private fun AppBody(
    screen:Screen,fa:Boolean,calMode:CalendarMode,themeId:Int,tasks:List<PTask>,goals:List<PGoal>,reviews:List<PReview>,countdowns:List<PCountdown>,store:PStore,
    onTasks:(List<PTask>)->Unit,onGoals:(List<PGoal>)->Unit,onReviews:(List<PReview>)->Unit,onCountdowns:(List<PCountdown>)->Unit,
    onFa:(Boolean)->Unit,onCal:(CalendarMode)->Unit,onTheme:(Int)->Unit,onAddTask:()->Unit,onAddGoal:()->Unit,onAddReview:()->Unit,onAddCountdown:()->Unit,modifier:Modifier=Modifier
){
    Column(modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Header(screen,fa)
        Crossfade(screen,label="screen") { s ->
            when(s){
                Screen.TODAY -> TodayPage(fa,calMode,tasks,onTasks,onAddTask,store)
                Screen.CALENDAR -> CalendarPage(fa,calMode,tasks)
                Screen.GOALS -> GoalsPage(fa,goals,onGoals,onAddGoal,store)
                Screen.FOCUS -> FocusPage(fa,store)
                Screen.REVIEW -> ReviewPage(fa,reviews,onReviews,onAddReview)
                Screen.STATS -> StatsPage(fa,tasks,goals,reviews,store)
                Screen.COUNTDOWN -> CountdownPage(fa,calMode,countdowns,onCountdowns,onAddCountdown)
                Screen.WIDGETS -> WidgetsPage(fa,tasks,goals,countdowns,store)
                Screen.JOY -> JoyPage(fa,tasks,goals,store)
                Screen.SMART -> SmartPage(fa,tasks,onTasks,store)
                Screen.SETTINGS -> SettingsPage(fa,calMode,themeId,store,onFa,onCal,onTheme)
            }
        }
    }
}

@Composable private fun Header(screen:Screen,fa:Boolean){
    val title = label(screen,fa)
    Row(Modifier.fillMaxWidth().padding(horizontal=20.dp,vertical=14.dp),verticalAlignment=Alignment.CenterVertically){
        DuckMascot(46.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)){ Text(title,style=MaterialTheme.typography.titleLarge); Text(if(fa)"برنامه‌ریزی آرام، روشن و قابل اعتماد" else "A calmer way to plan what matters",color=MaterialTheme.colorScheme.onSurfaceVariant,style=MaterialTheme.typography.bodyMedium) }
        AssistChip(onClick={},label={Text("R7.1.3")})
    }
    HorizontalDivider(color=MaterialTheme.colorScheme.outlineVariant)
}

@Composable private fun SideRail(selected:Screen,fa:Boolean,on:(Screen)->Unit,modifier:Modifier){
    Column(modifier.background(MaterialTheme.colorScheme.surfaceContainerLow).padding(12.dp)){
        Row(verticalAlignment=Alignment.CenterVertically){DuckMascot(52.dp);Spacer(Modifier.width(8.dp));Column{Text("PlanJoy",fontWeight=FontWeight.Bold,fontSize=21.sp);Text(if(fa)"نسخه کامل" else "Full feature build",fontSize=11.sp,color=MaterialTheme.colorScheme.primary)}}
        Spacer(Modifier.height(16.dp))
        val items=listOf(Screen.TODAY,Screen.CALENDAR,Screen.GOALS,Screen.FOCUS,Screen.REVIEW,Screen.STATS,Screen.COUNTDOWN,Screen.WIDGETS,Screen.JOY,Screen.SMART,Screen.SETTINGS)
        items.forEach { s -> NavRow(label(s,fa),selected==s){on(s)} }
        Spacer(Modifier.weight(1f)); Text(if(fa)"EN + فارسی • میلادی + شمسی • همه قابلیت‌ها فعال" else "EN + Persian • Gregorian + Jalali • full feature set",fontSize=11.sp,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable private fun NavRow(text:String,active:Boolean,on:()->Unit){
    val bg=if(active)MaterialTheme.colorScheme.primaryContainer else Color.Transparent
    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(bg).clickable(onClick=on).padding(12.dp),verticalAlignment=Alignment.CenterVertically){
        Text(if(active)"●" else "○",color=if(active)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant);Spacer(Modifier.width(10.dp));Text(text,fontWeight=if(active)FontWeight.Bold else FontWeight.Normal)
    }
}

@Composable private fun BottomNav(selected:Screen,fa:Boolean,on:(Screen)->Unit){
    NavigationBar{ listOf(Screen.TODAY,Screen.CALENDAR,Screen.WIDGETS,Screen.SETTINGS).forEach { s -> NavigationBarItem(selected==s,onClick={on(s)},icon={Text(if(selected==s)"●" else "○")},label={Text(label(s,fa))}) } }
}

@Composable private fun TodayPage(fa:Boolean,mode:CalendarMode,tasks:List<PTask>,onTasks:(List<PTask>)->Unit,onAdd:()->Unit,store:PStore){
    val today=LocalDate.now().toEpochDay(); val due=tasks.filter{it.epochDay<=today&&!it.done}; val completed=tasks.count{it.done}
    LazyColumn(Modifier.fillMaxSize().padding(horizontal=18.dp),contentPadding=PaddingValues(bottom=100.dp),verticalArrangement=Arrangement.spacedBy(10.dp)){
        item { HeroCard(fa,mode,tasks.size,completed,onAdd) }
        item { SectionTitle(if(fa)"امروز" else "Today", if(fa)"کارهای نزدیک را سبک و واضح نگه دار" else "Keep the next things clear and light") }
        if(due.isEmpty()) item { EmptyCard(if(fa)"امروز چیزی عقب نمانده ✨" else "Nothing is weighing on today ✨",if(fa)"یک برنامه کوچک اضافه کن یا از Smart Plan کمک بگیر." else "Add a small plan or use Smart Plan when you need help.") }
        items(due,key={it.id}) { t -> TaskRow(t,fa,mode){
            val n=tasks.map{if(it.id==t.id)it.copy(done=!it.done)else it}; onTasks(n); if(!t.done){store.putInt("joyXp",store.int("joyXp",0)+8);store.putInt("coins",store.int("coins",0)+2);SoundFx.play(LocalContext.current,store,R.raw.reward_chime)}
        } }
        if(tasks.any{it.done}) item{ SectionTitle(if(fa)"انجام‌شده" else "Completed", "${completed}") }
        items(tasks.filter{it.done}.takeLast(6),key={"done-${it.id}"}){t->TaskRow(t,fa,mode){onTasks(tasks.map{if(it.id==t.id)it.copy(done=false)else it})}}
    }
}

@Composable private fun HeroCard(fa:Boolean,mode:CalendarMode,total:Int,done:Int,onAdd:()->Unit){
    ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(26.dp),colors=CardDefaults.elevatedCardColors(containerColor=MaterialTheme.colorScheme.primaryContainer)){
        Row(Modifier.padding(20.dp),verticalAlignment=Alignment.CenterVertically){
            Column(Modifier.weight(1f)){Text(formatDate(LocalDate.now(),mode,fa),fontWeight=FontWeight.Bold,fontSize=17.sp);Spacer(Modifier.height(6.dp));Text(if(fa)"هر کار کوچک، کمی فضا برای نفس کشیدن می‌سازد." else "Every small finish makes a little more room to breathe.",color=MaterialTheme.colorScheme.onPrimaryContainer);Spacer(Modifier.height(14.dp));Row{Button(onClick=onAdd){Text(if(fa)"＋ برنامه" else "+ Plan")};Spacer(Modifier.width(10.dp));AssistChip(onClick={},label={Text("$done / $total")})}}
            DuckMascot(90.dp)
        }
    }
}

@Composable private fun TaskRow(t:PTask,fa:Boolean,mode:CalendarMode,onToggle:()->Unit){
    Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surfaceContainerLow)){
        Row(Modifier.clickable(onClick=onToggle).padding(14.dp),verticalAlignment=Alignment.CenterVertically){
            Box(Modifier.size(26.dp).clip(CircleShape).border(2.dp,if(t.done)MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline,CircleShape).background(if(t.done)MaterialTheme.colorScheme.primary else Color.Transparent),contentAlignment=Alignment.Center){if(t.done)Text("✓",color=MaterialTheme.colorScheme.onPrimary)}
            Spacer(Modifier.width(12.dp));Column(Modifier.weight(1f)){Text(t.title,fontWeight=FontWeight.SemiBold);Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){Text(t.category,fontSize=11.sp,color=MaterialTheme.colorScheme.primary);Text(formatDate(LocalDate.ofEpochDay(t.epochDay),mode,fa),fontSize=11.sp,color=MaterialTheme.colorScheme.onSurfaceVariant);if(t.repeat!="None")Text("↻ ${t.repeat}",fontSize=11.sp)}}
            Text("!".repeat(max(1,min(3,t.priority))),color=if(t.priority>=3)MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.secondary)
        }
    }
}

@Composable private fun CalendarPage(fa:Boolean,mode:CalendarMode,tasks:List<PTask>){
    var offset by remember{mutableIntStateOf(0)}; val start=LocalDate.now().plusDays(offset.toLong())
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
        item{Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically){OutlinedButton(onClick={offset-=7}){Text("‹")};Spacer(Modifier.weight(1f));Text(formatDate(start,mode,fa),fontWeight=FontWeight.Bold);Spacer(Modifier.weight(1f));OutlinedButton(onClick={offset+=7}){Text("›")}}}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(6.dp)){repeat(7){i->val d=start.plusDays(i.toLong());val c=tasks.count{it.epochDay==d.toEpochDay()&&!it.done};Card(Modifier.weight(1f),colors=CardDefaults.cardColors(containerColor=if(d==LocalDate.now())MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainerLow)){Column(Modifier.padding(vertical=12.dp).fillMaxWidth(),horizontalAlignment=Alignment.CenterHorizontally){Text(d.dayOfWeek.name.take(2),fontSize=10.sp);Text(if(mode==CalendarMode.JALALI)gregorianToJalali(d).third.toString() else d.dayOfMonth.toString(),fontWeight=FontWeight.Bold,fontSize=19.sp);if(c>0)Badge{Text(c.toString())}}}}}}
        (0..6).forEach { i -> val d=start.plusDays(i.toLong()); val list=tasks.filter{it.epochDay==d.toEpochDay()}; item{SectionTitle(formatDate(d,mode,fa),if(list.isEmpty())(if(fa)"برنامه‌ای نیست" else "No plans") else "${list.size}")}; if(list.isEmpty()) item{Spacer(Modifier.height(2.dp))} else items(list){TaskRow(it,fa,mode){}} }
    }
}

@Composable private fun GoalsPage(fa:Boolean,goals:List<PGoal>,onGoals:(List<PGoal>)->Unit,onAdd:()->Unit,store:PStore){
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
        item{ActionHeader(if(fa)"هدف‌ها و نقاط عطف" else "Goals & milestones",if(fa)"هدف را به قدم‌های قابل دیدن تبدیل کن." else "Turn a goal into visible, kind steps.",if(fa)"هدف تازه" else "New goal",onAdd)}
        if(goals.isEmpty())item{EmptyCard(if(fa)"یک مقصد انتخاب کن" else "Choose a destination",if(fa)"پیشرفت را بدون فشار، قدم‌به‌قدم ثبت کن." else "Track progress step by step, without pressure.")}
        items(goals,key={it.id}){g->ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(20.dp)){Column(Modifier.padding(16.dp)){Row{Text(g.title,fontWeight=FontWeight.Bold,modifier=Modifier.weight(1f));Text("${g.progress}%",color=MaterialTheme.colorScheme.primary,fontWeight=FontWeight.Bold)};Spacer(Modifier.height(10.dp));LinearProgressIndicator({g.progress/100f},Modifier.fillMaxWidth().height(9.dp).clip(CircleShape));Spacer(Modifier.height(10.dp));Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){OutlinedButton(onClick={onGoals(goals.map{if(it.id==g.id)it.copy(progress=max(0,it.progress-10))else it})}){Text("−10")};Button(onClick={val n=min(100,g.progress+10);onGoals(goals.map{if(it.id==g.id)it.copy(progress=n)else it});if(n==100){store.putInt("joyXp",store.int("joyXp",0)+40);SoundFx.play(LocalContext.current,store,R.raw.reward_chime)}}){Text("+10")}}}}}
    }
}

@Composable private fun FocusPage(fa:Boolean,store:PStore){
    var minutes by remember{mutableIntStateOf(25)}; var seconds by remember{mutableIntStateOf(25*60)}; var running by remember{mutableStateOf(false)}; val ctx=LocalContext.current
    LaunchedEffect(running,seconds){if(running&&seconds>0){delay(1000);seconds--} else if(running&&seconds==0){running=false;store.putInt("focusMinutes",store.int("focusMinutes",0)+minutes);store.putInt("joyXp",store.int("joyXp",0)+15);SoundFx.play(ctx,store,R.raw.reward_chime)}}
    Column(Modifier.fillMaxSize().padding(20.dp),horizontalAlignment=Alignment.CenterHorizontally){
        Spacer(Modifier.height(12.dp));DuckMascot(110.dp);Text(if(fa)"یک کار. یک بازه. بدون شلوغی." else "One thing. One session. Less noise.",color=MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(20.dp));Card(shape=CircleShape,colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.primaryContainer)){Box(Modifier.size(250.dp),contentAlignment=Alignment.Center){Canvas(Modifier.fillMaxSize().padding(16.dp)){drawArc(color=Color.White.copy(alpha=.65f),startAngle=-90f,sweepAngle=360f,useCenter=false,style=Stroke(13f));val ratio=seconds.toFloat()/(minutes*60).coerceAtLeast(1);drawArc(color=Color(0xFFE76F51),startAngle=-90f,sweepAngle=360f*ratio,useCenter=false,style=Stroke(13f))};Column(horizontalAlignment=Alignment.CenterHorizontally){Text("%02d:%02d".format(seconds/60,seconds%60),fontSize=44.sp,fontWeight=FontWeight.Bold);Text(if(fa)"زمان تمرکز" else "focus time")}}}
        Spacer(Modifier.height(18.dp));Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf(15,25,45,60).forEach{m->FilterChip(minutes==m,onClick={minutes=m;seconds=m*60;running=false},label={Text("$m")})}}
        Spacer(Modifier.height(14.dp));Button(onClick={running=!running;if(running)SoundFx.play(ctx,store,R.raw.focus_start)},modifier=Modifier.width(180.dp)){Text(if(running)(if(fa)"مکث" else "Pause") else (if(fa)"شروع" else "Start"))};TextButton(onClick={running=false;seconds=minutes*60}){Text(if(fa)"بازنشانی" else "Reset")}
        Spacer(Modifier.height(18.dp));InfoCard(if(fa)"تمرکز ثبت‌شده" else "Focus logged","${store.int("focusMinutes",0)} min")
    }
}

@Composable private fun ReviewPage(fa:Boolean,reviews:List<PReview>,onReviews:(List<PReview>)->Unit,onAdd:()->Unit){
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
        item{ActionHeader(if(fa)"مرور روز و حال‌و‌هوا" else "Review & mood",if(fa)"چند خط کوتاه هم کافی است." else "A few honest lines are enough.",if(fa)"ثبت امروز" else "Review today",onAdd)}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){listOf("😞","😕","😐","🙂","😄").forEachIndexed{i,e->val n=reviews.count{it.mood==i};Column(horizontalAlignment=Alignment.CenterHorizontally){Text(e,fontSize=28.sp);Text(n.toString(),fontSize=11.sp)}}}}
        if(reviews.isEmpty())item{EmptyCard(if(fa)"مرورت هنوز خالی است" else "Your review space is open",if(fa)"بدون نمره دادن به خودت، فقط ثبت کن چه گذشت." else "No grading yourself—just notice what happened.")}
        items(reviews.sortedByDescending{it.epochDay},key={it.id}){r->Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp)){Row(Modifier.padding(15.dp)){Text(listOf("😞","😕","😐","🙂","😄")[r.mood],fontSize=30.sp);Spacer(Modifier.width(12.dp));Column{Text(LocalDate.ofEpochDay(r.epochDay).toString(),fontSize=11.sp,color=MaterialTheme.colorScheme.onSurfaceVariant);Text(r.note.ifBlank{if(fa)"بدون یادداشت" else "No note"})}}}}
    }
}

@Composable private fun StatsPage(fa:Boolean,tasks:List<PTask>,goals:List<PGoal>,reviews:List<PReview>,store:PStore){
    val done=tasks.count{it.done};val rate=if(tasks.isEmpty())0 else done*100/tasks.size;val focus=store.int("focusMinutes",0)
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{SectionTitle(if(fa)"آمار و روندها" else "Statistics & trends",if(fa)"اطلاعات برای شناخت الگوها، نه قضاوت عملکرد." else "Information for patterns—not a performance grade.")}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(10.dp)){MetricCard(if(fa)"انجام‌شده" else "Completed","$done",Modifier.weight(1f));MetricCard(if(fa)"نرخ تکمیل" else "Completion","$rate%",Modifier.weight(1f));MetricCard(if(fa)"تمرکز" else "Focus","${focus}m",Modifier.weight(1f))}}
        item{ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(18.dp)){Text(if(fa)"توزیع اولویت" else "Priority distribution",fontWeight=FontWeight.Bold);Spacer(Modifier.height(14.dp));(1..3).forEach{p->val c=tasks.count{it.priority==p};Row(verticalAlignment=Alignment.CenterVertically){Text("P$p",Modifier.width(32.dp));LinearProgressIndicator({if(tasks.isEmpty())0f else c.toFloat()/tasks.size},Modifier.weight(1f).height(9.dp).clip(CircleShape));Spacer(Modifier.width(8.dp));Text(c.toString())};Spacer(Modifier.height(8.dp))}}}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(10.dp)){MetricCard(if(fa)"هدف‌ها" else "Goals",goals.size.toString(),Modifier.weight(1f));MetricCard(if(fa)"مرورها" else "Reviews",reviews.size.toString(),Modifier.weight(1f));MetricCard("JOY XP",store.int("joyXp",0).toString(),Modifier.weight(1f))}}
    }
}

@Composable private fun CountdownPage(fa:Boolean,mode:CalendarMode,countdowns:List<PCountdown>,onCountdowns:(List<PCountdown>)->Unit,onAdd:()->Unit){
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(12.dp)){
        item{ActionHeader(if(fa)"شمارش معکوس" else "Countdowns",if(fa)"برای تاریخ‌هایی که دوست داری جلوی چشم بمانند." else "Keep meaningful dates close without clutter.",if(fa)"شمارش تازه" else "New countdown",onAdd)}
        if(countdowns.isEmpty())item{EmptyCard(if(fa)"یک تاریخ مهم اضافه کن" else "Add a date worth remembering",if(fa)"سفر، تولد، تحویل پروژه یا هر نقطه مهم." else "A trip, birthday, project delivery, or anything meaningful.")}
        items(countdowns,key={it.id}){c->val days=c.targetEpochDay-LocalDate.now().toEpochDay();val palette=listOf(MaterialTheme.colorScheme.primaryContainer,MaterialTheme.colorScheme.secondaryContainer,MaterialTheme.colorScheme.tertiaryContainer);ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(24.dp),colors=CardDefaults.elevatedCardColors(containerColor=palette[c.style%palette.size])){Row(Modifier.padding(18.dp),verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){Text(c.title,fontWeight=FontWeight.Bold,fontSize=18.sp);Text(formatDate(LocalDate.ofEpochDay(c.targetEpochDay),mode,fa),fontSize=12.sp)};Text(days.toString(),fontSize=36.sp,fontWeight=FontWeight.ExtraBold);Spacer(Modifier.width(6.dp));Text(if(fa)"روز" else "days")}}}
    }
}

@Composable private fun WidgetsPage(fa:Boolean,tasks:List<PTask>,goals:List<PGoal>,countdowns:List<PCountdown>,store:PStore){
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{SectionTitle(if(fa)"مرکز ویجت‌ها" else "Widget studio",if(fa)"ویجت‌ها از همان داده‌های اصلی برنامه استفاده می‌کنند." else "Widgets read the same canonical data as the app.")}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(10.dp)){WidgetPreview("☀",if(fa)"امروز" else "Today","${tasks.count{!it.done}}",Modifier.weight(1f));WidgetPreview("◎",if(fa)"تمرکز" else "Focus","${store.int("focusMinutes",0)}m",Modifier.weight(1f))}}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(10.dp)){WidgetPreview("◒",if(fa)"هدف" else "Goal",goals.firstOrNull()?.let{"${it.progress}%"}?:"—",Modifier.weight(1f));WidgetPreview("▣",if(fa)"شمارش" else "Countdown",countdowns.firstOrNull()?.let{(it.targetEpochDay-LocalDate.now().toEpochDay()).toString()}?:"—",Modifier.weight(1f))}}
        item{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(10.dp)){WidgetPreview("☻",if(fa)"حال" else "Mood","🙂",Modifier.weight(1f));WidgetPreview("▤",if(fa)"هفته" else "Week","7",Modifier.weight(1f))}}
        item{InfoCard(if(fa)"ویجت‌های واقعی Android" else "Real Android widgets",if(fa)"Today • Focus • Goal — از صفحه افزودن ویجت گوشی قابل انتخاب‌اند." else "Today • Focus • Goal — available from the Android home-screen widget picker.")}
    }
}

@Composable private fun JoyPage(fa:Boolean,tasks:List<PTask>,goals:List<PGoal>,store:PStore){
    val xp=store.int("joyXp",0);val coins=store.int("coins",0);val level=xp/100+1;val doneToday=tasks.count{it.done&&it.epochDay==LocalDate.now().toEpochDay()}
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(26.dp),colors=CardDefaults.elevatedCardColors(containerColor=MaterialTheme.colorScheme.secondaryContainer)){Row(Modifier.padding(20.dp),verticalAlignment=Alignment.CenterVertically){DuckMascot(100.dp);Spacer(Modifier.width(14.dp));Column(Modifier.weight(1f)){Text("JOY • Lv $level",fontSize=24.sp,fontWeight=FontWeight.ExtraBold);Text(if(fa)"همراهی که با پیشرفتت رشد می‌کند، نه با فشار." else "A companion that grows with progress, never with pressure.");Spacer(Modifier.height(10.dp));LinearProgressIndicator({(xp%100)/100f},Modifier.fillMaxWidth().height(10.dp).clip(CircleShape));Text("$xp XP  •  ◆ $coins",fontWeight=FontWeight.Bold)}}}
        item{SectionTitle(if(fa)"چالش‌های امروز" else "Today’s challenges",if(fa)"پاداش‌ها فقط از کار واقعی می‌آیند." else "Rewards come from real activity only.")}
        item{ChallengeCard(if(fa)"یک برنامه را کامل کن" else "Complete one plan",doneToday>=1,8);ChallengeCard(if(fa)"یک جلسه تمرکز" else "Run a focus session",store.int("focusMinutes",0)>0,15);ChallengeCard(if(fa)"یک هدف را جلو ببر" else "Move a goal forward",goals.any{it.progress>0},12)}
        item{InfoCard(if(fa)"Full Feature Build" else "Full Feature Build",if(fa)"تم‌ها، ویجت‌های پیشرفته، آمار، هدف، Focus، مرور، شمارش معکوس، JOY و Smart Plan در این محصول مستقل بدون Paywall داخلی فعال‌اند." else "Themes, advanced widgets, analytics, Goals, Focus, Review, Countdowns, JOY and Smart Plan are available in this independent build without an internal paywall.")}
    }
}

@Composable private fun SmartPage(fa:Boolean,tasks:List<PTask>,onTasks:(List<PTask>)->Unit,store:PStore){
    var text by remember{mutableStateOf("")};var preview by remember{mutableStateOf<PTask?>(null)}
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{SectionTitle(if(fa)"Smart Plan" else "Smart Plan",if(fa)"یک جمله بنویس؛ تاریخ، اولویت و تکرار را پیشنهاد می‌دهیم." else "Write a sentence; we’ll suggest date, priority and recurrence locally.")}
        item{OutlinedTextField(text,{text=it},Modifier.fillMaxWidth(),minLines=3,label={Text(if(fa)"مثلاً: فردا ساعت ۹ گزارش را با اولویت بالا تمام کن" else "e.g. Finish the report tomorrow, high priority")});Spacer(Modifier.height(8.dp));Button(onClick={preview=parseSmart(text,fa)}){Text(if(fa)"تحلیل محلی" else "Parse locally")}}
        preview?.let{p->item{ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(18.dp)){Text(if(fa)"پیشنهاد" else "Suggestion",fontWeight=FontWeight.Bold);Text(p.title,fontSize=18.sp);Text("${LocalDate.ofEpochDay(p.epochDay)} • P${p.priority} • ${p.repeat}",color=MaterialTheme.colorScheme.onSurfaceVariant);Spacer(Modifier.height(10.dp));Button(onClick={onTasks(tasks+p);store.putInt("joyXp",store.int("joyXp",0)+2);text="";preview=null}){Text(if(fa)"افزودن به برنامه" else "Add to plans")}}}}}
        item{InfoCard(if(fa)"حریم خصوصی" else "Privacy",if(fa)"این نسخه از Smart Plan برای استخراج اولیه کاملاً روی دستگاه اجرا می‌شود؛ اتصال AI ابری در مرحله بعد فقط با رضایت کاربر اضافه می‌شود." else "This Smart Plan extraction runs on-device. Optional cloud AI can be added later only with explicit user consent.")}
    }
}

@Composable private fun SettingsPage(fa:Boolean,mode:CalendarMode,themeId:Int,store:PStore,onFa:(Boolean)->Unit,onCal:(CalendarMode)->Unit,onTheme:(Int)->Unit){
    val ctx=LocalContext.current;var sound by remember{mutableStateOf(store.bool("sound",true))};var privacy by remember{mutableStateOf(store.bool("widgetPrivacy",false))};var section by remember{mutableIntStateOf(0)}
    LazyColumn(Modifier.fillMaxSize().padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        item{Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf(if(fa)"عمومی" else "General",if(fa)"ظاهر" else "Appearance",if(fa)"داده" else "Data",if(fa)"امنیت" else "Security",if(fa)"همگام‌سازی" else "Sync").forEachIndexed{i,t->FilterChip(section==i,onClick={section=i},label={Text(t)})}}}
        when(section){
            0->{item{SettingGroup(if(fa)"زبان و تقویم" else "Language & calendar"){Text(if(fa)"زبان" else "Language",fontWeight=FontWeight.Bold);Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){Choice("English",!fa){onFa(false)};Choice("فارسی",fa){onFa(true)}};Spacer(Modifier.height(12.dp));Text(if(fa)"تقویم" else "Calendar",fontWeight=FontWeight.Bold);Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(8.dp)){Choice(if(fa)"میلادی" else "Gregorian",mode==CalendarMode.GREGORIAN){onCal(CalendarMode.GREGORIAN)};Choice(if(fa)"شمسی" else "Jalali",mode==CalendarMode.JALALI){onCal(CalendarMode.JALALI)};Choice(if(fa)"دوگانه" else "Dual",mode==CalendarMode.DUAL){onCal(CalendarMode.DUAL)}};Text(if(fa)"تغییر زبان و جهت صفحه فوری است و نیازی به راه‌اندازی دوباره ندارد." else "Language, typography and layout direction update immediately.",fontSize=12.sp,color=MaterialTheme.colorScheme.onSurfaceVariant)}}}
            1->{item{SettingGroup(if(fa)"تم و صدا" else "Theme & sound"){Text(if(fa)"تم‌های کامل" else "Full themes",fontWeight=FontWeight.Bold);Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf("Cloud","Mint","Rose","Midnight").forEachIndexed{i,n->Choice(n,themeId==i){onTheme(i)}};Spacer(Modifier.height(12.dp));SwitchLine(if(fa)"بازخورد صوتی" else "Sound feedback",sound){sound=it;store.putBool("sound",it)};OutlinedButton(onClick={SoundFx.play(ctx,store,R.raw.reward_chime)}){Text(if(fa)"پیش‌نمایش صدای پاداش" else "Preview reward sound")};Text(if(fa)"فارسی با IRANSansXV جاسازی‌شده رندر می‌شود." else "Persian uses the embedded IRANSansXV font.",fontSize=12.sp,color=MaterialTheme.colorScheme.primary)}}}
            2->{item{SettingGroup(if(fa)"پشتیبان و خروجی" else "Backup & export"){Button(onClick={shareBackup(ctx,store.fullBackup())}){Text(if(fa)"ساخت و اشتراک پشتیبان JSON" else "Create & share JSON backup")};Spacer(Modifier.height(8.dp));OutlinedButton(onClick={shareCsv(ctx,store.tasks())}){Text(if(fa)"خروجی CSV برنامه‌ها" else "Export plans CSV")};Text(if(fa)"داده اصلی محلی می‌ماند و خروجی فقط با اقدام شما ساخته می‌شود." else "Canonical data stays local; exports are created only on your action.",fontSize=12.sp,color=MaterialTheme.colorScheme.onSurfaceVariant)}}}
            3->{item{SettingGroup(if(fa)"حریم خصوصی و امنیت" else "Privacy & security"){SwitchLine(if(fa)"پنهان‌کردن جزئیات ویجت" else "Hide widget details",privacy){privacy=it;store.putBool("widgetPrivacy",it)};SwitchLine(if(fa)"قفل خودکار" else "Auto lock",store.bool("autoLock",false)){store.putBool("autoLock",it)};Text(if(fa)"PIN / Biometric و رمزگذاری پشتیبان در گام امنیتی بعدی سخت‌گیرانه‌تر می‌شود؛ داده خصوصی بدون رضایت از دستگاه خارج نمی‌شود." else "PIN/biometric and encrypted-backup hardening continue in the next security gate; private data never leaves the device without consent.",fontSize=12.sp,color=MaterialTheme.colorScheme.onSurfaceVariant)}}}
            else->{item{SettingGroup(if(fa)"دستگاه‌ها و Sync" else "Devices & sync"){InfoCard(if(fa)"Local-first" else "Local-first",if(fa)"برنامه بدون حساب هم کامل کار می‌کند. اتصال دستگاه‌ها قابلیت اختیاری است." else "The planner remains fully usable without an account; device sync is optional.");OutlinedButton(onClick={}){Text(if(fa)"مدیریت دستگاه‌ها" else "Device management")};Text(if(fa)"Relay رمزگذاری‌شده و conflict-safe در هسته پروژه حفظ شده است." else "The project retains its encrypted, conflict-safe relay architecture.",fontSize=12.sp)}}}
        }
        item{ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp),colors=CardDefaults.elevatedCardColors(containerColor=MaterialTheme.colorScheme.primaryContainer)){Column(Modifier.padding(18.dp)){Text("R7.1.3 • Experience Parity",fontWeight=FontWeight.ExtraBold);Text(if(fa)"این رابط با الهام از عمق تجربه نسخه مرجع، ولی با کد، دارایی و هویت بصری مستقل ساخته شده است." else "This experience matches the reference product’s depth while using independent code, assets and visual identity.")}}}
    }
}

@Composable private fun SettingGroup(title:String,content:@Composable ColumnScope.()->Unit){ElevatedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(18.dp)){Text(title,fontWeight=FontWeight.ExtraBold,fontSize=18.sp);Spacer(Modifier.height(14.dp));content()}}}
@Composable private fun Choice(text:String,selected:Boolean,on:()->Unit){FilterChip(selected,onClick=on,label={Text(text)})}
@Composable private fun SwitchLine(text:String,value:Boolean,on:(Boolean)->Unit){Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically){Text(text,Modifier.weight(1f));Switch(value,onCheckedChange=on)}}
@Composable private fun SectionTitle(title:String,sub:String){Column(Modifier.padding(top=8.dp,bottom=2.dp)){Text(title,fontWeight=FontWeight.ExtraBold,fontSize=20.sp);if(sub.isNotBlank())Text(sub,color=MaterialTheme.colorScheme.onSurfaceVariant,fontSize=12.sp)}}
@Composable private fun ActionHeader(title:String,sub:String,action:String,on:()->Unit){Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically){Column(Modifier.weight(1f)){SectionTitle(title,sub)};Button(onClick=on){Text("＋ $action")}}}
@Composable private fun EmptyCard(title:String,sub:String){OutlinedCard(Modifier.fillMaxWidth(),shape=RoundedCornerShape(20.dp)){Column(Modifier.padding(22.dp),horizontalAlignment=Alignment.CenterHorizontally){DuckMascot(72.dp);Text(title,fontWeight=FontWeight.Bold,textAlign=TextAlign.Center);Text(sub,color=MaterialTheme.colorScheme.onSurfaceVariant,textAlign=TextAlign.Center,fontSize=12.sp)}}}
@Composable private fun InfoCard(title:String,value:String){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(16.dp),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surfaceContainerLow)){Column(Modifier.padding(14.dp)){Text(title,fontWeight=FontWeight.Bold);Text(value,color=MaterialTheme.colorScheme.onSurfaceVariant,fontSize=12.sp)}}}
@Composable private fun MetricCard(title:String,value:String,modifier:Modifier){ElevatedCard(modifier,shape=RoundedCornerShape(18.dp)){Column(Modifier.padding(15.dp)){Text(value,fontSize=25.sp,fontWeight=FontWeight.ExtraBold);Text(title,fontSize=11.sp,color=MaterialTheme.colorScheme.onSurfaceVariant)}}}
@Composable private fun WidgetPreview(icon:String,title:String,value:String,modifier:Modifier){ElevatedCard(modifier.height(132.dp),shape=RoundedCornerShape(25.dp)){Column(Modifier.padding(15.dp)){Text(icon,fontSize=24.sp);Spacer(Modifier.weight(1f));Text(value,fontSize=27.sp,fontWeight=FontWeight.ExtraBold);Text(title,fontSize=12.sp)}}}
@Composable private fun ChallengeCard(title:String,done:Boolean,xp:Int){Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(18.dp),colors=CardDefaults.cardColors(containerColor=if(done)MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainerLow)){Row(Modifier.padding(15.dp),verticalAlignment=Alignment.CenterVertically){Text(if(done)"✓" else "○",fontSize=22.sp,color=MaterialTheme.colorScheme.primary);Spacer(Modifier.width(12.dp));Text(title,Modifier.weight(1f),fontWeight=FontWeight.SemiBold);Text("+$xp XP",fontSize=11.sp,color=MaterialTheme.colorScheme.primary)}}

@Composable private fun DuckMascot(size:androidx.compose.ui.unit.Dp){
    Canvas(Modifier.size(size)){val w=this.size.width;val h=this.size.height;val yellow=Color(0xFFFFC857);val orange=Color(0xFFF18F3B);drawCircle(yellow,w*.34f,Offset(w*.52f,h*.40f));drawOval(yellow,Offset(w*.20f,h*.47f),Size(w*.65f,h*.42f));val p=Path().apply{moveTo(w*.72f,h*.38f);lineTo(w*.98f,h*.48f);lineTo(w*.72f,h*.54f);close()};drawPath(p,orange);drawCircle(Color(0xFF263238),w*.035f,Offset(w*.60f,h*.34f));drawArc(orange,-10f,180f,false,Offset(w*.32f,h*.58f),Size(w*.34f,h*.20f),style=Stroke(max(2f,w*.025f)))}
}

@Composable private fun TaskDialog(fa:Boolean,on:(PTask?)->Unit){
    var title by remember{mutableStateOf("")};var days by remember{mutableIntStateOf(0)};var p by remember{mutableIntStateOf(1)};var repeat by remember{mutableStateOf("None")};
    AlertDialog(onDismissRequest={on(null)},title={Text(if(fa)"برنامه تازه" else "New plan")},text={Column{OutlinedTextField(title,{title=it},label={Text(if(fa)"عنوان" else "Title")});Spacer(Modifier.height(10.dp));Text(if(fa)"زمان" else "When",fontWeight=FontWeight.Bold);Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)){listOf(0,1,7,30).forEach{d->Choice(if(d==0)(if(fa)"امروز" else "Today") else "+$d",days==d){days=d}}};Spacer(Modifier.height(10.dp));Text(if(fa)"اولویت" else "Priority",fontWeight=FontWeight.Bold);Row(horizontalArrangement=Arrangement.spacedBy(6.dp)){(1..3).forEach{i->Choice("P$i",p==i){p=i}}};Spacer(Modifier.height(10.dp));Text(if(fa)"تکرار" else "Repeat",fontWeight=FontWeight.Bold);Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)){listOf("None","Daily","Weekly","Monthly").forEach{r->Choice(r,repeat==r){repeat=r}}}},confirmButton={Button(enabled=title.isNotBlank(),onClick={on(PTask(UUID.randomUUID().toString(),title.trim(),epochDay=LocalDate.now().plusDays(days.toLong()).toEpochDay(),priority=p,repeat=repeat))}){Text(if(fa)"ذخیره" else "Save")}},dismissButton={TextButton(onClick={on(null)}){Text(if(fa)"لغو" else "Cancel")}})
}

@Composable private fun TextDialog(title:String,hint:String,fa:Boolean,on:(String?)->Unit){var v by remember{mutableStateOf("")};AlertDialog(onDismissRequest={on(null)},title={Text(title)},text={OutlinedTextField(v,{v=it},label={Text(hint)})},confirmButton={Button(enabled=v.isNotBlank(),onClick={on(v.trim())}){Text(if(fa)"ذخیره" else "Save")}},dismissButton={TextButton(onClick={on(null)}){Text(if(fa)"لغو" else "Cancel")}})}
@Composable private fun ReviewDialog(fa:Boolean,on:(Int?,String)->Unit){var mood by remember{mutableIntStateOf(3)};var note by remember{mutableStateOf("")};AlertDialog(onDismissRequest={on(null,"")},title={Text(if(fa)"مرور امروز" else "Today’s review")},text={Column{Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){listOf("😞","😕","😐","🙂","😄").forEachIndexed{i,e->Text(e,fontSize=30.sp,modifier=Modifier.clip(CircleShape).background(if(i==mood)MaterialTheme.colorScheme.primaryContainer else Color.Transparent).clickable{mood=i}.padding(5.dp))}};Spacer(Modifier.height(10.dp));OutlinedTextField(note,{note=it},label={Text(if(fa)"چه چیزی مهم بود؟" else "What mattered today?")},minLines=3)}},confirmButton={Button(onClick={on(mood,note)}){Text(if(fa)"ثبت" else "Save")}},dismissButton={TextButton(onClick={on(null,"")}){Text(if(fa)"لغو" else "Cancel")}})}
@Composable private fun CountdownDialog(fa:Boolean,on:(String?,Int)->Unit){var title by remember{mutableStateOf("")};var days by remember{mutableIntStateOf(7)};AlertDialog(onDismissRequest={on(null,0)},title={Text(if(fa)"شمارش تازه" else "New countdown")},text={Column{OutlinedTextField(title,{title=it},label={Text(if(fa)"عنوان" else "Title")});Spacer(Modifier.height(10.dp));Row(Modifier.horizontalScroll(rememberScrollState()),horizontalArrangement=Arrangement.spacedBy(6.dp)){listOf(1,7,30,90,365).forEach{d->Choice("+$d",days==d){days=d}}}}},confirmButton={Button(enabled=title.isNotBlank(),onClick={on(title.trim(),days)}){Text(if(fa)"ذخیره" else "Save")}},dismissButton={TextButton(onClick={on(null,0)}){Text(if(fa)"لغو" else "Cancel")}})}

private object SoundFx { fun play(ctx:Context,store:PStore,res:Int){if(!store.bool("sound",true))return;runCatching{MediaPlayer.create(ctx,res)?.apply{setOnCompletionListener{it.release()};start()}}} }

private fun parseSmart(text:String,fa:Boolean):PTask{
    val low=text.lowercase();val tomorrow=low.contains("tomorrow")||text.contains("فردا");val weekly=low.contains("weekly")||text.contains("هفتگی");val daily=low.contains("daily")||text.contains("روزانه");val high=low.contains("high")||text.contains("مهم")||text.contains("بالا");val clean=text.trim().ifBlank{if(fa)"برنامه هوشمند" else "Smart plan"};return PTask(UUID.randomUUID().toString(),clean,epochDay=LocalDate.now().plusDays(if(tomorrow)1 else 0).toEpochDay(),priority=if(high)3 else 1,repeat=if(weekly)"Weekly" else if(daily)"Daily" else "None")
}

private fun shareBackup(ctx:Context,text:String){val i=Intent(Intent.ACTION_SEND).apply{type="application/json";putExtra(Intent.EXTRA_TEXT,text);putExtra(Intent.EXTRA_SUBJECT,"PlanJoy R7.1.3 backup")};ctx.startActivity(Intent.createChooser(i,"PlanJoy backup"))}
private fun shareCsv(ctx:Context,tasks:List<PTask>){val body=buildString{append("title,done,date,category,priority,repeat\n");tasks.forEach{append('"').append(it.title.replace("\"","\"\"")).append("\",").append(it.done).append(',').append(LocalDate.ofEpochDay(it.epochDay)).append(',').append(it.category).append(',').append(it.priority).append(',').append(it.repeat).append('\n')}};val i=Intent(Intent.ACTION_SEND).apply{type="text/csv";putExtra(Intent.EXTRA_TEXT,body);putExtra(Intent.EXTRA_SUBJECT,"PlanJoy plans.csv")};ctx.startActivity(Intent.createChooser(i,"Export PlanJoy CSV"))}

private fun label(s:Screen,fa:Boolean)=when(s){Screen.TODAY->if(fa)"امروز" else "Today";Screen.CALENDAR->if(fa)"تقویم" else "Calendar";Screen.GOALS->if(fa)"هدف‌ها" else "Goals";Screen.FOCUS->if(fa)"تمرکز" else "Focus";Screen.REVIEW->if(fa)"مرور" else "Review";Screen.STATS->if(fa)"آمار" else "Statistics";Screen.COUNTDOWN->if(fa)"شمارش" else "Countdowns";Screen.WIDGETS->if(fa)"ویجت‌ها" else "Widgets";Screen.JOY->"JOY";Screen.SMART->if(fa)"برنامه هوشمند" else "Smart Plan";Screen.SETTINGS->if(fa)"تنظیمات" else "Settings"}

private fun scheme(id:Int)=when(id){
    1->lightColorScheme(primary=Color(0xFF19766D),secondary=Color(0xFF5A8F76),tertiary=Color(0xFFE3A857),background=Color(0xFFF6FBF8),surface=Color(0xFFFBFFFC),primaryContainer=Color(0xFFD6F2E9),secondaryContainer=Color(0xFFE1F0E7))
    2->lightColorScheme(primary=Color(0xFFB45B72),secondary=Color(0xFF8A6375),tertiary=Color(0xFFE58D71),background=Color(0xFFFFF8FA),surface=Color(0xFFFFFBFC),primaryContainer=Color(0xFFFFDDE6),secondaryContainer=Color(0xFFF6E4EC))
    3->darkColorScheme(primary=Color(0xFFFFB59D),secondary=Color(0xFF8FD5C8),tertiary=Color(0xFFFFD080),background=Color(0xFF141319),surface=Color(0xFF1B1921),primaryContainer=Color(0xFF553026),secondaryContainer=Color(0xFF1D4C46))
    else->lightColorScheme(primary=Color(0xFFE76F51),secondary=Color(0xFF3F8075),tertiary=Color(0xFFE7A83E),background=Color(0xFFFFFBF7),surface=Color(0xFFFFFFFF),primaryContainer=Color(0xFFFFE6D8),secondaryContainer=Color(0xFFDDF2ED),surfaceContainerLow=Color(0xFFFFF5ED))
}

private fun formatDate(d:LocalDate,mode:CalendarMode,fa:Boolean):String{
    val g=d.format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));val j=gregorianToJalali(d);val js="%04d/%02d/%02d".format(j.first,j.second,j.third);return when(mode){CalendarMode.GREGORIAN->g;CalendarMode.JALALI->js;CalendarMode.DUAL->if(fa)"$js • $g" else "$g • $js"}
}

private fun gregorianToJalali(date:LocalDate):Triple<Int,Int,Int>{
    var gy=date.year;val gm=date.monthValue;val gd=date.dayOfMonth;val gdm=intArrayOf(0,31,59,90,120,151,181,212,243,273,304,334);var jy=if(gy>1600)979 else 0;gy-=if(gy>1600)1600 else 621;val gy2=if(gm>2)gy+1 else gy;var days=365*gy+(gy2+3)/4-(gy2+99)/100+(gy2+399)/400-80+gd+gdm[gm-1];jy+=33*(days/12053);days%=12053;jy+=4*(days/1461);days%=1461;if(days>365){jy+=(days-1)/365;days=(days-1)%365};val jm:Int;val jd:Int;if(days<186){jm=1+days/31;jd=1+days%31}else{jm=7+(days-186)/30;jd=1+(days-186)%30};return Triple(jy,jm,jd)
}
