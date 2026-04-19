import Foundation

struct CaptureEvent {
    let id: String
    let source: String
    let senderName: String?
    let content: String
    let timestamp: Date
    let blockedByWhitelist: Bool
    let metadata: [String: String]
}
