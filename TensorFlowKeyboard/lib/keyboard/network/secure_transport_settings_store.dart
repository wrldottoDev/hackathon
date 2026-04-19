import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SecureTransportSettings {
  const SecureTransportSettings({
    this.baseUrl,
    this.sgtTag,
  });

  final String? baseUrl;
  final String? sgtTag;

  bool get hasOverrides =>
      (baseUrl != null && baseUrl!.isNotEmpty) ||
      (sgtTag != null && sgtTag!.isNotEmpty);
}

class SecureTransportSettingsStore {
  SecureTransportSettingsStore._();

  static final SecureTransportSettingsStore instance =
      SecureTransportSettingsStore._();

  static const String _baseUrlKey = 'secure_alerts_base_url';
  static const String _sgtTagKey = 'secure_alerts_sgt_tag';

  SharedPreferencesAsync? _preferences;

  SharedPreferencesAsync? get _safePreferences {
    try {
      return _preferences ??= SharedPreferencesAsync();
    } catch (_) {
      return null;
    }
  }

  Future<SecureTransportSettings> load() async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return const SecureTransportSettings();
    }

    try {
      final storedBaseUrl = await preferences.getString(_baseUrlKey);
      final storedSgtTag = await preferences.getString(_sgtTagKey);
      String? normalizedBaseUrl;
      try {
        normalizedBaseUrl = normalizeBaseUrl(storedBaseUrl);
      } on FormatException {
        normalizedBaseUrl = null;
      }

      return SecureTransportSettings(
        baseUrl: normalizedBaseUrl,
        sgtTag: normalizeSgtTag(storedSgtTag),
      );
    } on MissingPluginException {
      return const SecureTransportSettings();
    }
  }

  Future<void> save(SecureTransportSettings settings) async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return;
    }

    final normalizedBaseUrl = normalizeBaseUrl(settings.baseUrl);
    final normalizedSgtTag = normalizeSgtTag(settings.sgtTag);

    try {
      if (normalizedBaseUrl == null) {
        await preferences.remove(_baseUrlKey);
      } else {
        await preferences.setString(_baseUrlKey, normalizedBaseUrl);
      }

      if (normalizedSgtTag == null) {
        await preferences.remove(_sgtTagKey);
      } else {
        await preferences.setString(_sgtTagKey, normalizedSgtTag);
      }
    } on MissingPluginException {
      // Preview/test hosts may not expose persistent storage.
    }
  }

  Future<void> clear() async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return;
    }

    try {
      await preferences.remove(_baseUrlKey);
      await preferences.remove(_sgtTagKey);
    } on MissingPluginException {
      // Preview/test hosts may not expose persistent storage.
    }
  }

  static String? normalizeBaseUrl(String? rawValue) {
    final value = rawValue?.trim() ?? '';
    if (value.isEmpty) {
      return null;
    }

    final uri = Uri.tryParse(value);
    if (uri == null) {
      throw const FormatException(
        'La URL del servidor debe ser absoluta y usar http o https.',
      );
    }

    final hasValidScheme = uri.scheme == 'http' || uri.scheme == 'https';
    if (!hasValidScheme || !(uri.hasAuthority && uri.host.isNotEmpty)) {
      throw const FormatException(
        'La URL del servidor debe ser absoluta y usar http o https.',
      );
    }

    final normalizedPath = uri.path.trim();
    if (normalizedPath.isNotEmpty && normalizedPath != '/') {
      throw const FormatException(
        'Usa solo el dominio base del servidor, sin rutas como /api/v1/alertas.',
      );
    }

    return uri.replace(path: '', query: null, fragment: null).toString();
  }

  static String? normalizeSgtTag(String? rawValue) {
    final value = rawValue?.trim() ?? '';
    if (value.isEmpty) {
      return null;
    }
    return value;
  }
}
