package com.tensorflowkeyboard.app.capture

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

class SafeAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) {
            return
        }

        if (event.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ||
            event.eventType == AccessibilityEvent.TYPE_VIEW_FOCUSED
        ) {
            CaptureCoordinator.getInstance(applicationContext).noteAccessibilityHeartbeat(
                event.packageName?.toString(),
            )
        }
    }

    override fun onInterrupt() = Unit
}
