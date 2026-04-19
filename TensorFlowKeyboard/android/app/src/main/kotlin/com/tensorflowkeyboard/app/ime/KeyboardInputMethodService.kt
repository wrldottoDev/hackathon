package com.tensorflowkeyboard.app.ime

import android.content.Intent
import android.inputmethodservice.InputMethodService
import android.provider.Settings
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import com.tensorflowkeyboard.app.capture.ContextChannels
import com.tensorflowkeyboard.app.capture.ContextEventStreamHandler
import com.tensorflowkeyboard.app.capture.ContextMethodChannelHandler
import io.flutter.embedding.android.FlutterView
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.EventChannel

class KeyboardInputMethodService : InputMethodService(), KeyboardActionDelegate {
    private lateinit var flutterEngine: FlutterEngine
    private lateinit var channelHandler: KeyboardMethodChannelHandler
    private lateinit var contextMethodHandler: ContextMethodChannelHandler

    private var inputRoot: FrameLayout? = null
    private var flutterView: FlutterView? = null
    private var contextEventChannel: EventChannel? = null
    private var secureModeEnabled = false

    override fun onCreate() {
        super.onCreate()
        flutterEngine = KeyboardFlutterEngineStore.getOrCreate(this)
        channelHandler = KeyboardMethodChannelHandler(
            delegate = this,
            binaryMessenger = flutterEngine.dartExecutor.binaryMessenger,
        )
        channelHandler.bind()
        contextMethodHandler = ContextMethodChannelHandler(
            context = this,
            binaryMessenger = flutterEngine.dartExecutor.binaryMessenger,
        )
        contextMethodHandler.bind()
        contextEventChannel = EventChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            ContextChannels.EVENT_CHANNEL,
        ).also { channel ->
            channel.setStreamHandler(ContextEventStreamHandler())
        }
    }

    override fun onCreateInputView(): View {
        if (inputRoot == null) {
            inputRoot = FrameLayout(this).apply {
                layoutParams = FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                )
                minimumHeight = (280 * resources.displayMetrics.density).toInt()
            }
        }

        if (flutterView == null) {
            flutterView = FlutterView(this).apply {
                layoutParams = FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.MATCH_PARENT,
                )
            }
        }

        (flutterView?.parent as? ViewGroup)?.removeView(flutterView)
        inputRoot?.removeAllViews()
        inputRoot?.addView(flutterView)
        attachFlutterUi()
        return inputRoot!!
    }

    override fun onEvaluateFullscreenMode(): Boolean = false

    override fun onStartInputView(info: android.view.inputmethod.EditorInfo?, restarting: Boolean) {
        super.onStartInputView(info, restarting)
        attachFlutterUi()
    }

    override fun onFinishInputView(finishingInput: Boolean) {
        detachFlutterUi()
        super.onFinishInputView(finishingInput)
    }

    override fun onDestroy() {
        detachFlutterUi()
        channelHandler.unbind()
        contextMethodHandler.unbind()
        contextEventChannel?.setStreamHandler(null)
        contextEventChannel = null
        super.onDestroy()
    }

    override fun commitText(text: String) {
        if (text.isEmpty()) {
            return
        }
        currentInputConnection?.commitText(text, 1)
    }

    override fun backspace() {
        currentInputConnection?.deleteSurroundingText(1, 0)
    }

    override fun enter() {
        currentInputConnection?.commitText("\n", 1)
    }

    override fun setSecureMode(enabled: Boolean) {
        secureModeEnabled = enabled
    }

    override fun openInputMethodSettings() {
        startActivity(
            Intent(Settings.ACTION_INPUT_METHOD_SETTINGS).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            },
        )
    }

    override fun keyboardState(): Map<String, Any?> {
        return mapOf(
            "hostMode" to "ime",
            "connected" to (currentInputConnection != null),
            "secureMode" to secureModeEnabled,
        )
    }

    private fun attachFlutterUi() {
        val view = flutterView ?: return
        if (view.getAttachedFlutterEngine() == null) {
            view.attachToFlutterEngine(flutterEngine)
        }
        flutterEngine.lifecycleChannel.appIsResumed()
    }

    private fun detachFlutterUi() {
        val view = flutterView ?: return
        flutterEngine.lifecycleChannel.appIsInactive()
        if (view.getAttachedFlutterEngine() != null) {
            view.detachFromFlutterEngine()
        }
    }
}
