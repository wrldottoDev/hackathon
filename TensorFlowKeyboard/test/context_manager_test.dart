import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tensorflow_keyboard/keyboard/context/context_manager.dart';
import 'package:tensorflow_keyboard/src/models/capture_item.dart';
import 'package:tensorflow_keyboard/src/services/whitelist_service.dart';

void main() {
  test('keeps only the last 20 keyboard events in volatile memory', () {
    final whitelist = WhitelistService();
    final manager = ContextManager(whitelist: whitelist, capacity: 20);

    manager.handleNativeSignal(
      CaptureItem(
        id: 'signal-1',
        source: CaptureSource.accessibilityStub,
        content: 'state',
        timestamp: DateTime.now(),
        metadata: const <String, dynamic>{
          'packageName': 'com.instagram.android',
          'surveillanceActive': true,
          'appLostFocus': false,
        },
      ),
    );

    for (var index = 0; index < 25; index++) {
      manager.recordKeyboardInput('mensaje-$index');
    }

    expect(manager.entries.length, 20);
    expect(manager.entries.first.payload, 'mensaje-24');
    expect(manager.entries.first.originApp, 'com.instagram.android');
    expect(manager.entries.last.payload, 'mensaje-5');
  });

  test('suspends and purges when current conversation matches whitelist',
      () async {
    final whitelist = WhitelistService();
    await whitelist.addContact('Alice');
    final manager = ContextManager(whitelist: whitelist, capacity: 20);

    manager.handleNativeSignal(
      CaptureItem(
        id: 'signal-1',
        source: CaptureSource.accessibilityStub,
        content: 'state',
        timestamp: DateTime.now(),
        metadata: const <String, dynamic>{
          'packageName': 'com.whatsapp',
          'surveillanceActive': true,
          'appLostFocus': false,
        },
      ),
    );

    manager.recordKeyboardInput('hola');
    manager.handleConversationLabel('Alice');

    expect(manager.suspended, isTrue);
    expect(manager.entries, isEmpty);
  });

  test('purges when focus is lost', () {
    final manager = ContextManager(whitelist: WhitelistService(), capacity: 20);

    manager.handleNativeSignal(
      CaptureItem(
        id: 'signal-1',
        source: CaptureSource.accessibilityStub,
        content: 'state',
        timestamp: DateTime.now(),
        metadata: const <String, dynamic>{
          'packageName': 'com.whatsapp',
          'surveillanceActive': true,
          'appLostFocus': false,
        },
      ),
    );
    manager.recordKeyboardInput('hola');
    manager.handleAppLifecycleChange(AppLifecycleState.paused);

    expect(manager.entries, isEmpty);
  });

  test('keeps only the latest keyboard draft snapshot when forced from IME',
      () {
    final manager = ContextManager(whitelist: WhitelistService(), capacity: 20);

    manager.recordKeyboardDraft(
      'hola',
      force: true,
      fallbackOriginApp: 'com.telegram.messenger',
    );
    manager.recordKeyboardDraft(
      'hola tengo 15 años',
      force: true,
      fallbackOriginApp: 'com.telegram.messenger',
    );

    expect(manager.entries.length, 1);
    expect(manager.entries.first.source, 'Keyboard Draft');
    expect(manager.entries.first.payload, 'hola tengo 15 años');
    expect(manager.entries.first.originApp, 'com.telegram.messenger');
  });
}
