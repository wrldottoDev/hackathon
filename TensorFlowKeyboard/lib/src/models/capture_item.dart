enum CaptureSource {
  keyboard,
  accessibilityStub,
  notificationStub,
  simulation,
}

extension CaptureSourceWire on CaptureSource {
  String get wireValue => switch (this) {
        CaptureSource.keyboard => 'keyboard',
        CaptureSource.accessibilityStub => 'accessibility_stub',
        CaptureSource.notificationStub => 'notification_stub',
        CaptureSource.simulation => 'simulation',
      };

  String get label => switch (this) {
        CaptureSource.keyboard => 'Keyboard',
        CaptureSource.accessibilityStub => 'Accessibility Stub',
        CaptureSource.notificationStub => 'Notification Stub',
        CaptureSource.simulation => 'Simulation',
      };

  static CaptureSource fromWire(String? raw) {
    return switch (raw) {
      'keyboard' => CaptureSource.keyboard,
      'accessibility_stub' => CaptureSource.accessibilityStub,
      'notification_stub' => CaptureSource.notificationStub,
      'simulation' => CaptureSource.simulation,
      _ => CaptureSource.simulation,
    };
  }
}

class CaptureItem {
  const CaptureItem({
    required this.id,
    required this.source,
    required this.content,
    required this.timestamp,
    this.senderName,
    this.blockedByWhitelist = false,
    this.metadata = const <String, dynamic>{},
  });

  final String id;
  final CaptureSource source;
  final String content;
  final DateTime timestamp;
  final String? senderName;
  final bool blockedByWhitelist;
  final Map<String, dynamic> metadata;

  CaptureItem copyWith({
    String? id,
    CaptureSource? source,
    String? content,
    DateTime? timestamp,
    String? senderName,
    bool? blockedByWhitelist,
    Map<String, dynamic>? metadata,
  }) {
    return CaptureItem(
      id: id ?? this.id,
      source: source ?? this.source,
      content: content ?? this.content,
      timestamp: timestamp ?? this.timestamp,
      senderName: senderName ?? this.senderName,
      blockedByWhitelist: blockedByWhitelist ?? this.blockedByWhitelist,
      metadata: metadata ?? this.metadata,
    );
  }

  factory CaptureItem.fromMap(Map<Object?, Object?> map) {
    final metadata = (map['metadata'] as Map<Object?, Object?>?) ?? const {};
    return CaptureItem(
      id: (map['id'] ?? '').toString(),
      source: CaptureSourceWire.fromWire(map['source']?.toString()),
      senderName: map['senderName']?.toString(),
      content: (map['content'] ?? '').toString(),
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        _parseInt(map['timestamp']),
        isUtc: false,
      ),
      blockedByWhitelist: map['blockedByWhitelist'] == true,
      metadata: metadata.map(
        (key, value) => MapEntry(key.toString(), value),
      ),
    );
  }

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'id': id,
      'source': source.wireValue,
      'senderName': senderName,
      'content': content,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'blockedByWhitelist': blockedByWhitelist,
      'metadata': metadata,
    };
  }

  static int _parseInt(Object? raw) {
    if (raw is int) {
      return raw;
    }
    return int.tryParse(raw?.toString() ?? '') ?? 0;
  }
}
