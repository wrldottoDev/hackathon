package com.tensorflowkeyboard.app.ime

import android.content.Context
import android.content.Intent
import android.provider.Settings

class PreviewKeyboardDelegate(
    private val context: Context,
) : KeyboardActionDelegate {
    private var secureModeEnabled = false

    override fun commitText(text: String) = Unit

    override fun backspace() = Unit

    override fun enter() = Unit

    override fun setSecureMode(enabled: Boolean) {
        secureModeEnabled = enabled
    }

    override fun openInputMethodSettings() {
        context.startActivity(
            Intent(Settings.ACTION_INPUT_METHOD_SETTINGS).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            },
        )
    }

    override fun keyboardState(): Map<String, Any?> {
        return mapOf(
            "hostMode" to "preview",
            "connected" to false,
            "secureMode" to secureModeEnabled,
        )
    }
}
