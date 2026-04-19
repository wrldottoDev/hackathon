package com.tensorflowkeyboard.app.capture

import android.content.Context
import java.util.UUID

class CaptureCoordinator private constructor(
    context: Context,
) {
    private val appContext = context.applicationContext
    private val trustedContactsStore = TrustedContactsStore(appContext)
    private val buffer = InMemoryMessageBuffer(capacity = 20)

    @Volatile
    private var lastAccessibilityPackage: String? = null

    @Volatile
    private var lastNotificationPackage: String? = null

    @Volatile
    private var activeAppPackage: String? = null

    @Volatile
    private var surveillanceActive: Boolean = false

    fun setTrustedContacts(contacts: List<String>) {
        trustedContactsStore.setContacts(contacts)
    }

    fun getTrustedContacts(): List<String> {
        return trustedContactsStore.getContacts()
    }

    fun getBufferedEvents(): List<CaptureEvent> {
        return buffer.snapshot()
    }

    fun acceptKeyboardDraft(content: String) {
        ingest(
            source = CaptureSource.KEYBOARD,
            senderName = null,
            content = content,
            metadata = mapOf("origin" to "ime"),
        )
    }

    fun acceptSimulation(senderName: String?, content: String) {
        ingest(
            source = CaptureSource.SIMULATION,
            senderName = senderName,
            content = content,
            metadata = mapOf("origin" to "native_debug"),
        )
    }

    fun noteAccessibilityHeartbeat(packageName: String?) {
        lastAccessibilityPackage = packageName
    }

    fun noteNotificationHeartbeat(packageName: String?) {
        lastNotificationPackage = packageName
    }

    fun updateActiveApp(packageName: String?) {
        activeAppPackage = packageName
        surveillanceActive = MonitoredMessagingApps.contains(packageName)
        emitAppState(
            packageName = packageName,
            surveillance = surveillanceActive,
            appLostFocus = !surveillanceActive,
        )
    }

    fun emitAccessibilitySignal(
        packageName: String,
        eventTypeLabel: String,
    ) {
        // Privacy boundary:
        // We intentionally do NOT traverse window nodes or extract third-party text.
        // Only a redacted signal is emitted and it exists in memory while the process lives.
        emitSignal(
            source = CaptureSource.ACCESSIBILITY_STUB,
            content = "${MonitoredMessagingApps.labelFor(packageName)} content changed. Text redacted by design.",
            metadata = mapOf(
                "packageName" to packageName,
                "appLabel" to MonitoredMessagingApps.labelFor(packageName),
                "eventType" to eventTypeLabel,
                "privacy" to "ram_only_redacted_signal",
            ),
        )
    }

    fun emitNotificationSignal(packageName: String) {
        // Privacy boundary:
        // We intentionally do NOT read notification title/body from third-party apps.
        // Only a redacted signal is emitted and it exists in memory while the process lives.
        emitSignal(
            source = CaptureSource.NOTIFICATION_STUB,
            content = "${MonitoredMessagingApps.labelFor(packageName)} notification received. Notification text redacted by design.",
            metadata = mapOf(
                "packageName" to packageName,
                "appLabel" to MonitoredMessagingApps.labelFor(packageName),
                "privacy" to "ram_only_redacted_signal",
            ),
        )
    }

    fun diagnostics(): Map<String, Any?> {
        return mapOf(
            "bufferSize" to getBufferedEvents().size,
            "trustedContactsCount" to getTrustedContacts().size,
            "lastAccessibilityPackage" to lastAccessibilityPackage,
            "lastNotificationPackage" to lastNotificationPackage,
            "activeAppPackage" to activeAppPackage,
            "surveillanceActive" to surveillanceActive,
        )
    }

    private fun ingest(
        source: CaptureSource,
        senderName: String?,
        content: String,
        metadata: Map<String, Any?>,
    ) {
        val trimmedContent = content.trim()
        if (trimmedContent.isEmpty()) {
            return
        }

        if (trustedContactsStore.isTrusted(senderName)) {
            NativeEventDispatcher.emit(
                CaptureEvent(
                    id = UUID.randomUUID().toString(),
                    source = source,
                    senderName = senderName,
                    content = "",
                    timestamp = System.currentTimeMillis(),
                    blockedByWhitelist = true,
                    metadata = metadata + ("reason" to "trusted_contact_match"),
                ),
            )
            return
        }

        val event = CaptureEvent(
            id = UUID.randomUUID().toString(),
            source = source,
            senderName = senderName,
            content = trimmedContent,
            timestamp = System.currentTimeMillis(),
            metadata = metadata,
        )
        buffer.add(event)
        NativeEventDispatcher.emit(event)
    }

    private fun emitSignal(
        source: CaptureSource,
        content: String,
        metadata: Map<String, Any?>,
    ) {
        NativeEventDispatcher.emit(
            CaptureEvent(
                id = UUID.randomUUID().toString(),
                source = source,
                senderName = null,
                content = content,
                timestamp = System.currentTimeMillis(),
                metadata = metadata,
            ),
        )
    }

    private fun emitAppState(
        packageName: String?,
        surveillance: Boolean,
        appLostFocus: Boolean,
    ) {
        NativeEventDispatcher.emit(
            CaptureEvent(
                id = UUID.randomUUID().toString(),
                source = CaptureSource.ACCESSIBILITY_STUB,
                senderName = null,
                content = if (surveillance) {
                    "Active app entered surveillance list."
                } else {
                    "Active app not in surveillance list."
                },
                timestamp = System.currentTimeMillis(),
                metadata = mapOf(
                    "packageName" to packageName,
                    "appLabel" to MonitoredMessagingApps.labelFor(packageName),
                    "surveillanceActive" to surveillance,
                    "appLostFocus" to appLostFocus,
                    "privacy" to "package_name_only",
                ),
            ),
        )
    }

    companion object {
        @Volatile
        private var instance: CaptureCoordinator? = null

        fun getInstance(context: Context): CaptureCoordinator {
            return instance ?: synchronized(this) {
                instance ?: CaptureCoordinator(context).also { instance = it }
            }
        }
    }
}
