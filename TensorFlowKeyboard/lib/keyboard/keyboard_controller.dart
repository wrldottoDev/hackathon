import 'dart:async';

import 'package:flutter/widgets.dart';

import '../src/services/whitelist_service.dart';
import 'context/context_manager.dart';
import 'context/native_context_bridge.dart';
import 'context/speech_to_text_bridge.dart';
import 'context/trusted_contacts_service.dart';
import 'keyboard_method_channel.dart';
import 'ml/risk_assessment.dart';
import 'ml/text_classifier.dart';
import 'network/secure_alert_models.dart';
import 'network/secure_transport.dart';

class KeyboardController extends ChangeNotifier {
  KeyboardController({
    KeyboardMethodChannel? methodChannel,
    SecureTransport? secureTransport,
  })  : _methodChannel = methodChannel ?? const KeyboardMethodChannel(),
        _secureTransport = secureTransport ?? SecureTransport() {
    contextManager.addListener(_handleContextChanged);
    whitelist.addListener(notifyListeners);
    speechBridge.addListener(notifyListeners);
    trustedContacts.addListener(notifyListeners);
  }

  final KeyboardMethodChannel _methodChannel;
  final SecureTransport _secureTransport;
  final WhitelistService whitelist = WhitelistService();
  late final ContextManager contextManager = ContextManager(
    whitelist: whitelist,
  );
  late final NativeContextBridge _nativeContextBridge = NativeContextBridge(
    contextManager: contextManager,
  );
  late final SpeechToTextBridge speechBridge = SpeechToTextBridge(
    contextManager: contextManager,
  );
  late final TrustedContactsService trustedContacts = TrustedContactsService(
    whitelist: whitelist,
  );
  final TextClassifier _textClassifier = TextClassifier();

  static const List<String> securityAlerts = <String>[
    'Links Sospechosos',
    'OTP Sensible',
    'Captura Activa',
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
  String _alertDeliveryStatus = 'Sin envíos remotos todavía.';
  SecureAlertReceipt? _lastReceipt;

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

  Future<void> hydrate() async {
    final state = await _methodChannel.getKeyboardState();
    _hostMode = (state['hostMode'] ?? 'preview').toString();
    _nativeConnected = state['connected'] == true;
    _secureModeEnabled = state['secureMode'] == true;

    await _nativeContextBridge.start();
    _contextSummary = await _nativeContextBridge.getSummary();
    await trustedContacts.synchronize();
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

  Future<void> synchronizeContacts() => trustedContacts.synchronize();

  void updateConversationLabel(String value) {
    contextManager.handleConversationLabel(value);
  }

  void addTrustedContact(String name) {
    whitelist.addContact(name);
  }

  void removeTrustedContact(String name) {
    whitelist.removeContact(name);
  }

  void clearContextBuffer() {
    contextManager.purge(reason: 'Limpieza manual.');
  }

  Future<void> sendRiskAlert() async {
    if (_sendingAlert) {
      return;
    }

    final entries = contextManager.entries;
    if (entries.isEmpty) {
      _alertDeliveryStatus = 'No hay eventos locales para enviar.';
      notifyListeners();
      return;
    }

    _sendingAlert = true;
    _alertDeliveryStatus = 'Entregando alerta cifrada al servidor central...';
    notifyListeners();

    try {
      final receipt = await _secureTransport.sendAlert(
        SecureAlertReport(
          riskProbability: _riskAssessment.riskProbability,
          bufferEntries: entries
              .map(SecureAlertBufferEntry.fromTelemetry)
              .toList(growable: false),
          metadata: <String, dynamic>{
            'host_mode': _hostMode,
            'secure_mode': _secureModeEnabled,
            'surveillance_enabled': contextManager.surveillanceEnabled,
            'active_app_package': contextManager.activeAppPackage,
            'model_status': _riskAssessment.modelStatus,
            'client_timestamp': DateTime.now().toUtc().toIso8601String(),
          },
          extractedEntities: _riskAssessment.tokens,
          originApp: contextManager.activeAppPackage,
          createdAt: DateTime.now(),
        ),
      );
      _lastReceipt = receipt;
      _alertDeliveryStatus =
          'Alerta enviada. Recibo ${receipt.reciboInmutabilidad.substring(0, 12)}...';
    } on SecureTransportException catch (error) {
      _alertDeliveryStatus = error.message;
    } catch (_) {
      _alertDeliveryStatus = 'No se pudo entregar la alerta al servidor.';
    } finally {
      _sendingAlert = false;
      notifyListeners();
    }
  }

  void handleLifecycleChange(AppLifecycleState state) {
    contextManager.handleAppLifecycleChange(state);
  }

  void _handleContextChanged() {
    notifyListeners();
    _scheduleRiskAnalysis();
  }

  void _scheduleRiskAnalysis() {
    _analysisDebounce?.cancel();
    _analysisDebounce = Timer(const Duration(milliseconds: 220), () async {
      final generation = ++_analysisGeneration;
      final entries = contextManager.entries;

      if (entries.isEmpty || !contextManager.surveillanceEnabled) {
        _riskAssessment = const RiskAssessment(
          riskProbability: 0,
          threshold: 0.8,
          tokens: <String>[],
          modelStatus: 'Sin riesgo activo o buffer vacío.',
        );
        notifyListeners();
        return;
      }

      final assessment = await _textClassifier.analyzeBuffer(entries);
      if (generation != _analysisGeneration) {
        return;
      }

      _riskAssessment = assessment;
      notifyListeners();
    });
  }

  void disposeSafely() {
    unawaited(setSecureMode(false));
    unawaited(_nativeContextBridge.dispose());
    unawaited(speechBridge.stopListening());
    _analysisDebounce?.cancel();
    unawaited(_textClassifier.close());
    _secureTransport.dispose();
    contextManager.removeListener(_handleContextChanged);
    whitelist.removeListener(notifyListeners);
    speechBridge.removeListener(notifyListeners);
    trustedContacts.removeListener(notifyListeners);
    trustedContacts.dispose();
    whitelist.dispose();
    contextManager.dispose();
    speechBridge.dispose();
    dispose();
  }
}
