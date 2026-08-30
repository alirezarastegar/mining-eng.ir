package com.planjoy.r7

import android.Manifest
import android.app.AlarmManager
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.PowerManager
import android.os.SystemClock
import android.provider.Settings
import android.util.Base64
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import org.json.JSONObject
import java.io.PrintWriter
import java.io.StringWriter
import java.net.HttpURLConnection
import java.net.URL
import java.security.KeyFactory
import java.security.Signature
import java.security.spec.X509EncodedKeySpec
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID
import kotlin.concurrent.thread

private fun r73tr(fa:Boolean,en:String,faText:String)=if(fa)faText else en

data class R73UpdateResult(val ok:Boolean,val message:String,val available:Boolean=false,val version:String="",val url:String="")

object R73Diagnostics {
    private const val VERSION="0.7.3"
    private var installed=false
    fun install(c:Context,startElapsed:Long){
        if(installed)return;installed=true
        val db=PlanJoyDb.get(c)
        val prev=Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler{t,e->
            runCatching{
                val sw=StringWriter();e.printStackTrace(PrintWriter(sw))
                db.diagnostic("crash","thread=${t.name}\n${sw.toString().take(12000)}")
                val dir=java.io.File(c.filesDir,"diagnostics").apply{mkdirs()}
                java.io.File(dir,"crash_latest.txt").writeText("PlanJoy $VERSION\n${Build.MANUFACTURER} ${Build.MODEL}\nAndroid ${Build.VERSION.RELEASE} API ${Build.VERSION.SDK_INT}\n${sw}")
            }
            prev?.uncaughtException(t,e)
        }
        val elapsed=(SystemClock.elapsedRealtime()-startElapsed).coerceAtLeast(0)
        db.setSetting("startup_ms",elapsed.toString())
        db.diagnostic("startup","${elapsed}ms")
    }
    fun seedQa(c:Context){
        val db=PlanJoyDb.get(c); if(db.setting("qa_seeded","0")=="1")return
        val now=System.currentTimeMillis()/1000
        val t1=TaskModel("qa_task_1","Prepare weekly plan","Three small priorities for a calm start","Work",now+3600,now+7200,false,2,0,false,0,true,now+7200,0,0,0,0,"","",0,1,1,0,0,0,0,10)
        val t2=TaskModel("qa_task_2","Walk and reset","A short break is still progress","Personal",now+10800,now+14400,false,1,3,false,0,true,0,0,0,0,0,"","",0,0,1,0,0,0,0,0)
        db.save("task",t1.id,Codec.task(t1)); db.save("task",t2.id,Codec.task(t2))
        val g=GoalModel("qa_goal","Build a calmer routine","Consistency over intensity",now,now+30*86400,0,42,0);db.save("goal",g.id,Codec.goal(g))
        val cd=CountdownModel("qa_countdown","Project milestone",now+12*86400,1,true,true,"QA visual seed");db.save("countdown",cd.id,Codec.countdown(cd))
        db.setSetting("qa_seeded","1")
    }
    fun snapshot(c:Context):String{
        val db=PlanJoyDb.get(c);val rt=Runtime.getRuntime();val ns=db.notificationStats();val fmt=DateTimeFormatter.ISO_OFFSET_DATE_TIME
        val types=listOf("task","goal","focus","review","countdown","reward")
        val b=StringBuilder()
        b.appendLine("PlanJoy R7.3 diagnostics")
        b.appendLine("generated=${fmt.format(Instant.now().atZone(ZoneId.systemDefault()))}")
        b.appendLine("app_version=$VERSION")
        b.appendLine("device=${Build.MANUFACTURER} ${Build.MODEL}")
        b.appendLine("android=${Build.VERSION.RELEASE} api=${Build.VERSION.SDK_INT}")
        b.appendLine("locale=${db.setting("lang","en")} calendar=${db.setting("calendar","0")} theme=${db.setting("theme","0")}")
        b.appendLine("startup_ms=${db.setting("startup_ms","unknown")}")
        b.appendLine("memory_used_mb=${(rt.totalMemory()-rt.freeMemory())/1024/1024} memory_max_mb=${rt.maxMemory()/1024/1024}")
        b.appendLine("sync_configured=${SyncEngine.configured(c)} pending=${db.pending().size} cursor=${db.cursor()} devices=${SyncEngine.devices(c).size}")
        b.appendLine("open_conflicts=${db.conflicts().size}")
        b.appendLine("notification_rows=${ns.first} last_fired_utc=${ns.second} snoozes=${ns.third}")
        b.appendLine("notification_permission=${notificationAllowed(c)} battery_unrestricted=${batteryUnrestricted(c)}")
        types.forEach{b.appendLine("entity_$it=${db.rows(it).size}")}
        b.appendLine("privacy: tokens, recovery keys and payload contents are intentionally excluded")
        return b.toString()
    }
    fun notificationAllowed(c:Context)=Build.VERSION.SDK_INT<33||c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)==PackageManager.PERMISSION_GRANTED
    fun batteryUnrestricted(c:Context):Boolean{val p=c.getSystemService(PowerManager::class.java);return p?.isIgnoringBatteryOptimizations(c.packageName)?:true}
    fun openBatterySettings(c:Context){runCatching{c.startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))}.recoverCatching{c.startActivity(Intent(Settings.ACTION_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))}}
    fun alarmMode(c:Context):String{val a=c.getSystemService(AlarmManager::class.java);return if(Build.VERSION.SDK_INT>=31&&a!=null)if(a.canScheduleExactAlarms())"exact-capable" else "idle-safe-inexact" else "idle-safe"}
}

