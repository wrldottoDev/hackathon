import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

import '../keyboard/keyboard_method_channel.dart';

class PlatformSettingsLauncher {
  PlatformSettingsLauncher({
    KeyboardMethodChannel? keyboardMethodChannel,
  }) : _keyboardMethodChannel = keyboardMethodChannel ?? const KeyboardMethodChannel();

  static const MethodChannel _contextMethodsChannel =
      MethodChannel('tensorflow_keyboard/context_methods');

  final KeyboardMethodChannel _keyboardMethodChannel;

  Future<void> openInputMethodSettings() =>
      _keyboardMethodChannel.openInputMethodSettings();

  Future<void> openAccessibilitySettings() =>
      _invokeContextMethod('openAccessibilitySettings');

  Future<void> openNotificationSettings() =>
      _invokeContextMethod('openNotificationSettings');

  Future<void> _invokeContextMethod(String method) async {
    try {
      await _contextMethodsChannel.invokeMethod<void>(method);
    } on MissingPluginException {
      debugPrint('Context method $method unavailable in current host.');
    } on PlatformException catch (error) {
      debugPrint('Context method $method failed: ${error.message}');
    }
  }
}
