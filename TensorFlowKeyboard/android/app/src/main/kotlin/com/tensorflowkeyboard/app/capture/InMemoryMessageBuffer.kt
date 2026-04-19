package com.tensorflowkeyboard.app.capture

class InMemoryMessageBuffer(
    private val capacity: Int,
) {
    private val items = ArrayDeque<CaptureEvent>(capacity)

    @Synchronized
    fun add(event: CaptureEvent) {
        if (items.size == capacity) {
            items.removeFirst()
        }
        items.addLast(event)
    }

    @Synchronized
    fun snapshot(): List<CaptureEvent> {
        return items.toList().asReversed()
    }
}
