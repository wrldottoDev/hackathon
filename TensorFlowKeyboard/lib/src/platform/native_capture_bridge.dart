import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

import '../models/capture_item.dart';
import '../services/capture_coordinator.dart';
import '../services/whitelist_service.dart';

class NativeCaptureBridge {
  NativeCaptureBridge({
    required this.coordinator,
    required this.whitelist,
  }) : _whitelistListener = (() {}) {
    _whitelistListener = () {
      unawaited(syncTrustedContacts());
    };
    whitelist.addListener(_whitelistListener);
  }

  static const MethodChannel _methodChannel =
      MethodChannel('tensorflow_keyboard/methods');
  static const EventChannel _eventChannel =
      EventChannel('tensorflow_keyboard/events');

  final CaptureCoordinator coordinator;
  final WhitelistService whitelist;
  late final VoidCallback _whitelistListener;

  StreamSubscription<dynamic>? _subscription;

  Future<void> start() async {
    _subscription ??= _eventChannel.receiveBroadcastStream().listen(
          _onEvent,
          onError: (Object error) {
            coordinator.registerBridgeStatus('Error nativo: $error');
          },
        );
    await syncTrustedContacts();
    coordinator.registerBridgeStatus('Bridge nativo conectado.');
  }

  Future<void> dispose() async {
    whitelist.removeListener(_whitelistListener);
    await _subscription?.cancel();
  }

  Future<void> syncTrustedContacts() async {
    try {
      await _methodChannel.invokeMethod<void>(
        'setTrustedContacts',
        <String, dynamic>{'contacts': whitelist.contacts},
      );
    } on PlatformException catch (error) {
      coordinator.registerBridgeStatus('No se pudo sincronizar whitelist: ${error.message}');
    }
  }

  Future<Map<String, dynamic>> getPlatformSummary() async {
    try {
      final result =
          await _methodChannel.invokeMapMethod<Object?, Object?>('getPlatformSummary');
      if (result == null) {
        return const <String, dynamic>{};
      }
      return result.map((key, value) => MapEntry(key.toString(), value));
    } on PlatformException catch (error) {
      coordinator.registerBridgeStatus('No se pudo leer el resumen nativo: ${error.message}');
      return const <String, dynamic>{};
    }
  }

  Future<void> seedNativeSimulation({
    required String senderName,
    required String content,
  }) async {
    try {
      await _methodChannel.invokeMethod<void>(
        'seedSimulationEvent',
        <String, dynamic>{
          'senderName': senderName,
          'content': content,
        },
      );
    } on PlatformException catch (error) {
      coordinator.registerBridgeStatus('No se pudo simular el evento nativo: ${error.message}');
    }
  }

  Future<void> openInputMethodSettings() => _invokeVoid('openInputMethodSettings');
  Future<void> openAccessibilitySettings() => _invokeVoid('openAccessibilitySettings');
  Future<void> openNotificationSettings() => _invokeVoid('openNotificationSettings');

  Future<void> _invokeVoid(String method) async {
    try {
      await _methodChannel.invokeMethod<void>(method);
    } on PlatformException catch (error) {
      coordinator.registerBridgeStatus('Falló la acción $method: ${error.message}');
    }
  }

  void _onEvent(dynamic event) {
    if (event is! Map<Object?, Object?>) {
      coordinator.registerBridgeStatus('Evento nativo ignorado por formato inválido.');
      return;
    }
    unawaited(coordinator.handleIncoming(CaptureItem.fromMap(event)));
  }
}
