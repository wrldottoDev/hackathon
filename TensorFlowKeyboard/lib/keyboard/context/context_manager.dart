import 'dart:async';
import 'dart:collection';

import 'package:flutter/widgets.dart';

import '../../src/models/capture_item.dart';
import '../../src/services/whitelist_service.dart';
import 'telemetry_entry.dart';

class ContextManager extends ChangeNotifier {
  ContextManager({
    required this.whitelist,
    this.capacity = 20,
    Duration? retentionWindow,
  })  : assert(capacity > 0, 'capacity must be greater than zero'),
        _retentionWindow = retentionWindow ?? const Duration(minutes: 5) {
    _startPurgeTimer();
  }

  final WhitelistService whitelist;
  final int capacity;
  final Duration _retentionWindow;
  final ListQueue<TelemetryEntry> _entries = ListQueue<TelemetryEntry>();

  Timer? _purgeTimer;
  String? _activeAppPackage;
  bool _surveillanceEnabled = false;
  bool _suspended = false;
  String _status = 'Esperando estado de telemetría local.';

  List<TelemetryEntry> get entries => List<TelemetryEntry>.unmodifiable(
        _entries.toList().reversed,
      );
  String get status => _status;
  String? get activeAppPackage => _activeAppPackage;
  bool get surveillanceEnabled => _surveillanceEnabled;
  bool get suspended => _suspended;

  void reportSystemStatus(String message) {
    _status = message;
    notifyListeners();
  }

  void handleNativeSignal(CaptureItem item) {
    final packageName = item.metadata['packageName']?.toString();
    final surveillance = item.metadata['surveillanceActive'] == true;
    final appLostFocus = item.metadata['appLostFocus'] == true;

    _activeAppPackage = packageName;
    _surveillanceEnabled = surveillance;

    if (appLostFocus || !_surveillanceEnabled) {
      purge(reason: 'Foco perdido o app fuera de vigilancia.');
      return;
    }

    _status = surveillance
        ? 'Vigilancia local activa en ${item.metadata['appLabel'] ?? packageName}.'
        : 'Vigilancia local inactiva.';
    notifyListeners();
  }

  void handleConversationLabel(String? conversationLabel) {
    final trimmed = conversationLabel?.trim() ?? '';
    if (trimmed.isEmpty) {
      if (_suspended) {
        _suspended = false;
        _status = 'Modo suspendido desactivado.';
        notifyListeners();
      }
      return;
    }

    if (whitelist.matches(trimmed)) {
      _suspended = true;
      purge(reason: 'Contacto de confianza detectado.');
      return;
    }

    if (_suspended) {
      _suspended = false;
      _status = 'Modo suspendido desactivado.';
      notifyListeners();
    }
  }

  bool recordKeyboardInput(String text) {
    return _record(
      source: 'Keyboard',
      payload: text,
    );
  }

  bool recordSpeechInput(String text) {
    return _record(
      source: 'Speech To Text',
      payload: text,
    );
  }

  void handleAppLifecycleChange(AppLifecycleState state) {
    if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused ||
        state == AppLifecycleState.detached) {
      purge(reason: 'La app perdió foco.');
    }
  }

  void purge({String reason = 'Purga solicitada.'}) {
    if (_entries.isNotEmpty) {
      _entries.clear();
    }
    _status = 'Buffer purgado: $reason';
    notifyListeners();
  }

  bool _record({
    required String source,
    required String payload,
  }) {
    final trimmed = payload.trim();
    if (trimmed.isEmpty) {
      return false;
    }

    if (_suspended) {
      _status = 'Modo suspendido activo. Evento descartado.';
      notifyListeners();
      return false;
    }

    if (!_surveillanceEnabled || _activeAppPackage == null) {
      _status = 'Vigilancia inactiva. Evento no agregado.';
      notifyListeners();
      return false;
    }

    // Privacy boundary:
    // This telemetry buffer lives only in volatile RAM.
    // It is purged on timer or focus loss and is not written to disk here.
    if (_entries.length == capacity) {
      _entries.removeFirst();
    }
    _entries.addLast(
      TelemetryEntry(
        source: source,
        originApp: _activeAppPackage!,
        payload: trimmed,
        timestamp: DateTime.now(),
      ),
    );
    _status = 'Evento local agregado desde $source.';
    notifyListeners();
    return true;
  }

  void _startPurgeTimer() {
    _purgeTimer?.cancel();
    _purgeTimer = Timer.periodic(_retentionWindow, (_) {
      purge(reason: 'Retención de 5 minutos agotada.');
    });
  }

  @override
  void dispose() {
    _purgeTimer?.cancel();
    super.dispose();
  }
}
