package com.tensorflowkeyboard.app.capture

data class CaptureEvent(
    val id: String,
    val source: CaptureSource,
    val senderName: String?,
    val content: String,
    val timestamp: Long,
    val blockedByWhitelist: Boolean = false,
    val metadata: Map<String, Any?> = emptyMap(),
) {
    fun toMap(): Map<String, Any?> {
        return mapOf(
            "id" to id,
            "source" to source.wireValue,
            "senderName" to senderName,
            "content" to content,
            "timestamp" to timestamp,
            "blockedByWhitelist" to blockedByWhitelist,
            "metadata" to metadata,
        )
    }
}
