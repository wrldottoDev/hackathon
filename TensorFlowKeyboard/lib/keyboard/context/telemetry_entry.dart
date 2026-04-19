class TelemetryEntry {
  const TelemetryEntry({
    required this.source,
    required this.originApp,
    required this.payload,
    required this.timestamp,
  });

  final String source;
  final String originApp;
  final String payload;
  final DateTime timestamp;

  String get label => '[$source][$originApp] $payload';
}
