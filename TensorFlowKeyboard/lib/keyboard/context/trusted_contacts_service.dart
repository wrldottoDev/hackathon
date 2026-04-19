import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_contacts/flutter_contacts.dart';

import '../../src/services/whitelist_service.dart';

class TrustedContactsService extends ChangeNotifier {
  TrustedContactsService({
    required this.whitelist,
  });

  final WhitelistService whitelist;

  bool _permissionGranted = false;
  String _status = 'Contactos no cargados.';

  bool get permissionGranted => _permissionGranted;
  String get status => _status;

  Future<void> synchronize() async {
    try {
      final permission = await FlutterContacts.permissions.request(
        PermissionType.read,
      );
      if (permission != PermissionStatus.granted &&
          permission != PermissionStatus.limited) {
        _permissionGranted = false;
        _status = 'Permiso de contactos denegado.';
        notifyListeners();
        return;
      }

      final contacts = await FlutterContacts.getAll(
        properties: const <ContactProperty>{ContactProperty.name},
      );

      whitelist.replaceAll(
        contacts
            .map((contact) => contact.displayName)
            .whereType<String>()
            .where((name) => name.trim().isNotEmpty),
      );

      _permissionGranted = true;
      _status = 'Contactos sincronizados: ${whitelist.contacts.length}.';
      notifyListeners();
    } on MissingPluginException {
      _permissionGranted = false;
      _status = 'Plugin de contactos no disponible en este host.';
      notifyListeners();
    } catch (error) {
      _permissionGranted = false;
      _status = 'No se pudieron cargar contactos: $error';
      notifyListeners();
    }
  }
}
