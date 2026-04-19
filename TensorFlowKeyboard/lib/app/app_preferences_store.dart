import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ConsentState {
  const ConsentState({
    this.termsAccepted = false,
    this.accessibilityAccepted = false,
    this.localAnalysisAccepted = false,
  });

  final bool termsAccepted;
  final bool accessibilityAccepted;
  final bool localAnalysisAccepted;

  bool get isComplete =>
      termsAccepted && accessibilityAccepted && localAnalysisAccepted;

  ConsentState copyWith({
    bool? termsAccepted,
    bool? accessibilityAccepted,
    bool? localAnalysisAccepted,
  }) {
    return ConsentState(
      termsAccepted: termsAccepted ?? this.termsAccepted,
      accessibilityAccepted:
          accessibilityAccepted ?? this.accessibilityAccepted,
      localAnalysisAccepted:
          localAnalysisAccepted ?? this.localAnalysisAccepted,
    );
  }
}

class PendingNotificationIntent {
  const PendingNotificationIntent({
    required this.actionId,
    this.payload,
  });

  final String actionId;
  final String? payload;
}

class AppPreferencesStore {
  AppPreferencesStore._();

  static final AppPreferencesStore instance = AppPreferencesStore._();

  static const String _termsAcceptedKey = 'consent_terms_accepted';
  static const String _accessibilityAcceptedKey =
      'consent_accessibility_accepted';
  static const String _localAnalysisAcceptedKey =
      'consent_local_analysis_accepted';
  static const String _whitelistContactsKey = 'whitelist_contacts';
  static const String _pendingNotificationActionKey =
      'pending_notification_action';
  static const String _pendingNotificationPayloadKey =
      'pending_notification_payload';

  SharedPreferencesAsync? _preferences;

  SharedPreferencesAsync? get _safePreferences {
    try {
      return _preferences ??= SharedPreferencesAsync();
    } catch (_) {
      return null;
    }
  }

  Future<ConsentState> loadConsentState() async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return const ConsentState();
    }
    try {
      return ConsentState(
        termsAccepted: await preferences.getBool(_termsAcceptedKey) ?? false,
        accessibilityAccepted:
            await preferences.getBool(_accessibilityAcceptedKey) ?? false,
        localAnalysisAccepted:
            await preferences.getBool(_localAnalysisAcceptedKey) ?? false,
      );
    } on MissingPluginException {
      return const ConsentState();
    }
  }

  Future<void> saveConsentState(ConsentState state) async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return;
    }
    try {
      await preferences.setBool(_termsAcceptedKey, state.termsAccepted);
      await preferences.setBool(
        _accessibilityAcceptedKey,
        state.accessibilityAccepted,
      );
      await preferences.setBool(
        _localAnalysisAcceptedKey,
        state.localAnalysisAccepted,
      );
    } on MissingPluginException {
      // Preview/test hosts may not expose persistent storage.
    }
  }

  Future<List<String>> loadWhitelist() async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return const <String>[];
    }
    try {
      final stored = await preferences.getStringList(_whitelistContactsKey);
      return _normalizeContacts(stored ?? const <String>[]);
    } on MissingPluginException {
      return const <String>[];
    }
  }

  Future<void> saveWhitelist(Iterable<String> contacts) async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return;
    }
    try {
      await preferences.setStringList(
        _whitelistContactsKey,
        _normalizeContacts(contacts),
      );
    } on MissingPluginException {
      // Preview/test hosts may not expose persistent storage.
    }
  }

  Future<void> setPendingNotificationIntent(
    PendingNotificationIntent intent,
  ) async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return;
    }
    try {
      await preferences.setString(
        _pendingNotificationActionKey,
        intent.actionId,
      );
      if (intent.payload == null || intent.payload!.isEmpty) {
        await preferences.remove(_pendingNotificationPayloadKey);
      } else {
        await preferences.setString(
          _pendingNotificationPayloadKey,
          intent.payload!,
        );
      }
    } on MissingPluginException {
      // Background notification handlers may be unavailable in tests.
    }
  }

  Future<PendingNotificationIntent?> consumePendingNotificationIntent() async {
    final preferences = _safePreferences;
    if (preferences == null) {
      return null;
    }
    try {
      final actionId =
          await preferences.getString(_pendingNotificationActionKey);
      if (actionId == null || actionId.isEmpty) {
        return null;
      }
      final payload =
          await preferences.getString(_pendingNotificationPayloadKey);
      await preferences.remove(_pendingNotificationActionKey);
      await preferences.remove(_pendingNotificationPayloadKey);
      return PendingNotificationIntent(
        actionId: actionId,
        payload: payload,
      );
    } on MissingPluginException {
      return null;
    }
  }

  List<String> _normalizeContacts(Iterable<String> contacts) {
    final normalized = contacts
        .map((entry) => entry.trim())
        .where((entry) => entry.isNotEmpty)
        .toSet()
        .toList(growable: false)
      ..sort();
    return normalized;
  }
}
