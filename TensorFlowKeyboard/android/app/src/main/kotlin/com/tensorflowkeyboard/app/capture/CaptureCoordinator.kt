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

    fun diagnostics(): Map<String, Any?> {
        return mapOf(
            "bufferSize" to getBufferedEvents().size,
            "trustedContactsCount" to getTrustedContacts().size,
            "lastAccessibilityPackage" to lastAccessibilityPackage,
            "lastNotificationPackage" to lastNotificationPackage,
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
