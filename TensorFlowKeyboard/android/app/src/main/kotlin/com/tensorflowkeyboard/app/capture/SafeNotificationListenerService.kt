package com.tensorflowkeyboard.app.capture

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification

class SafeNotificationListenerService : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        CaptureCoordinator.getInstance(applicationContext).noteNotificationHeartbeat(
            sbn?.packageName,
        )
    }
}
