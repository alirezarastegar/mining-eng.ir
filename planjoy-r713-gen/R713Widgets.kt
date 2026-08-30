package com.planjoy.r7

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.widget.RemoteViews
import org.json.JSONArray

private fun widgetPrefs(context: Context) = context.getSharedPreferences("planjoy_r713", Context.MODE_PRIVATE)
private fun remainingTasks(context: Context): Int = runCatching {
    val a = JSONArray(widgetPrefs(context).getString("tasks", "[]")); var c=0
    for(i in 0 until a.length()) if(!a.getJSONObject(i).optBoolean("done")) c++
    c
}.getOrDefault(0)
private fun firstGoal(context: Context): Pair<String,Int> = runCatching {
    val a=JSONArray(widgetPrefs(context).getString("goals","[]")); if(a.length()==0) Pair("No goal yet",0) else a.getJSONObject(0).let{Pair(it.optString("title","Goal"),it.optInt("progress"))}
}.getOrDefault(Pair("No goal yet",0))

class R713TodayWidget : AppWidgetProvider() {
    override fun onUpdate(context: Context, manager: AppWidgetManager, ids: IntArray) {
        val private = widgetPrefs(context).getBoolean("widgetPrivacy",false)
        ids.forEach { id ->
            val rv=RemoteViews(context.packageName,R.layout.r713_widget_today)
            rv.setTextViewText(R.id.widget_title, if(private) "PlanJoy" else "Today")
            rv.setTextViewText(R.id.widget_value, if(private) "•••" else remainingTasks(context).toString())
            rv.setTextViewText(R.id.widget_note, if(private) "Private widget" else "plans waiting gently")
            manager.updateAppWidget(id,rv)
        }
    }
}

class R713FocusWidget : AppWidgetProvider() {
    override fun onUpdate(context: Context, manager: AppWidgetManager, ids: IntArray) {
        val private = widgetPrefs(context).getBoolean("widgetPrivacy",false)
        val min=widgetPrefs(context).getInt("focusMinutes",0)
        ids.forEach { id ->
            val rv=RemoteViews(context.packageName,R.layout.r713_widget_focus)
            rv.setTextViewText(R.id.widget_title, "Focus")
            rv.setTextViewText(R.id.widget_value, if(private) "•••" else "${min}m")
            rv.setTextViewText(R.id.widget_note, "quiet time logged")
            manager.updateAppWidget(id,rv)
        }
    }
}

class R713GoalWidget : AppWidgetProvider() {
    override fun onUpdate(context: Context, manager: AppWidgetManager, ids: IntArray) {
        val private = widgetPrefs(context).getBoolean("widgetPrivacy",false)
        val (name,progress)=firstGoal(context)
        ids.forEach { id ->
            val rv=RemoteViews(context.packageName,R.layout.r713_widget_goal)
            rv.setTextViewText(R.id.widget_title, if(private) "Goal" else name)
            rv.setTextViewText(R.id.widget_value, if(private) "•••" else "$progress%")
            rv.setTextViewText(R.id.widget_note, "one step at a time")
            manager.updateAppWidget(id,rv)
        }
    }
}
