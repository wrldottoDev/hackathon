import 'package:flutter/material.dart';

import 'keyboard_controller.dart';
import 'widgets/qwerty_keyboard.dart';
import 'widgets/security_alert_bar.dart';

class KeyboardScreen extends StatefulWidget {
  const KeyboardScreen({super.key});

  @override
  State<KeyboardScreen> createState() => _KeyboardScreenState();
}

class _KeyboardScreenState extends State<KeyboardScreen>
    with WidgetsBindingObserver {
  late final KeyboardController _controller;
  final TextEditingController _contactController = TextEditingController();
  final TextEditingController _conversationController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _controller = KeyboardController();
    _controller.hydrate();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _contactController.dispose();
    _conversationController.dispose();
    _controller.disposeSafely();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    _controller.handleLifecycleChange(state);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Scaffold(
          body: SafeArea(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: <Color>[
                    Color(0xFFF6F2E9),
                    Color(0xFFEAE3D6),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                children: <Widget>[
                  _Header(controller: _controller),
                  const SizedBox(height: 12),
                  SecurityAlertBar(
                    alerts: KeyboardController.securityAlerts,
                    secureModeEnabled: _controller.secureModeEnabled,
                  ),
                  if (_controller.hasRiskAlert) ...<Widget>[
                    const SizedBox(height: 12),
                    _RiskAlertCard(controller: _controller),
                  ],
                  const SizedBox(height: 12),
                  _DraftPreview(controller: _controller),
                  const SizedBox(height: 12),
                  _TelemetryStateCard(controller: _controller),
                  const SizedBox(height: 12),
                  _TrustedContactsCard(
                    controller: _controller,
                    contactController: _contactController,
                    conversationController: _conversationController,
                  ),
                  const SizedBox(height: 12),
                  _SpeechCard(controller: _controller),
                  const SizedBox(height: 12),
                  _BufferCard(controller: _controller),
                  const SizedBox(height: 16),
                  QwertyKeyboard(controller: _controller),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(
                'TensorFlowKeyboard IME',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                controller.nativeConnected
                    ? 'Conectado al InputConnection nativo'
                    : 'Modo preview Flutter',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: const Color(0xFF5D645D),
                    ),
              ),
            ],
          ),
        ),
        FilledButton.tonal(
          onPressed: controller.openInputMethodSettings,
          child: const Text('Ajustes IME'),
        ),
      ],
    );
  }
}

class _DraftPreview extends StatelessWidget {
  const _DraftPreview({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    final borderColor = controller.secureModeEnabled
        ? const Color(0xFFB33A3A)
        : const Color(0xFFD7CDBB);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: borderColor, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Text(
                'Vista previa',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: controller.secureModeEnabled
                      ? const Color(0xFFFDE5E5)
                      : const Color(0xFFE6F0EC),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  controller.secureModeEnabled
                      ? 'Modo Seguro activo'
                      : 'Modo Estándar',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            controller.draftPreview.isEmpty
                ? 'Las teclas se reflejan aquí y se envían al MethodChannel nativo.'
                : controller.draftPreview,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }
}

class _TelemetryStateCard extends StatelessWidget {
  const _TelemetryStateCard({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    final summary = controller.contextSummary;
    return _SectionCard(
      title: 'Telemetría Local',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(controller.contextManager.status),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: <Widget>[
              _StatusPill(
                label: 'Vigilancia',
                value: controller.contextManager.surveillanceEnabled
                    ? 'Activa'
                    : 'Inactiva',
              ),
              _StatusPill(
                label: 'Suspendido',
                value: controller.contextManager.suspended ? 'Sí' : 'No',
              ),
              _StatusPill(
                label: 'App activa',
                value: controller.contextManager.activeAppPackage ??
                    (summary['activeAppPackage']?.toString() ?? 'n/a'),
              ),
              _StatusPill(
                label: 'Riesgo',
                value: controller.riskAssessment.riskProbability
                    .toStringAsFixed(2),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: <Widget>[
              FilledButton.tonal(
                onPressed: controller.openAccessibilitySettings,
                child: const Text('Accessibility'),
              ),
              FilledButton.tonal(
                onPressed: controller.refreshContextSummary,
                child: const Text('Refrescar'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'El servicio Android observa solo el packageName activo. No extrae nodos externos ni texto de terceros.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
          ),
          const SizedBox(height: 8),
          Text(
            controller.riskAssessment.modelStatus,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
          ),
        ],
      ),
    );
  }
}

class _RiskAlertCard extends StatelessWidget {
  const _RiskAlertCard({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    final assessment = controller.riskAssessment;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF8D1F1F),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            'Alerta de Riesgo',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Probabilidad: ${assessment.riskProbability.toStringAsFixed(2)}',
            style: const TextStyle(color: Colors.white),
          ),
          if (assessment.tokens.isNotEmpty) ...<Widget>[
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: assessment.tokens.take(8).map((token) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFFB94141),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    token,
                    style: const TextStyle(color: Colors.white),
                  ),
                );
              }).toList(),
            ),
          ],
          const SizedBox(height: 12),
          FilledButton(
            onPressed:
                controller.sendingAlert ? null : controller.sendRiskAlert,
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFFF2D4D4),
              foregroundColor: const Color(0xFF6A1010),
            ),
            child: Text(
              controller.sendingAlert
                  ? 'Enviando alerta...'
                  : 'Enviar a /api/v1/alertas',
            ),
          ),
          const SizedBox(height: 8),
          Text(
            controller.alertDeliveryStatus,
            style: const TextStyle(color: Colors.white),
          ),
          if (controller.lastReceipt != null) ...<Widget>[
            const SizedBox(height: 8),
            Text(
              'Recibo: ${controller.lastReceipt!.reciboInmutabilidad}',
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ],
      ),
    );
  }
}

