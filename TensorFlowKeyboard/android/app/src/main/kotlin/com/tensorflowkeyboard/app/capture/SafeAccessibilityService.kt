package com.tensorflowkeyboard.app.capture

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

class SafeAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) {
            return
        }

        val packageName = event.packageName?.toString() ?: return
        val coordinator = CaptureCoordinator.getInstance(applicationContext)
        coordinator.updateActiveApp(packageName)

        if (event.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED ||
            event.eventType == AccessibilityEvent.TYPE_VIEW_FOCUSED ||
            event.eventType == AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
        ) {
            coordinator.noteAccessibilityHeartbeat(packageName)
        }
    }

    override fun onInterrupt() = Unit

    private fun eventTypeLabel(eventType: Int): String {
        return when (eventType) {
            AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED -> "TYPE_WINDOW_CONTENT_CHANGED"
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> "TYPE_WINDOW_STATE_CHANGED"
            AccessibilityEvent.TYPE_VIEW_FOCUSED -> "TYPE_VIEW_FOCUSED"
            else -> "UNKNOWN"
        }
    }
}
