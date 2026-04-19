package com.tensorflowkeyboard.app.capture

import io.flutter.plugin.common.EventChannel

class ContextEventStreamHandler : EventChannel.StreamHandler {
    override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
        NativeEventDispatcher.attach(events)
    }

    override fun onCancel(arguments: Any?) {
        NativeEventDispatcher.attach(null)
    }
}
