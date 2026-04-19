import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';

import 'context_manager.dart';

class SpeechToTextBridge extends ChangeNotifier {
  SpeechToTextBridge({
    required this.contextManager,
    SpeechToText? speechToText,
  }) : _speechToText = speechToText ?? SpeechToText();

  final ContextManager contextManager;
  final SpeechToText _speechToText;

  bool _isAvailable = false;
  bool _isListening = false;
  bool _isDisposed = false;
  String _status = 'STT listo para inicializar.';

  bool get isAvailable => _isAvailable;
  bool get isListening => _isListening;
  String get status => _status;

  Future<void> initialize() async {
    try {
      _isAvailable = await _speechToText.initialize(
        onStatus: _handleStatus,
        onError: (error) {
          _status = 'STT error: ${error.errorMsg}';
          _safeNotify();
        },
      );
      _status = _isAvailable
          ? 'STT disponible. Solo escucha por acción explícita del usuario.'
          : 'STT no disponible en este host.';
      _safeNotify();
    } catch (error) {
      _status = 'No se pudo inicializar STT: $error';
      _safeNotify();
    }
  }

  Future<void> startListening() async {
    if (!_isAvailable) {
      await initialize();
      if (!_isAvailable) {
        return;
      }
    }

    await _speechToText.listen(
      onResult: _handleResult,
      listenFor: const Duration(seconds: 20),
      listenOptions: SpeechListenOptions(
        partialResults: true,
      ),
    );
    _isListening = true;
    _status = 'Escuchando audio local.';
    _safeNotify();
  }

  Future<void> stopListening() async {
    await _speechToText.stop();
    _isListening = false;
    _status = 'Escucha detenida.';
    _safeNotify();
  }

  void _handleStatus(String status) {
    _isListening = _speechToText.isListening;
    _status = 'STT: $status';
    _safeNotify();
  }

  void _handleResult(SpeechRecognitionResult result) {
    final text = result.recognizedWords.trim();
    if (text.isEmpty || !result.finalResult) {
      return;
    }

    // Privacy boundary:
    // Recognized speech is inserted into the volatile RAM buffer only.
    // This bridge does not persist transcripts to disk.
    contextManager.recordSpeechInput(text);
  }

  void _safeNotify() {
    if (_isDisposed) {
      return;
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _isDisposed = true;
    super.dispose();
  }
}