object R73UpdateVerifier {
    private const val PUB="MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEVGtThtMYWc3gc894rMe10us90fMfcezys6v7fPidyu1ekw/ZygsSQx6oMsF8yHXOZmik4cfvBFZojX9krW+P2A=="
    private fun get(url:String):Pair<Int,ByteArray>{val x=(URL(url).openConnection() as HttpURLConnection);x.connectTimeout=7000;x.readTimeout=7000;x.instanceFollowRedirects=false;x.setRequestProperty("Accept","application/json,text/plain");val code=x.responseCode;val data=(if(code in 200..299)x.inputStream else x.errorStream)?.use{it.readBytes()}?:ByteArray(0);x.disconnect();return code to data}
    fun verify(c:Context,manifestUrl:String):R73UpdateResult{
        if(!SyncEngine.safe(manifestUrl))return R73UpdateResult(false,"HTTPS manifest required")
        return try{
            val (mc,raw)=get(manifestUrl);if(mc !in 200..299)return R73UpdateResult(false,"Manifest HTTP $mc")
            val (sc,sraw)=get(manifestUrl+".sig");if(sc !in 200..299)return R73UpdateResult(false,"Signature HTTP $sc")
            val pub=KeyFactory.getInstance("EC").generatePublic(X509EncodedKeySpec(Base64.decode(PUB,Base64.DEFAULT)))
            val sig=Signature.getInstance("SHA256withECDSA");sig.initVerify(pub);sig.update(raw)
            val sigBytes=Base64.decode(String(sraw).trim(),Base64.DEFAULT);if(!sig.verify(sigBytes))return R73UpdateResult(false,"Signature verification failed")
            val j=JSONObject(String(raw));val code=j.optInt("version_code",0);val ver=j.optString("version","?");val url=j.optString("android_url","")
            PlanJoyDb.get(c).diagnostic("update_check","verified $ver code=$code")
            R73UpdateResult(true,if(code>73000)"Update available" else "You're up to date",code>73000,ver,url)
        }catch(e:Exception){R73UpdateResult(false,e.message?:"Update check failed")}
    }
}

