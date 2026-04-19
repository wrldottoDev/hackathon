import 'package:flutter/foundation.dart';

import '../../app/app_preferences_store.dart';

class WhitelistService extends ChangeNotifier {
  WhitelistService({
    AppPreferencesStore? store,
  }) : _store = store ?? AppPreferencesStore.instance;

  final AppPreferencesStore _store;
  final List<String> _contacts = <String>[];

  bool _hydrated = false;

  List<String> get contacts => List<String>.unmodifiable(_contacts);
  bool get isHydrated => _hydrated;

  Future<void> hydrate() async {
    final storedContacts = await _store.loadWhitelist();
    _replaceInternal(storedContacts, notify: false);
    _hydrated = true;
    notifyListeners();
  }

  Future<void> addContact(String value) async {
    final normalized = _normalize(value);
    if (normalized.isEmpty) {
      return;
    }
    final alreadyExists =
        _contacts.any((contact) => _normalize(contact) == normalized);
    if (alreadyExists) {
      return;
    }
    _contacts.add(value.trim());
    _contacts.sort();
    notifyListeners();
    await _persist();
  }

  Future<void> removeContact(String value) async {
    final before = _contacts.length;
    _contacts.removeWhere(
      (contact) => _normalize(contact) == _normalize(value),
    );
    final removed = _contacts.length != before;
    if (!removed) {
      return;
    }
    notifyListeners();
    await _persist();
  }

  Future<void> replaceAll(Iterable<String> contacts) async {
    _replaceInternal(contacts, notify: true);
    await _persist();
  }

  Future<void> toggleContact(String value, bool selected) {
    if (selected) {
      return addContact(value);
    }
    return removeContact(value);
  }

  bool contains(String value) {
    final normalized = _normalize(value);
    return _contacts.any((contact) => _normalize(contact) == normalized);
  }

  bool matches(String? senderName) {
    final normalizedSender = _normalize(senderName ?? '');
    if (normalizedSender.isEmpty) {
      return false;
    }

    for (final contact in _contacts) {
      final normalizedContact = _normalize(contact);
      if (normalizedContact.isEmpty) {
        continue;
      }
      if (normalizedSender == normalizedContact ||
          normalizedSender.contains(normalizedContact) ||
          normalizedContact.contains(normalizedSender)) {
        return true;
      }
    }
    return false;
  }

  Future<void> _persist() => _store.saveWhitelist(_contacts);

  void _replaceInternal(
    Iterable<String> contacts, {
    required bool notify,
  }) {
    _contacts
      ..clear()
      ..addAll(
        contacts
            .map((entry) => entry.trim())
            .where((entry) => _normalize(entry).isNotEmpty),
      );
    _contacts.sort();
    if (notify) {
      notifyListeners();
    }
  }

  static String _normalize(String value) {
    return value.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');
  }
}
