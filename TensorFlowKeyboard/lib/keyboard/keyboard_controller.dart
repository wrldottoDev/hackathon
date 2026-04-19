import 'dart:async';
import 'dart:convert';

import 'package:flutter/widgets.dart';

import '../src/services/whitelist_service.dart';
import 'alerts/local_alert_notification_service.dart';
import 'context/context_manager.dart';
import 'context/native_context_bridge.dart';
import 'context/speech_to_text_bridge.dart';
import 'context/telemetry_entry.dart';
import 'context/trusted_contacts_service.dart';
import 'keyboard_method_channel.dart';
import 'ml/risk_assessment.dart';
import 'ml/text_classifier.dart';
import 'network/secure_alert_models.dart';

class LocalReportPreview {
  const LocalReportPreview({
    required this.createdAt,
    required this.originApp,
    required this.eventCount,
    required this.riskCategoryLabel,
    required this.signals,
    required this.comment,
  });

  final DateTime createdAt;
  final String? originApp;
  final int eventCount;
  final String riskCategoryLabel;
  final List<String> signals;
  final String comment;
}

class KeyboardController extends ChangeNotifier {
  KeyboardController({
    KeyboardMethodChannel? methodChannel,
    WhitelistService? whitelistService,
    TrustedContactsService? trustedContactsService,
    LocalAlertNotificationService? notificationService,
  })  : _methodChannel = methodChannel ?? const KeyboardMethodChannel(),
        whitelist = whitelistService ?? WhitelistService(),
        _ownsWhitelist = whitelistService == null,
        _notificationService =
            notificationService ?? LocalAlertNotificationService.instance,
        _ownsTrustedContacts = trustedContactsService == null {
    trustedContacts = trustedContactsService ??
        TrustedContactsService(
          whitelist: whitelist,
        );
    contextManager.addListener(_handleContextChanged);
    whitelist.addListener(notifyListeners);
    speechBridge.addListener(notifyListeners);
    trustedContacts.addListener(notifyListeners);
    _notificationCommandsSubscription =
        _notificationService.commands.listen(_handleNotificationCommand);
  }

  final KeyboardMethodChannel _methodChannel;
  final bool _ownsWhitelist;
  final bool _ownsTrustedContacts;
  final LocalAlertNotificationService _notificationService;
  final WhitelistService whitelist;

  late final ContextManager contextManager = ContextManager(
    whitelist: whitelist,
  );
  late final NativeContextBridge _nativeContextBridge = NativeContextBridge(
    contextManager: contextManager,
  );
  late final SpeechToTextBridge speechBridge = SpeechToTextBridge(
    contextManager: contextManager,
  );
  late final TrustedContactsService trustedContacts;
  final TextClassifier _textClassifier = TextClassifier();

  StreamSubscription<LocalAlertCommand>? _notificationCommandsSubscription;

  static const List<String> securityAlerts = <String>[
    'Edad + números',
    'Ofertas laborales',
    'Amenazas íntimas',
    'Fraude bancario',
  ];

  String _draftPreview = '';
  bool _secureModeEnabled = false;
  String _hostMode = 'preview';
  bool _nativeConnected = false;
  Map<String, dynamic> _contextSummary = const <String, dynamic>{};
  RiskAssessment _riskAssessment = RiskAssessment.idle;
  Timer? _analysisDebounce;
  int _analysisGeneration = 0;
  bool _sendingAlert = false;
  String _alertDeliveryStatus = 'No se ha generado ninguna denuncia local.';
  SecureAlertReceipt? _lastReceipt;
  LocalReportPreview? _lastLocalReport;
  String? _lastAlertFingerprint;
  bool _reportFormVisible = false;
  bool _reportIntentConfirmed = false;
  String _reportComment = '';

  String get draftPreview => _draftPreview;
  bool get secureModeEnabled => _secureModeEnabled;
  String get hostMode => _hostMode;
  bool get nativeConnected => _nativeConnected;
  Map<String, dynamic> get contextSummary => _contextSummary;
  RiskAssessment get riskAssessment => _riskAssessment;
  bool get hasRiskAlert => _riskAssessment.shouldTriggerAlert;
  bool get sendingAlert => _sendingAlert;
  String get alertDeliveryStatus => _alertDeliveryStatus;
  SecureAlertReceipt? get lastReceipt => _lastReceipt;
  LocalReportPreview? get lastLocalReport => _lastLocalReport;
  bool get reportFormVisible => _reportFormVisible;
  bool get reportIntentConfirmed => _reportIntentConfirmed;
  String get reportComment => _reportComment;
  bool get canSubmitReport => _reportIntentConfirmed && !_sendingAlert;

