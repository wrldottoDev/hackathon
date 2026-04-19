import 'package:flutter/material.dart';

import '../../keyboard/alerts/local_alert_notification_service.dart';
import '../../keyboard/context/trusted_contacts_service.dart';
import '../../keyboard/keyboard_controller.dart';
import '../../keyboard/keyboard_screen.dart';
import '../../src/services/whitelist_service.dart';
import '../app_preferences_store.dart';
import '../platform_settings_launcher.dart';
import '../widgets/whitelist_management_panel.dart';

class MainApplicationScreen extends StatefulWidget {
  const MainApplicationScreen({
    super.key,
    required this.consentState,
    required this.controller,
    required this.whitelist,
    required this.trustedContacts,
  });

  final ConsentState consentState;
  final KeyboardController controller;
  final WhitelistService whitelist;
  final TrustedContactsService trustedContacts;

  @override
  State<MainApplicationScreen> createState() => _MainApplicationScreenState();
}

class _MainApplicationScreenState extends State<MainApplicationScreen> {
  final PlatformSettingsLauncher _settingsLauncher = PlatformSettingsLauncher();
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TensorFlowKeyboard'),
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: <Widget>[
          _DashboardTab(
            consentState: widget.consentState,
            settingsLauncher: _settingsLauncher,
            controller: widget.controller,
            trustedContacts: widget.trustedContacts,
          ),
          WhitelistManagementPanel(
            trustedContacts: widget.trustedContacts,
            whitelist: widget.whitelist,
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: const <NavigationDestination>[
          NavigationDestination(
            icon: Icon(Icons.security),
            label: 'Control',
          ),
          NavigationDestination(
            icon: Icon(Icons.people_alt_outlined),
            label: 'Whitelist',
          ),
        ],
      ),
    );
  }
}

class _DashboardTab extends StatelessWidget {
  const _DashboardTab({
    required this.consentState,
    required this.settingsLauncher,
    required this.controller,
    required this.trustedContacts,
  });

  final ConsentState consentState;
  final PlatformSettingsLauncher settingsLauncher;
  final KeyboardController controller;
  final TrustedContactsService trustedContacts;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge(<Listenable>[
        controller,
        trustedContacts,
      ]),
      builder: (context, child) {
        return ListView(
          padding: const EdgeInsets.fromLTRB(16, 18, 16, 18),
          children: <Widget>[
            Text(
              'Centro de Control',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w900,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Desde aquí aceptas el flujo de seguridad, abres la configuración del teclado y gestionas la vista previa del IME.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: const Color(0xFF595952),
                  ),
            ),
            const SizedBox(height: 16),
            _DashboardCard(
              title: 'Consentimiento informado',
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: <Widget>[
                  _StatusChip(
                    label: 'Términos',
                    value: consentState.termsAccepted ? 'Aceptado' : 'Pendiente',
                  ),
                  _StatusChip(
                    label: 'Accessibility',
                    value: consentState.accessibilityAccepted
                        ? 'Aceptado'
                        : 'Pendiente',
                  ),
                  _StatusChip(
                    label: 'Análisis local',
                    value: consentState.localAnalysisAccepted
                        ? 'Aceptado'
                        : 'Pendiente',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _DashboardCard(
              title: 'Activación del teclado',
              child: Wrap(
                spacing: 12,
                runSpacing: 12,
                children: <Widget>[
                  FilledButton(
                    onPressed: settingsLauncher.openInputMethodSettings,
                    child: const Text('Configurar teclado'),
                  ),
                  FilledButton.tonal(
                    onPressed: settingsLauncher.openAccessibilitySettings,
                    child: const Text('Abrir Accessibility'),
                  ),
                  FilledButton.tonal(
                    onPressed: () async {
                      await LocalAlertNotificationService.instance
                          .requestPermissions();
                      await settingsLauncher.openNotificationSettings();
                    },
                    child: const Text('Permiso de alertas'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _DashboardCard(
              title: 'Estado local',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: <Widget>[
                      _StatusChip(
                        label: 'Whitelist',
                        value: '${controller.whitelist.contacts.length}',
                      ),
                      _StatusChip(
                        label: 'Agenda',
                        value: trustedContacts.permissionGranted
                            ? 'Concedida'
                            : 'Pendiente',
                      ),
                      _StatusChip(
                        label: 'Riesgo',
                        value: controller.riskAssessment.categoryLabel,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(trustedContacts.status),
                  const SizedBox(height: 12),
                  Text(
                    'Si se detecta un riesgo mayor a 0.8, el teclado publica una alerta local y puede abrir un formulario de denuncia cifrada.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: const Color(0xFF626158),
                        ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _DashboardCard(
              title: 'Vista previa del IME',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  const Text(
                    'Abre una simulación funcional del teclado para validar alertas locales, whitelist y denuncia segura.',
                  ),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute<void>(
                          builder: (context) => KeyboardScreen(
                            controller: controller,
                          ),
                        ),
                      );
                    },
                    child: const Text('Abrir preview del teclado'),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

class _DashboardCard extends StatelessWidget {
  const _DashboardCard({
    required this.title,
    required this.child,
  });

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFD8CDBA)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F0EB),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text('$label: $value'),
    );
  }
}