@Composable
fun R73CertificationPanel(a:MainActivity,fa:Boolean){
    val db=PlanJoyDb.get(a);var tick by remember{mutableIntStateOf(0)};var updateMsg by remember{mutableStateOf("")};var updateUrl by remember{mutableStateOf("")};var manifestUrl by remember{mutableStateOf(db.setting("update_manifest_url",""))}
    val exporter=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("text/plain")){uri:Uri?->uri?.let{runCatching{a.contentResolver.openOutputStream(it)?.bufferedWriter()?.use{w->w.write(R73Diagnostics.snapshot(a))}};db.diagnostic("diagnostic_export","user export")}}
    val conflicts=remember(tick){db.conflicts()};val ns=remember(tick){db.notificationStats()};val devs=remember(tick){SyncEngine.devices(a)}
    Column(verticalArrangement=Arrangement.spacedBy(10.dp)){
        Text(r73tr(fa,"Production health","سلامت نسخه نهایی"),style=MaterialTheme.typography.titleMedium)
        Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
            Text(r73tr(fa,"Reminder reliability","پایداری یادآوری‌ها"),fontWeight=FontWeight.Bold)
            Text(r73tr(fa,"Notifications: ${if(R73Diagnostics.notificationAllowed(a))"allowed" else "permission needed"} • Battery: ${if(R73Diagnostics.batteryUnrestricted(a))"unrestricted" else "optimized"} • ${R73Diagnostics.alarmMode(a)}","اعلان‌ها: ${if(R73Diagnostics.notificationAllowed(a))"مجاز" else "نیازمند مجوز"} • باتری: ${if(R73Diagnostics.batteryUnrestricted(a))"بدون محدودیت" else "بهینه‌سازی فعال"} • ${R73Diagnostics.alarmMode(a)}"),style=MaterialTheme.typography.bodySmall)
            Text(r73tr(fa,"Reminder history: ${ns.first} tasks • ${ns.third} snoozes","سابقه یادآوری: ${Jalali.faDigits(ns.first.toString())} برنامه • ${Jalali.faDigits(ns.third.toString())} تعویق"),style=MaterialTheme.typography.bodySmall)
            OutlinedButton({R73Diagnostics.openBatterySettings(a)}){Text(r73tr(fa,"Battery settings","تنظیمات باتری"))}
        }}
        Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
            Text(r73tr(fa,"Cross-device sync health","سلامت همگام‌سازی بین دستگاه‌ها"),fontWeight=FontWeight.Bold)
            Text(r73tr(fa,"Authorized devices: ${devs.count{!it.revoked}} • Pending local changes: ${db.pending().size} • Open conflicts: ${conflicts.size}","دستگاه‌های مجاز: ${Jalali.faDigits(devs.count{!it.revoked}.toString())} • تغییرات منتظر: ${Jalali.faDigits(db.pending().size.toString())} • تعارض باز: ${Jalali.faDigits(conflicts.size.toString())}"),style=MaterialTheme.typography.bodySmall)
            if(conflicts.isEmpty())Text(r73tr(fa,"No unresolved conflicts. Deterministic merge remains active in the background.","تعارض حل‌نشده‌ای نیست؛ ادغام قطعی همچنان در پس‌زمینه فعال است."),style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.primary)
            conflicts.take(5).forEach{c->HorizontalDivider();Text("${c.type} • ${c.entityId.take(12)}…",fontWeight=FontWeight.SemiBold);Text(r73tr(fa,"Both devices changed this item. Choose the version you want to publish as the new canonical revision.","این مورد روی هر دو دستگاه تغییر کرده؛ نسخه‌ای را که می‌خواهی به‌عنوان نسخه جدید منتشر شود انتخاب کن."),style=MaterialTheme.typography.bodySmall);Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(5.dp)){TextButton({db.resolveConflict(c.id,"local");tick++}){Text(r73tr(fa,"Keep mine","نسخه من"))};TextButton({db.resolveConflict(c.id,"remote");tick++}){Text(r73tr(fa,"Use other","نسخه دستگاه دیگر"))};TextButton({db.resolveConflict(c.id,"both");tick++}){Text(r73tr(fa,"Keep both","هر دو"))}}}
        }}
        Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
            Text(r73tr(fa,"Crash & diagnostic export","خروجی خطا و عیب‌یابی"),fontWeight=FontWeight.Bold)
            Text(r73tr(fa,"The report contains app/device/runtime health only. Sync tokens, recovery keys and plan contents are excluded.","گزارش فقط سلامت برنامه، دستگاه و Runtime را دارد؛ توکن همگام‌سازی، کلید بازیابی و متن برنامه‌ها عمداً حذف می‌شوند."),style=MaterialTheme.typography.bodySmall)
            Text(r73tr(fa,"Startup: ${db.setting("startup_ms","?")} ms","زمان شروع: ${Jalali.faDigits(db.setting("startup_ms","?"))} میلی‌ثانیه"),style=MaterialTheme.typography.bodySmall)
            OutlinedButton({exporter.launch("PlanJoy-R73-diagnostics.txt")},Modifier.semantics{contentDescription=if(fa)"خروجی گزارش عیب‌یابی" else "Export diagnostic report"}){Text(r73tr(fa,"Export diagnostic report","خروجی گزارش عیب‌یابی"))}
        }}
        Card(Modifier.fillMaxWidth(),shape=RoundedCornerShape(22.dp)){Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(7.dp)){
            Text(r73tr(fa,"Signed update channel","کانال به‌روزرسانی امضاشده"),fontWeight=FontWeight.Bold)
            OutlinedTextField(manifestUrl,{manifestUrl=it;db.setSetting("update_manifest_url",it.trim())},label={Text(r73tr(fa,"HTTPS manifest URL","آدرس HTTPS مانیفست"))},modifier=Modifier.fillMaxWidth())
            Button({thread{val r=R73UpdateVerifier.verify(a,manifestUrl.trim());a.runOnUiThread{updateMsg=r.message;updateUrl=if(r.available)r.url else ""}}}){Text(r73tr(fa,"Check signed update","بررسی به‌روزرسانی امضاشده"))}
            if(updateMsg.isNotBlank())Text(updateMsg,style=MaterialTheme.typography.bodySmall,color=if(updateUrl.isNotBlank())MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
            if(updateUrl.isNotBlank())OutlinedButton({runCatching{a.startActivity(Intent(Intent.ACTION_VIEW,Uri.parse(updateUrl)))}}){Text(r73tr(fa,"Open verified download","بازکردن دانلود تأییدشده"))}
        }}
    }
}
