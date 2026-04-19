package com.tensorflowkeyboard.app.ime

interface KeyboardActionDelegate {
    fun commitText(text: String)
    fun backspace()
    fun enter()
    fun setSecureMode(enabled: Boolean)
    fun openInputMethodSettings()
    fun keyboardState(): Map<String, Any?>
}
