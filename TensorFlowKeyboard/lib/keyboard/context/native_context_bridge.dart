import 'dart:async';

import 'package:flutter/services.dart';

import 'context_manager.dart';
import '../../src/models/capture_item.dart';

class NativeContextBridge {
  NativeContextBridge({
    required this.contextManager,
  });

  static const EventChannel _eventChannel =
      EventChannel('tensorflow_keyboard/context_events');
  static const MethodChannel _methodChannel =
      MethodChannel('tensorflow_keyboard/context_methods');

  final ContextManager contextManager;

  StreamSubscription<dynamic>? _subscription;

  Future<void> start() async {
    _subscription ??= _eventChannel.receiveBroadcastStream().listen(
          _handleEvent,
          onError: (Object error) {
            contextManager.reportSystemStatus(
              'Error en bridge contextual: $error',
            );
          },
        );
  }

  Future<void> dispose() async {
    await _subscription?.cancel();
    _subscription = null;
  }

  Future<Map<String, dynamic>> getSummary() async {
    try {
      final result = await _methodChannel.invokeMapMethod<Object?, Object?>(
        'getContextSummary',
      );
      if (result == null) {
        return const <String, dynamic>{};
      }
      return result.map((key, value) => MapEntry(key.toString(), value));
    } on PlatformException {
      return const <String, dynamic>{};
    }
  }

  Future<void> openAccessibilitySettings() => _invokeVoid('openAccessibilitySettings');
  Future<void> openNotificationSettings() => _invokeVoid('openNotificationSettings');

  Future<void> _invokeVoid(String method) async {
    try {
      await _methodChannel.invokeMethod<void>(method);
    } on PlatformException {
      // Ignore in preview hosts where these settings may be unavailable.
    }
  }

  void _handleEvent(dynamic event) {
    if (event is! Map<Object?, Object?>) {
      return;
    }
    contextManager.handleNativeSignal(CaptureItem.fromMap(event));
  }
}
