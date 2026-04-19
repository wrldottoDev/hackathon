package com.tensorflowkeyboard.app

import com.tensorflowkeyboard.app.capture.ContextChannels
import com.tensorflowkeyboard.app.capture.ContextEventStreamHandler
import com.tensorflowkeyboard.app.capture.ContextMethodChannelHandler
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import com.tensorflowkeyboard.app.ime.KeyboardMethodChannelHandler
import com.tensorflowkeyboard.app.ime.PreviewKeyboardDelegate
import io.flutter.plugin.common.EventChannel

class MainActivity : FlutterActivity() {
    private var channelHandler: KeyboardMethodChannelHandler? = null
    private var contextMethodHandler: ContextMethodChannelHandler? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        channelHandler = KeyboardMethodChannelHandler(
            delegate = PreviewKeyboardDelegate(this),
            binaryMessenger = flutterEngine.dartExecutor.binaryMessenger,
        ).also { it.bind() }

        contextMethodHandler = ContextMethodChannelHandler(
            context = this,
            binaryMessenger = flutterEngine.dartExecutor.binaryMessenger,
        ).also { it.bind() }

        EventChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            ContextChannels.EVENT_CHANNEL,
        ).setStreamHandler(ContextEventStreamHandler())
    }

    override fun onDestroy() {
        channelHandler?.unbind()
        contextMethodHandler?.unbind()
        super.onDestroy()
    }
}
