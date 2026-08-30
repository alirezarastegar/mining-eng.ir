package com.planjoy.r7

data class TaskModel(val id:String,val title:String,val note:String="",val category:String="Inbox",val startUtc:Long=0,val endUtc:Long=0,val allDay:Boolean=false,val priority:Int=0,val quadrant:Int=0,val completed:Boolean=false,val completedUtc:Long=0,val planned:Boolean=true,val deadlineUtc:Long=0,val calendarSystem:Int=0,val sourceY:Int=0,val sourceM:Int=0,val sourceD:Int=0,val parentId:String="",val recurrenceId:String="",val recurrenceCalendar:Int=-1,val recurrenceFrequency:Int=0,val recurrenceInterval:Int=0,val anchorDay:Int=0,val anchorMonth:Int=0,val recurrenceUntil:Long=0,val occurrenceLimit:Int=0,val reminderLead:Int=-1)
data class GoalModel(val id:String,val title:String,val description:String="",val startUtc:Long=0,val endUtc:Long=0,val status:Int=0,val progress:Int=0,val calendarSystem:Int=0)
data class MilestoneModel(val id:String,val title:String,val goalId:String,val dueUtc:Long=0,val sortOrder:Int=0,val completed:Boolean=false,val parentId:String="",val weight:Int=1,val calendarSystem:Int=0,val sourceY:Int=0,val sourceM:Int=0,val sourceD:Int=0)
data class ReviewModel(val id:String,val dateKey:String,val calendarSystem:Int=0,val sourceY:Int=0,val sourceM:Int=0,val sourceD:Int=0,val title:String="",val diary:String="",val mood:Int=3)
data class FocusModel(val id:String,val taskId:String="",val title:String="Focus",val startedUtc:Long,val endedUtc:Long,val plannedSeconds:Int,val actualSeconds:Int,val completed:Boolean=true)
data class RewardModel(val id:String,val sourceKey:String,val eventType:String,val entityType:String,val entityId:String,val xpDelta:Int,val coinsDelta:Int,val eventUtc:Long)
data class SyncOp(val seq:Long=0,val opId:String,val deviceId:String="",val type:String,val entityId:String,val kind:Int,val revision:Long,val hlcUtc:Long,val hlcCounter:Long,val payload:String)
data class EntityRow(val type:String,val id:String,val payload:String,val tombstone:Boolean,val revision:Long,val hlcUtc:Long,val hlcCounter:Long,val deviceId:String)

data class CountdownModel(val id:String,val title:String,val targetUtc:Long,val style:Int=0,val pinned:Boolean=false,val reminder:Boolean=true,val note:String="")
data class R73Conflict(val id:String,val type:String,val entityId:String,val localPayload:String,val remotePayload:String,val localRevision:Long,val remoteRevision:Long,val winner:Int,val createdUtc:Long,val resolvedUtc:Long,val resolution:String)
