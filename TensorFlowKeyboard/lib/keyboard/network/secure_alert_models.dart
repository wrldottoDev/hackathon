import '../context/telemetry_entry.dart';

class SecureAlertLocation {
  const SecureAlertLocation({
    this.latitude,
    this.longitude,
    this.precisionMeters,
  });

  final double? latitude;
  final double? longitude;
  final double? precisionMeters;

  Map<String, dynamic> toJson() => <String, dynamic>{
        'latitude': latitude,
        'longitude': longitude,
        'precision_meters': precisionMeters,
      };
}

class SecureAlertBufferEntry {
  const SecureAlertBufferEntry({
    required this.source,
    required this.originApp,
    required this.payload,
    required this.timestamp,
  });

  factory SecureAlertBufferEntry.fromTelemetry(TelemetryEntry entry) {
    return SecureAlertBufferEntry(
      source: entry.source,
      originApp: entry.originApp,
      payload: entry.payload,
      timestamp: entry.timestamp,
    );
  }

  final String source;
  final String originApp;
  final String payload;
  final DateTime timestamp;

  Map<String, dynamic> toJson() => <String, dynamic>{
        'source': source,
        'origin_app': originApp,
        'payload': payload,
        'timestamp': timestamp.toUtc().toIso8601String(),
      };
}

class SecureAlertReport {
  const SecureAlertReport({
    required this.riskProbability,
    required this.bufferEntries,
    required this.metadata,
    required this.extractedEntities,
    required this.createdAt,
    this.location,
    this.originApp,
  });

  final double riskProbability;
  final SecureAlertLocation? location;
  final List<SecureAlertBufferEntry> bufferEntries;
  final Map<String, dynamic> metadata;
  final List<String> extractedEntities;
  final String? originApp;
  final DateTime createdAt;

  Map<String, dynamic> toJson() => <String, dynamic>{
        'riesgo_probabilidad': riskProbability,
        'ubicacion_gps': location?.toJson(),
        'entidades_extraidas': extractedEntities,
        'metadata': metadata,
        'buffer_texto': bufferEntries.map((entry) => entry.toJson()).toList(),
        'origen_app': originApp,
        'creado_en': createdAt.toUtc().toIso8601String(),
      };
}

class SecureAlertReceipt {
  const SecureAlertReceipt({
    required this.id,
    required this.hashDenuncia,
    required this.reciboInmutabilidad,
    required this.timestamp,
    required this.estadoInvestigacion,
  });

  factory SecureAlertReceipt.fromJson(Map<String, dynamic> json) {
    return SecureAlertReceipt(
      id: (json['id'] as num).toInt(),
      hashDenuncia: json['hash_denuncia']?.toString() ?? '',
      reciboInmutabilidad: json['recibo_inmutabilidad']?.toString() ?? '',
      timestamp: DateTime.parse(json['timestamp'].toString()),
      estadoInvestigacion: json['estado_investigacion']?.toString() ?? '',
    );
  }

  final int id;
  final String hashDenuncia;
  final String reciboInmutabilidad;
  final DateTime timestamp;
  final String estadoInvestigacion;
}
