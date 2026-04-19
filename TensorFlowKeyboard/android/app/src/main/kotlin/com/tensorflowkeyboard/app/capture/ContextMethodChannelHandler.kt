package com.tensorflowkeyboard.app.capture

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.provider.Settings
import androidx.core.app.NotificationManagerCompat
import io.flutter.plugin.common.BinaryMessenger
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel

class ContextMethodChannelHandler(
    private val context: Context,
    binaryMessenger: BinaryMessenger,
) : MethodChannel.MethodCallHandler {
    private val appContext = context.applicationContext
    private val channel = MethodChannel(binaryMessenger, ContextChannels.METHOD_CHANNEL)

    fun bind() {
        channel.setMethodCallHandler(this)
    }

    fun unbind() {
        channel.setMethodCallHandler(null)
    }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "openAccessibilitySettings" -> {
                launchIntent(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
                result.success(null)
            }

            "openNotificationSettings" -> {
                launchIntent(Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS"))
                result.success(null)
            }

            "getContextSummary" -> {
                val coordinator = CaptureCoordinator.getInstance(appContext)
                result.success(
                    coordinator.diagnostics() + mapOf(
                        "accessibilityEnabled" to isAccessibilityEnabled(),
                        "notificationEnabled" to isNotificationListenerEnabled(),
                    ),
                )
            }

            else -> result.notImplemented()
        }
    }

    private fun launchIntent(intent: Intent) {
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        appContext.startActivity(intent)
    }

    private fun isAccessibilityEnabled(): Boolean {
        val enabledServices = Settings.Secure.getString(
            appContext.contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES,
        ).orEmpty()
        val expected = ComponentName(appContext, SafeAccessibilityService::class.java).flattenToString()
        return enabledServices.contains(expected)
    }

    private fun isNotificationListenerEnabled(): Boolean {
        return NotificationManagerCompat.getEnabledListenerPackages(appContext)
            .contains(appContext.packageName)
    }
}