class _TrustedContactsCard extends StatelessWidget {
  const _TrustedContactsCard({
    required this.controller,
    required this.contactController,
    required this.conversationController,
  });

  final KeyboardController controller;
  final TextEditingController contactController;
  final TextEditingController conversationController;

  @override
  Widget build(BuildContext context) {
    return _SectionCard(
      title: 'Whitelist Dinámica',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(controller.trustedContacts.status),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: <Widget>[
              FilledButton.tonal(
                onPressed: controller.synchronizeContacts,
                child: const Text('Sincronizar contactos'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            controller: conversationController,
            onChanged: controller.updateConversationLabel,
            decoration: const InputDecoration(
              labelText: 'Etiqueta actual de conversación',
              helperText:
                  'Fuente segura controlada por el usuario. Si coincide con un contacto confiable, el buffer se purga y entra en modo suspendido.',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: contactController,
            decoration: InputDecoration(
              labelText: 'Agregar contacto manual',
              suffixIcon: IconButton(
                onPressed: () {
                  controller.addTrustedContact(contactController.text);
                  contactController.clear();
                },
                icon: const Icon(Icons.person_add_alt_1),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: controller.whitelist.contacts
                .map(
                  (contact) => InputChip(
                    label: Text(contact),
                    onDeleted: () => controller.removeTrustedContact(contact),
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _SpeechCard extends StatelessWidget {
  const _SpeechCard({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    return _SectionCard(
      title: 'STT Local',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(controller.speechBridge.status),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: controller.toggleSpeechListening,
            child: Text(
              controller.speechBridge.isListening
                  ? 'Detener dictado'
                  : 'Iniciar dictado',
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'El audio se procesa localmente solo cuando el usuario activa el dictado del teclado.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
          ),
        ],
      ),
    );
  }
}

class _BufferCard extends StatelessWidget {
  const _BufferCard({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    final entries = controller.contextManager.entries;
    return _SectionCard(
      title: 'Buffer Circular en RAM (20)',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Align(
            alignment: Alignment.centerRight,
            child: TextButton(
              onPressed: controller.clearContextBuffer,
              child: const Text('Purgar'),
            ),
          ),
          if (entries.isEmpty)
            const Text('No hay eventos locales retenidos.')
          else
            for (final entry in entries)
              Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  dense: true,
                  title: Text(entry.label),
                ),
              ),
          const SizedBox(height: 8),
          Text(
            'Este buffer es volátil: se purga cada 5 minutos o cuando se pierde el foco.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({
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
        border: Border.all(color: const Color(0xFFD7CDBB)),
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

class _StatusPill extends StatelessWidget {
  const _StatusPill({
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
        color: const Color(0xFFE6F0EC),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text('$label: $value'),
    );
  }
}
