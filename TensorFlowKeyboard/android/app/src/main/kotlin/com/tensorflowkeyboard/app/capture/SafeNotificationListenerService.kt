package com.tensorflowkeyboard.app.capture

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

class SafeNotificationListenerService : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        val packageName = sbn?.packageName ?: return
        if (!MonitoredMessagingApps.contains(packageName)) {
            return
        }

        val coordinator = CaptureCoordinator.getInstance(applicationContext)
        coordinator.noteNotificationHeartbeat(packageName)
        coordinator.emitNotificationSignal(packageName)
    }
}
