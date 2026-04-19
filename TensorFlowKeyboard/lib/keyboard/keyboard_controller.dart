import 'dart:async';

import 'package:flutter/foundation.dart';

import 'keyboard_method_channel.dart';

class KeyboardController extends ChangeNotifier {
  KeyboardController({
    KeyboardMethodChannel? methodChannel,
  }) : _methodChannel = methodChannel ?? const KeyboardMethodChannel();

  final KeyboardMethodChannel _methodChannel;

  static const List<String> securityAlerts = <String>[
    'Links Sospechosos',
    'OTP Sensible',
    'Captura Activa',
  ];

  String _draftPreview = '';
  bool _secureModeEnabled = false;
  String _hostMode = 'preview';
  bool _nativeConnected = false;

  String get draftPreview => _draftPreview;
  bool get secureModeEnabled => _secureModeEnabled;
  String get hostMode => _hostMode;
  bool get nativeConnected => _nativeConnected;

  Future<void> hydrate() async {
    final state = await _methodChannel.getKeyboardState();
    _hostMode = (state['hostMode'] ?? 'preview').toString();
    _nativeConnected = state['connected'] == true;
    _secureModeEnabled = state['secureMode'] == true;
    notifyListeners();
  }

  Future<void> insertText(String value) async {
    _draftPreview += value;
    notifyListeners();
    await _methodChannel.commitText(value);
  }

  Future<void> insertSpace() => insertText(' ');

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

  Future<void> openInputMethodSettings() => _methodChannel.openInputMethodSettings();

  void disposeSafely() {
    unawaited(setSecureMode(false));
    dispose();
  }
}
