package com.planjoy.r7
import android.Manifest
import android.app.*
import android.content.pm.PackageManager
import android.os.*
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

class MainActivity:ComponentActivity(){
    override fun onCreate(savedInstanceState:Bundle?){
        val startup=android.os.SystemClock.elapsedRealtime()
        super.onCreate(savedInstanceState)
        val db=PlanJoyDb.get(this)
        if(BuildConfig.DEBUG){intent.getStringExtra("qa_lang")?.let{db.setSetting("lang",if(it=="fa")"fa" else "en")};intent.getIntExtra("qa_calendar",-1).takeIf{it in 0..2}?.let{db.setSetting("calendar",it.toString())};intent.getIntExtra("qa_theme",-1).takeIf{it in 0..3}?.let{db.setSetting("theme",it.toString())};if(intent.getBooleanExtra("qa_seed",false))R73Diagnostics.seedQa(this)}
        R73Diagnostics.install(this,startup)
        BackgroundScheduler.schedule(this)
        ReminderScheduler.schedule(this)
        R72WidgetUpdater.refreshAll(this)
        if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS),700)
        setContent{PlanJoyApp(this)}
    }
    fun unlock(done:()->Unit){
        val fa=PlanJoyDb.get(this).setting("lang","en")=="fa"
        if(Build.VERSION.SDK_INT>=28)
            android.hardware.biometrics.BiometricPrompt.Builder(this)
                .setTitle(if(fa)"خوش آمدی" else "Welcome back")
                .setSubtitle(if(fa)"با اثر انگشت یا چهره، برنامه‌هات رو باز کن" else "Use your fingerprint or face to open your plans")
                .setNegativeButton(if(fa)"فعلاً نه" else "Not now",mainExecutor){_,_->}
                .build()
                .authenticate(CancellationSignal(),mainExecutor,object:android.hardware.biometrics.BiometricPrompt.AuthenticationCallback(){
                    override fun onAuthenticationSucceeded(r:android.hardware.biometrics.BiometricPrompt.AuthenticationResult){done()}
                })
        else done()
    }
}
