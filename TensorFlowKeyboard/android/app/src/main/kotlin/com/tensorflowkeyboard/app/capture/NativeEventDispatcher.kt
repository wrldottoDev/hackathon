package com.tensorflowkeyboard.app.capture

import android.os.Handler
import android.os.Looper
import io.flutter.plugin.common.EventChannel

object NativeEventDispatcher {
    private val mainHandler = Handler(Looper.getMainLooper())
    private var sink: EventChannel.EventSink? = null

    fun attach(eventSink: EventChannel.EventSink?) {
        sink = eventSink
    }

    fun emit(event: CaptureEvent) {
        mainHandler.post {
            sink?.success(event.toMap())
        }
    }
}
