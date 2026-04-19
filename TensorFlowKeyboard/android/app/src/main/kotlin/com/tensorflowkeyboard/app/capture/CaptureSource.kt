package com.tensorflowkeyboard.app.capture

enum class CaptureSource(val wireValue: String) {
    KEYBOARD("keyboard"),
    ACCESSIBILITY_STUB("accessibility_stub"),
    NOTIFICATION_STUB("notification_stub"),
    SIMULATION("simulation"),
}
