import 'package:flutter/foundation.dart';

class WhitelistService extends ChangeNotifier {
  final List<String> _contacts = <String>[];

  List<String> get contacts => List<String>.unmodifiable(_contacts);

  void addContact(String value) {
    final normalized = _normalize(value);
    if (normalized.isEmpty) {
      return;
    }
    final alreadyExists = _contacts.any((contact) => _normalize(contact) == normalized);
    if (alreadyExists) {
      return;
    }
    _contacts.add(value.trim());
    _contacts.sort();
    notifyListeners();
  }

  void removeContact(String value) {
    _contacts.removeWhere((contact) => _normalize(contact) == _normalize(value));
    notifyListeners();
  }

  void replaceAll(Iterable<String> contacts) {
    _contacts
      ..clear()
      ..addAll(
        contacts
            .map((entry) => entry.trim())
            .where((entry) => _normalize(entry).isNotEmpty),
      );
    _contacts.sort();
    notifyListeners();
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

  static String _normalize(String value) {
    return value
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9]'), '');
  }
}
