import 'package:flutter/material.dart';

import '../../keyboard/alerts/local_alert_notification_service.dart';
import '../../keyboard/context/trusted_contacts_service.dart';
import '../../keyboard/keyboard_controller.dart';
import '../../src/services/whitelist_service.dart';
import '../app_preferences_store.dart';
import 'main_application_screen.dart';
import 'onboarding_consent_screen.dart';

class AppBootstrapScreen extends StatefulWidget {
  const AppBootstrapScreen({super.key});

  @override
  State<AppBootstrapScreen> createState() => _AppBootstrapScreenState();
}

class _AppBootstrapScreenState extends State<AppBootstrapScreen> {
  final WhitelistService _whitelist = WhitelistService();
  late final TrustedContactsService _trustedContacts = TrustedContactsService(
    whitelist: _whitelist,
  );

  ConsentState _consentState = const ConsentState();
  KeyboardController? _controller;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  @override
  void dispose() {
    _controller?.disposeSafely();
    _trustedContacts.dispose();
    _whitelist.dispose();
    super.dispose();
  }

  Future<void> _bootstrap() async {
    await LocalAlertNotificationService.instance.initialize();
    await _whitelist.hydrate();
    final consentState =
        await AppPreferencesStore.instance.loadConsentState();
    if (!mounted) {
      return;
    }

    setState(() {
      _consentState = consentState;
      _loading = false;
    });

    if (consentState.isComplete) {
      await _initializeKeyboardController();
    }
  }

  Future<void> _initializeKeyboardController() async {
    if (_controller != null) {
      return;
    }
    final controller = KeyboardController(
      whitelistService: _whitelist,
      trustedContactsService: _trustedContacts,
    );
    await controller.hydrate();
    if (!mounted) {
      controller.disposeSafely();
      return;
    }
    setState(() {
      _controller = controller;
    });
  }

  Future<void> _handleConsentAccepted(ConsentState consentState) async {
    await AppPreferencesStore.instance.saveConsentState(consentState);
    await LocalAlertNotificationService.instance.requestPermissions();
    await _initializeKeyboardController();
    if (!mounted) {
      return;
    }
    setState(() {
      _consentState = consentState;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (!_consentState.isComplete) {
      return OnboardingConsentScreen(
        initialState: _consentState,
        onAccepted: (state) {
          _handleConsentAccepted(state);
        },
      );
    }

    if (_controller == null) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return MainApplicationScreen(
      consentState: _consentState,
      controller: _controller!,
      whitelist: _whitelist,
      trustedContacts: _trustedContacts,
    );
  }
}
