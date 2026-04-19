import Foundation

enum TrustedContactMatcher {
    static func matches(senderName: String?, contacts: [String]) -> Bool {
        let normalizedSender = normalize(senderName ?? "")
        guard !normalizedSender.isEmpty else {
            return false
        }

        return contacts.contains { contact in
            let normalizedContact = normalize(contact)
            return !normalizedContact.isEmpty &&
                (normalizedContact == normalizedSender ||
                 normalizedSender.contains(normalizedContact) ||
                 normalizedContact.contains(normalizedSender))
        }
    }

    static func normalize(_ value: String) -> String {
        return value
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .joined()
    }
}
