import 'package:flutter/material.dart';

import '../../keyboard/alerts/local_alert_notification_service.dart';
import '../../keyboard/context/trusted_contacts_service.dart';
import '../../keyboard/keyboard_controller.dart';
import '../../keyboard/network/secure_transport.dart';
import '../../keyboard/network/secure_transport_settings_store.dart';
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
                    value:
                        consentState.termsAccepted ? 'Aceptado' : 'Pendiente',
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
            const _SecureAlertsServerCard(),
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

class _SecureAlertsServerCard extends StatefulWidget {
  const _SecureAlertsServerCard();

  @override
  State<_SecureAlertsServerCard> createState() =>
      _SecureAlertsServerCardState();
}

class _SecureAlertsServerCardState extends State<_SecureAlertsServerCard> {
  final SecureTransportSettingsStore _settingsStore =
      SecureTransportSettingsStore.instance;
  final TextEditingController _baseUrlController = TextEditingController();
  final TextEditingController _sgtTagController = TextEditingController();

  bool _loading = true;
  bool _saving = false;
  String _statusMessage = '';
  bool _statusIsError = false;
  SecureTransportSettings _settings = const SecureTransportSettings();

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    _sgtTagController.dispose();
    super.dispose();
  }

  Future<void> _loadSettings() async {
    final settings = await _settingsStore.load();
    if (!mounted) {
      return;
    }

    setState(() {
      _settings = settings;
      _baseUrlController.text = settings.baseUrl ?? '';
      _sgtTagController.text = settings.sgtTag ?? '';
      _loading = false;
    });
  }

  Future<void> _saveSettings() async {
    setState(() {
      _saving = true;
      _statusMessage = '';
      _statusIsError = false;
    });

    try {
      final nextSettings = SecureTransportSettings(
        baseUrl: _baseUrlController.text,
        sgtTag: _sgtTagController.text,
      );
      await _settingsStore.save(nextSettings);
      final persisted = await _settingsStore.load();
      if (!mounted) {
        return;
      }

      setState(() {
        _settings = persisted;
        _baseUrlController.text = persisted.baseUrl ?? '';
        _sgtTagController.text = persisted.sgtTag ?? '';
        _statusMessage =
            'Configuración guardada. Los próximos envíos usarán este servidor sin reinstalar la app.';
      });
    } on FormatException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _statusIsError = true;
        _statusMessage = error.message;
      });
    } finally {
      if (mounted) {
        setState(() {
          _saving = false;
        });
      }
    }
  }

  Future<void> _resetSettings() async {
    setState(() {
      _saving = true;
      _statusMessage = '';
      _statusIsError = false;
    });

    await _settingsStore.clear();
    if (!mounted) {
      return;
    }

    setState(() {
      _settings = const SecureTransportSettings();
      _baseUrlController.clear();
      _sgtTagController.clear();
      _statusMessage =
          'Se restauró la configuración por defecto del servidor de denuncias.';
      _saving = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final effectiveBaseUrl =
        _settings.baseUrl ?? SecureTransport.defaultBaseUri.toString();
    final effectiveSgtTag = _settings.sgtTag ?? SecureTransport.defaultSgtTag;

    return _DashboardCard(
      title: 'Servidor de denuncias',
      child: _loading
          ? const Center(
              child: Padding(
                padding: EdgeInsets.symmetric(vertical: 16),
                child: CircularProgressIndicator(),
              ),
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  'Configura la VPS que recibirá `/api/v1/alertas`. Si dejas los campos vacíos, la app usa el valor compilado por defecto.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFF595952),
                      ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _baseUrlController,
                  keyboardType: TextInputType.url,
                  autocorrect: false,
                  enableSuggestions: false,
                  decoration: InputDecoration(
                    labelText: 'Base URL del servidor',
                    hintText: SecureTransport.defaultBaseUri.toString(),
                    helperText:
                        'Usa solo el dominio base, por ejemplo https://analytics.tudominio.com',
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _sgtTagController,
                  autocorrect: false,
                  enableSuggestions: false,
                  decoration: InputDecoration(
                    labelText: 'X-SGT-Tag',
                    hintText: SecureTransport.defaultSgtTag,
                    helperText:
                        'Opcional. Déjalo vacío si el backend usa el tag por defecto.',
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: <Widget>[
                    _StatusChip(
                      label: 'URL activa',
                      value: effectiveBaseUrl,
                    ),
                    _StatusChip(
                      label: 'SGT activo',
                      value: effectiveSgtTag,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: <Widget>[
                    FilledButton(
                      onPressed: _saving ? null : _saveSettings,
                      child: Text(
                        _saving ? 'Guardando...' : 'Guardar servidor',
                      ),
                    ),
                    OutlinedButton(
                      onPressed: _saving ? null : _resetSettings,
                      child: const Text('Restaurar default'),
                    ),
                  ],
                ),
                if (_statusMessage.isNotEmpty) ...<Widget>[
                  const SizedBox(height: 12),
                  Text(
                    _statusMessage,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: _statusIsError
                              ? const Color(0xFF8D1F1F)
                              : const Color(0xFF0F5A4F),
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
                const SizedBox(height: 12),
                Text(
                  'Importante: la VPS debe exponer HTTPS válido y conservar la llave pública esperada por la app, o tendrás que publicar un APK con la nueva llave.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: const Color(0xFF626158),
                      ),
                ),
              ],
            ),
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
