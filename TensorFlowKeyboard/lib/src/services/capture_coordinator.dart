import 'package:flutter/foundation.dart';

import '../models/capture_item.dart';
import 'ai_processor.dart';
import 'capture_buffer.dart';
import 'whitelist_service.dart';

class CaptureCoordinator extends ChangeNotifier {
  CaptureCoordinator({
    required this.buffer,
    required this.whitelist,
    required this.processor,
  }) {
    buffer.addListener(notifyListeners);
    whitelist.addListener(notifyListeners);
  }

  final CircularCaptureBuffer<CaptureItem> buffer;
  final WhitelistService whitelist;
  final CaptureProcessor processor;

  String _statusMessage = 'Esperando eventos nativos o simulados.';
  Object? _lastError;

  List<CaptureItem> get recentItems => buffer.items;
  String get statusMessage => _statusMessage;
  Object? get lastError => _lastError;

  Future<void> handleIncoming(CaptureItem item) async {
    if (item.blockedByWhitelist) {
      _statusMessage = 'Captura detenida por whitelist para ${item.senderName}.';
      notifyListeners();
      return;
    }

    final shouldBlock = whitelist.matches(item.senderName);

    if (shouldBlock) {
      _statusMessage = 'Captura detenida por whitelist para ${item.senderName}.';
      notifyListeners();
      return;
    }

    buffer.add(item);
    _statusMessage = 'Procesado ${item.source.label} a las ${_formatTime(item.timestamp)}.';
    _lastError = null;
    notifyListeners();

    try {
      await processor.process(item);
    } catch (error) {
      _lastError = error;
      _statusMessage = 'Fallo en procesamiento: $error';
      notifyListeners();
    }
  }

  Future<void> simulate({
    required String senderName,
    required String content,
  }) {
    final item = CaptureItem(
      id: 'flutter-${DateTime.now().microsecondsSinceEpoch}',
      source: CaptureSource.simulation,
      senderName: senderName.trim().isEmpty ? null : senderName.trim(),
      content: content,
      timestamp: DateTime.now(),
      metadata: const <String, dynamic>{'origin': 'flutter_debug_panel'},
    );
    return handleIncoming(item);
  }

  void registerBridgeStatus(String message) {
    _statusMessage = message;
    notifyListeners();
  }

  static String _formatTime(DateTime value) {
    final hour = value.hour.toString().padLeft(2, '0');
    final minute = value.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