  Future<void> hydrate() async {
    await whitelist.hydrate();

    final state = await _methodChannel.getKeyboardState();
    _hostMode = (state['hostMode'] ?? 'preview').toString();
    _nativeConnected = state['connected'] == true;
    _secureModeEnabled = state['secureMode'] == true;

    await _notificationService.initialize();
    await _nativeContextBridge.start();
    _contextSummary = await _nativeContextBridge.getSummary();
    await speechBridge.initialize();
    unawaited(_textClassifier.initialize());
    notifyListeners();
  }

  Future<void> refreshContextSummary() async {
    _contextSummary = await _nativeContextBridge.getSummary();
    notifyListeners();
  }

  Future<void> insertText(String value) async {
    _draftPreview += value;
    contextManager.recordKeyboardInput(value);
    notifyListeners();
    await _methodChannel.commitText(value);
  }

  Future<void> insertSpace() async {
    _draftPreview += ' ';
    notifyListeners();
    await _methodChannel.commitText(' ');
  }

  Future<void> backspace() async {
    if (_draftPreview.isNotEmpty) {
      _draftPreview = _draftPreview.substring(0, _draftPreview.length - 1);
      notifyListeners();
    }
    await _methodChannel.backspace();
  }

  Future<void> insertNewLine() async {
    _draftPreview = '';
    notifyListeners();
    await _methodChannel.enter();
  }

  Future<void> setSecureMode(bool enabled) async {
    if (_secureModeEnabled == enabled) {
      return;
    }
    _secureModeEnabled = enabled;
    notifyListeners();
    await _methodChannel.setSecureMode(enabled);
  }

  Future<void> openInputMethodSettings() =>
      _methodChannel.openInputMethodSettings();

  Future<void> openAccessibilitySettings() =>
      _nativeContextBridge.openAccessibilitySettings();

  Future<void> openNotificationSettings() =>
      _nativeContextBridge.openNotificationSettings();

  Future<void> toggleSpeechListening() async {
    if (speechBridge.isListening) {
      await speechBridge.stopListening();
      return;
    }
    await speechBridge.startListening();
  }

  Future<void> synchronizeContacts() => trustedContacts.loadContacts();

  void updateConversationLabel(String value) {
    contextManager.handleConversationLabel(value);
  }

  void addTrustedContact(String name) {
    unawaited(whitelist.addContact(name));
  }

  void removeTrustedContact(String name) {
    unawaited(whitelist.removeContact(name));
  }

  void showReportForm() {
    if (_reportFormVisible) {
      return;
    }
    _reportFormVisible = true;
    _reportIntentConfirmed = false;
    notifyListeners();
  }

  void hideReportForm() {
    _reportFormVisible = false;
    _reportIntentConfirmed = false;
    _reportComment = '';
    notifyListeners();
  }

  void setReportIntentConfirmed(bool value) {
    _reportIntentConfirmed = value;
    notifyListeners();
  }

  void updateReportComment(String value) {
    _reportComment = value;
    notifyListeners();
  }

  void clearContextBuffer() {
    _resetAlertUi(cancelNotification: true);
    contextManager.purge(reason: 'Limpieza manual.');
  }

  Future<void> sendRiskAlert() async {
    if (_sendingAlert) {
      return;
    }

    final entries = contextManager.entries;
    if (entries.isEmpty) {
      _alertDeliveryStatus =
          'No hay eventos locales para preparar una denuncia.';
      notifyListeners();
      return;
    }

    _sendingAlert = true;
    _alertDeliveryStatus = 'Preparando denuncia local simulada...';
    notifyListeners();

    try {
      await Future<void>.delayed(const Duration(milliseconds: 350));
      final createdAt = DateTime.now();
      final receiptMarker = _buildLocalReceiptMarker(entries, createdAt);

      _lastReceipt = SecureAlertReceipt(
        id: createdAt.microsecondsSinceEpoch,
        hashDenuncia: receiptMarker,
        reciboInmutabilidad: 'LOCAL-$receiptMarker',
        timestamp: createdAt,
        estadoInvestigacion: 'simulada_local',
      );
      _alertDeliveryStatus =
          'Denuncia local simulada. No se envió información a ningún servidor.';
      _lastLocalReport = LocalReportPreview(
        createdAt: createdAt,
        originApp: contextManager.activeAppPackage,
        eventCount: entries.length,
        riskCategoryLabel: _riskAssessment.categoryLabel,
        signals: List<String>.unmodifiable(
          _riskAssessment.tokens.take(8).toList(growable: false),
        ),
        comment: _reportComment.trim(),
      );
      _resetAlertUi(cancelNotification: true);
      contextManager.purge(reason: 'Denuncia local simulada por el usuario.');
    } catch (_) {
      _alertDeliveryStatus = 'No se pudo preparar la denuncia local simulada.';
    } finally {
      _sendingAlert = false;
      notifyListeners();
    }
  }

