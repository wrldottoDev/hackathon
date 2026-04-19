import Foundation

final class InMemoryMessageBuffer {
    private let capacity: Int
    private var items: [CaptureEvent] = []

    init(capacity: Int = 20) {
        self.capacity = capacity
    }

    func add(_ event: CaptureEvent) {
        if items.count == capacity {
            items.removeFirst()
        }
        items.append(event)
    }

    func snapshot() -> [CaptureEvent] {
        return items.reversed()
    }
}
