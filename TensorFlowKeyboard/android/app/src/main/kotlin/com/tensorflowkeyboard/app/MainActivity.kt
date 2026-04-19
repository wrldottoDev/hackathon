package com.tensorflowkeyboard.app

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import com.tensorflowkeyboard.app.ime.KeyboardMethodChannelHandler
import com.tensorflowkeyboard.app.ime.PreviewKeyboardDelegate

class MainActivity : FlutterActivity() {
    private var channelHandler: KeyboardMethodChannelHandler? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        channelHandler = KeyboardMethodChannelHandler(
            delegate = PreviewKeyboardDelegate(this),
            binaryMessenger = flutterEngine.dartExecutor.binaryMessenger,
        ).also { it.bind() }
    }

    override fun onDestroy() {
        channelHandler?.unbind()
        super.onDestroy()
    }
}
