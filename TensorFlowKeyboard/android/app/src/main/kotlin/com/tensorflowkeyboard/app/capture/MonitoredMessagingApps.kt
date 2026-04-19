package com.tensorflowkeyboard.app.capture

object MonitoredMessagingApps {
    private val labels = mapOf(
        "com.whatsapp" to "WhatsApp",
        "com.facebook.orca" to "Messenger",
        "com.instagram.android" to "Instagram",
    )

    fun contains(packageName: String?): Boolean = labels.containsKey(packageName)

    fun labelFor(packageName: String?): String {
        return labels[packageName] ?: packageName.orEmpty()
    }
}
