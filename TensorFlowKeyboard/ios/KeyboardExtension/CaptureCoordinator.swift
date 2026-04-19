import Foundation

final class CaptureCoordinator {
    private let buffer = InMemoryMessageBuffer(capacity: 20)
    private let processor: (CaptureEvent) -> Void

    init(processor: @escaping (CaptureEvent) -> Void = { _ in }) {
        self.processor = processor
    }

    func acceptKeyboardDraft(content: String, senderName: String? = nil) {
        let trimmed = content.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return
        }

        let trustedContacts = UserDefaults.standard.stringArray(forKey: "trusted_contacts") ?? []
        guard !TrustedContactMatcher.matches(senderName: senderName, contacts: trustedContacts) else {
            return
        }

        let event = CaptureEvent(
            id: UUID().uuidString,
            source: "keyboard",
            senderName: senderName,
            content: trimmed,
            timestamp: Date(),
            blockedByWhitelist: false,
            metadata: ["origin": "ios_keyboard_extension"]
        )
        buffer.add(event)
        processor(event)
    }

    func recentItems() -> [CaptureEvent] {
        return buffer.snapshot()
    }
}
