package com.tensorflowkeyboard.app.capture

import android.content.Context

class TrustedContactsStore(
    context: Context,
) {
    private val preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun setContacts(contacts: List<String>) {
        preferences.edit().putStringSet(KEY_CONTACTS, contacts.toSet()).apply()
    }

    fun getContacts(): List<String> {
        return preferences.getStringSet(KEY_CONTACTS, emptySet()).orEmpty().sorted()
    }

    fun isTrusted(senderName: String?): Boolean {
        val normalizedSender = normalize(senderName)
        if (normalizedSender.isEmpty()) {
            return false
        }

        return getContacts().any { contact ->
            val normalizedContact = normalize(contact)
            normalizedContact.isNotEmpty() && (
                normalizedSender == normalizedContact ||
                    normalizedSender.contains(normalizedContact) ||
                    normalizedContact.contains(normalizedSender)
                )
        }
    }

    private fun normalize(value: String?): String {
        return value.orEmpty()
            .lowercase()
            .replace(NON_ALPHANUMERIC, "")
    }

    private companion object {
        private const val PREFS_NAME = "trusted_contacts_store"
        private const val KEY_CONTACTS = "contacts"
        private val NON_ALPHANUMERIC = Regex("[^a-z0-9]")
    }
}
