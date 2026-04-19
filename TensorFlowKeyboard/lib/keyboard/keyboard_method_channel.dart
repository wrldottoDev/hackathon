import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class KeyboardMethodChannel {
  const KeyboardMethodChannel();

  static const MethodChannel _channel =
      MethodChannel('tensorflow_keyboard/ime');

  Future<void> commitText(String text) => _invokeVoid(
        'commitText',
        <String, dynamic>{'text': text},
      );

  Future<void> backspace() => _invokeVoid('backspace');

  Future<void> enter() => _invokeVoid('enter');

  Future<void> setSecureMode(bool enabled) => _invokeVoid(
        'setSecureMode',
        <String, dynamic>{'enabled': enabled},
      );

  Future<void> openInputMethodSettings() =>
      _invokeVoid('openInputMethodSettings');

  Future<Map<String, dynamic>> getKeyboardState() async {
    try {
      final raw = await _channel.invokeMapMethod<Object?, Object?>(
        'getKeyboardState',
      );
      if (raw == null) {
        return const <String, dynamic>{};
      }
      return raw.map((key, value) => MapEntry(key.toString(), value));
    } on MissingPluginException {
      return const <String, dynamic>{'hostMode': 'preview'};
    } on PlatformException {
      return const <String, dynamic>{'hostMode': 'preview'};
    }
  }

  Future<void> _invokeVoid(
    String method, [
    Map<String, dynamic>? arguments,
  ]) async {
    try {
      await _channel.invokeMethod<void>(method, arguments);
    } on MissingPluginException {
      debugPrint('MethodChannel $method unavailable in current host.');
    } on PlatformException catch (error) {
      debugPrint('MethodChannel $method failed: ${error.message}');
    }
  }
}