  void handleLifecycleChange(AppLifecycleState state) {
    contextManager.handleAppLifecycleChange(state);
    if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused ||
        state == AppLifecycleState.detached) {
      _resetAlertUi(cancelNotification: true);
    }
  }

  void _handleContextChanged() {
    notifyListeners();
    _scheduleRiskAnalysis();
  }

  void _handleNotificationCommand(LocalAlertCommand command) {
    if (command.shouldPurgeBuffer) {
      _alertDeliveryStatus =
          'La alerta fue descartada. El buffer local se purgó por seguridad.';
      _resetAlertUi(cancelNotification: true);
      contextManager.purge(
        reason: 'Notificación descartada por el usuario.',
      );
      return;
    }

    if (command.shouldOpenReportForm) {
      _alertDeliveryStatus =
          'La notificación abrió el formulario de denuncia local.';
      showReportForm();
    }
  }

  void _scheduleRiskAnalysis() {
    _analysisDebounce?.cancel();
    _analysisDebounce = Timer(const Duration(milliseconds: 220), () async {
      final generation = ++_analysisGeneration;
      final entries = contextManager.entries;

      if (entries.isEmpty || !contextManager.surveillanceEnabled) {
        final hadAlert = _lastAlertFingerprint != null;
        _riskAssessment = const RiskAssessment(
          riskProbability: 0,
          threshold: 0.58,
          tokens: <String>[],
          modelStatus: 'Sin riesgo activo o buffer vacío.',
          category: RiskCategory.idle,
        );
        if (hadAlert) {
          _lastAlertFingerprint = null;
          unawaited(_notificationService.cancelRiskAlert());
        }
        notifyListeners();
        return;
      }

      final assessment = await _textClassifier.analyzeBuffer(entries);
      if (generation != _analysisGeneration) {
        return;
      }

      _riskAssessment = assessment;
      notifyListeners();
      await _handleAlertTransition(assessment);
    });
  }

  Future<void> _handleAlertTransition(RiskAssessment assessment) async {
    if (!assessment.shouldTriggerAlert) {
      if (_lastAlertFingerprint != null) {
        _lastAlertFingerprint = null;
        await _notificationService.cancelRiskAlert();
      }
      return;
    }

    if (_lastAlertFingerprint == assessment.alertFingerprint) {
      return;
    }

    _lastAlertFingerprint = assessment.alertFingerprint;
    _alertDeliveryStatus =
        '${assessment.notificationTitle} detectada localmente.';
    notifyListeners();
    await _notificationService.showRiskAlert(
      assessment,
      originApp: contextManager.activeAppPackage,
    );
  }

  void _resetAlertUi({
    required bool cancelNotification,
  }) {
    _reportFormVisible = false;
    _reportIntentConfirmed = false;
    _reportComment = '';
    _lastAlertFingerprint = null;
    if (cancelNotification) {
      unawaited(_notificationService.cancelRiskAlert());
    }
    notifyListeners();
  }

  void disposeSafely() {
    unawaited(setSecureMode(false));
    unawaited(_nativeContextBridge.dispose());
    unawaited(speechBridge.stopListening());
    _analysisDebounce?.cancel();
    _notificationCommandsSubscription?.cancel();
    unawaited(_textClassifier.close());
    contextManager.removeListener(_handleContextChanged);
    whitelist.removeListener(notifyListeners);
    speechBridge.removeListener(notifyListeners);
    trustedContacts.removeListener(notifyListeners);
    if (_ownsWhitelist) {
      whitelist.dispose();
    }
    contextManager.dispose();
    speechBridge.dispose();
    if (_ownsTrustedContacts) {
      trustedContacts.dispose();
    }
    dispose();
  }

  String _buildLocalReceiptMarker(
    Iterable<TelemetryEntry> entries,
    DateTime createdAt,
  ) {
    final payload = <String>[
      createdAt.toUtc().toIso8601String(),
      _riskAssessment.category.name,
      _riskAssessment.tokens.join('|'),
      _reportComment.trim(),
      ...entries.map(
        (entry) =>
            '${entry.source}|${entry.originApp}|${entry.payload}|${entry.timestamp.toUtc().toIso8601String()}',
      ),
    ].join('||');

    final encoded = base64Url.encode(utf8.encode(payload)).replaceAll('=', '');
    return encoded.length <= 24 ? encoded : encoded.substring(0, 24);
  }
}
