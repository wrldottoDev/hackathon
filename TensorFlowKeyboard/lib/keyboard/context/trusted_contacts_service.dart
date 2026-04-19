import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_contacts/flutter_contacts.dart';

import '../../src/services/whitelist_service.dart';

class TrustedContactEntry {
  const TrustedContactEntry({
    required this.displayName,
    this.subtitle,
  });

  final String displayName;
  final String? subtitle;
}

class TrustedContactsService extends ChangeNotifier {
  TrustedContactsService({
    required this.whitelist,
  });

  final WhitelistService whitelist;

  bool _permissionGranted = false;
  bool _loading = false;
  String _status = 'Agenda no consultada todavía.';
  List<TrustedContactEntry> _availableContacts = const <TrustedContactEntry>[];

  bool get permissionGranted => _permissionGranted;
  bool get isLoading => _loading;
  String get status => _status;
  List<TrustedContactEntry> get availableContacts => _availableContacts;

  Future<void> loadContacts({
    bool requestPermissionIfNeeded = true,
  }) async {
    _loading = true;
    notifyListeners();

    try {
      final permission = requestPermissionIfNeeded
          ? await FlutterContacts.permissions.request(PermissionType.read)
          : await FlutterContacts.permissions.check(PermissionType.read);

      if (permission != PermissionStatus.granted &&
          permission != PermissionStatus.limited) {
        _permissionGranted = false;
        _availableContacts = const <TrustedContactEntry>[];
        _status = 'Permiso de contactos pendiente o denegado.';
        _loading = false;
        notifyListeners();
        return;
      }

      final contacts = await FlutterContacts.getAll(
        properties: const <ContactProperty>{
          ContactProperty.name,
          ContactProperty.phone,
        },
      );

      final entries = contacts
          .map(
            (contact) => TrustedContactEntry(
              displayName: (contact.displayName ?? '').trim(),
              subtitle: contact.phones.isEmpty
                  ? null
                  : contact.phones.first.number.trim(),
            ),
          )
          .where((contact) => contact.displayName.isNotEmpty)
          .toList(growable: false)
        ..sort((a, b) => a.displayName.compareTo(b.displayName));

      _permissionGranted = true;
      _availableContacts = entries;
      _status = 'Agenda cargada: ${entries.length} contactos visibles.';
    } on MissingPluginException {
      _permissionGranted = false;
      _availableContacts = const <TrustedContactEntry>[];
      _status = 'Plugin de contactos no disponible en este host.';
    } catch (error) {
      _permissionGranted = false;
      _availableContacts = const <TrustedContactEntry>[];
      _status = 'No se pudieron cargar contactos: $error';
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  bool isTrusted(TrustedContactEntry entry) {
    return whitelist.contains(entry.displayName);
  }

  Future<void> setTrusted(TrustedContactEntry entry, bool trusted) async {
    await whitelist.toggleContact(entry.displayName, trusted);
    _status = trusted
        ? 'Contacto agregado a la whitelist.'
        : 'Contacto removido de la whitelist.';
    notifyListeners();
  }
}
