package com.tensorflowkeyboard.app.ime

import io.flutter.plugin.common.BinaryMessenger
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel

class KeyboardMethodChannelHandler(
    private val delegate: KeyboardActionDelegate,
    binaryMessenger: BinaryMessenger,
) : MethodChannel.MethodCallHandler {
    private val channel = MethodChannel(binaryMessenger, KeyboardChannels.METHOD_CHANNEL)

    fun bind() {
        channel.setMethodCallHandler(this)
    }

    fun unbind() {
        channel.setMethodCallHandler(null)
    }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "commitText" -> {
                delegate.commitText(call.argument<String>("text").orEmpty())
                result.success(null)
            }

            "backspace" -> {
                delegate.backspace()
                result.success(null)
            }

            "enter" -> {
                delegate.enter()
                result.success(null)
            }

            "setSecureMode" -> {
                delegate.setSecureMode(call.argument<Boolean>("enabled") == true)
                result.success(null)
            }

            "openInputMethodSettings" -> {
                delegate.openInputMethodSettings()
                result.success(null)
            }

            "getKeyboardState" -> result.success(delegate.keyboardState())
            else -> result.notImplemented()
        }
    }
}
