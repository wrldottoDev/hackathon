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
  static const String _keyboardDraftSource = 'Keyboard Draft';

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

    if (appLostFocus && packageName == null) {
      purge(reason: 'Foco perdido o app fuera de vigilancia.');
      return;
    }

    final appLabel = item.metadata['appLabel'] ?? packageName;
    _status = surveillance
        ? 'Vigilancia local activa en $appLabel.'
        : 'Teclado activo en $appLabel. Revisión por texto local habilitada.';
    notifyListeners();
  }

  void synchronizeHostState({
    required String? activeAppPackage,
    required bool surveillanceEnabled,
    String? appLabel,
  }) {
    _activeAppPackage = activeAppPackage;
    _surveillanceEnabled = surveillanceEnabled;

    if (activeAppPackage == null) {
      _status = 'Esperando app activa para iniciar revisión local.';
      notifyListeners();
      return;
    }

    final visibleLabel = appLabel ?? activeAppPackage;
    _status = surveillanceEnabled
        ? 'Vigilancia local activa en $visibleLabel.'
        : 'Teclado activo en $visibleLabel. Revisión por texto local habilitada.';
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

  bool recordKeyboardDraft(
    String text, {
    bool force = false,
    String? fallbackOriginApp,
  }) {
    return _record(
      source: _keyboardDraftSource,
      payload: text,
      force: force,
      fallbackOriginApp: fallbackOriginApp,
      replaceExistingSource: _keyboardDraftSource,
    );
  }

  bool recordSpeechInput(String text) {
    return _record(
      source: 'Speech To Text',
      payload: text,
    );
  }

  void clearKeyboardDraft() {
    _entries.removeWhere((entry) => entry.source == _keyboardDraftSource);
    notifyListeners();
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
    bool force = false,
    String? fallbackOriginApp,
    String? replaceExistingSource,
  }) {
    final trimmed = payload.trim();
    if (trimmed.isEmpty) {
      if (replaceExistingSource != null) {
        _entries.removeWhere((entry) => entry.source == replaceExistingSource);
        notifyListeners();
      }
      return false;
    }

    if (_suspended) {
      _status = 'Modo suspendido activo. Evento descartado.';
      notifyListeners();
      return false;
    }

    final originApp = _activeAppPackage ?? fallbackOriginApp;
    if (!force && (!_surveillanceEnabled || originApp == null)) {
      _status = 'Vigilancia inactiva. Evento no agregado.';
      notifyListeners();
      return false;
    }

    if (replaceExistingSource != null) {
      _entries.removeWhere((entry) => entry.source == replaceExistingSource);
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
        originApp: originApp ?? 'ime.local',
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
