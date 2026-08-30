package com.planjoy.r7
import android.Manifest
import android.app.*
import android.content.pm.PackageManager
import android.os.*
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
class MainActivity:ComponentActivity(){override fun onCreate(savedInstanceState:Bundle?){super.onCreate(savedInstanceState);BackgroundScheduler.schedule(this);ReminderScheduler.schedule(this);if(Build.VERSION.SDK_INT>=33&&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS),700);setContent{PlanJoyApp(this)}};fun unlock(done:()->Unit){if(Build.VERSION.SDK_INT>=28)android.hardware.biometrics.BiometricPrompt.Builder(this).setTitle("PlanJoy").setSubtitle("Unlock").setNegativeButton("Cancel",mainExecutor){_,_->}.build().authenticate(CancellationSignal(),mainExecutor,object:android.hardware.biometrics.BiometricPrompt.AuthenticationCallback(){override fun onAuthenticationSucceeded(r:android.hardware.biometrics.BiometricPrompt.AuthenticationResult){done()}})else done()}}
