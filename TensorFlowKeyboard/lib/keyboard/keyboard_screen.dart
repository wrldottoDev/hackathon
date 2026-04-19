import 'dart:async';

import 'package:flutter/material.dart';

import 'keyboard_controller.dart';
import 'widgets/qwerty_keyboard.dart';
import 'widgets/security_alert_bar.dart';

class KeyboardScreen extends StatefulWidget {
  const KeyboardScreen({
    super.key,
    this.controller,
    this.imeOnly = false,
  });

  final KeyboardController? controller;
  final bool imeOnly;

  @override
  State<KeyboardScreen> createState() => _KeyboardScreenState();
}

class _KeyboardScreenState extends State<KeyboardScreen>
    with WidgetsBindingObserver {
  late final KeyboardController _controller;
  late final bool _ownsController;
  final TextEditingController _contactController = TextEditingController();
  final TextEditingController _conversationController = TextEditingController();
  final TextEditingController _reportCommentController =
      TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _controller = widget.controller ?? KeyboardController();
    _ownsController = widget.controller == null;
    unawaited(_controller.hydrate());
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _contactController.dispose();
    _conversationController.dispose();
    _reportCommentController.dispose();
    if (_ownsController) {
      _controller.disposeSafely();
    }
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
        if (!_controller.reportFormVisible &&
            _reportCommentController.text.isNotEmpty) {
          _reportCommentController.clear();
        }

        if (widget.imeOnly || _controller.hostMode == 'ime') {
          return Material(
            color: const Color(0xFFF6F2E9),
            child: SafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(10, 10, 10, 8),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    if (_controller.hasRiskAlert) ...<Widget>[
                      _ImeRiskBanner(controller: _controller),
                      const SizedBox(height: 10),
                    ],
                    if (_controller.reportFormVisible) ...<Widget>[
                      _InlineReportComposer(
                        controller: _controller,
                        reportCommentController: _reportCommentController,
                      ),
                      const SizedBox(height: 10),
                    ],
                    QwertyKeyboard(controller: _controller),
                  ],
                ),
              ),
            ),
          );
        }

        return Scaffold(
          body: SafeArea(
            child: Stack(
              children: <Widget>[
                Container(
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
                    padding: EdgeInsets.fromLTRB(
                      16,
                      12,
                      16,
                      _controller.reportFormVisible ? 280 : 16,
                    ),
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
                      if (_controller.lastLocalReport != null) ...<Widget>[
                        const SizedBox(height: 12),
                        _LastLocalReportCard(controller: _controller),
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
                _FloatingReportComposer(
                  controller: _controller,
                  reportCommentController: _reportCommentController,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _ImeRiskBanner extends StatelessWidget {
  const _ImeRiskBanner({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    final assessment = controller.riskAssessment;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF8D1F1F),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: <Widget>[
          const Icon(Icons.warning_amber_rounded, color: Colors.white),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  assessment.notificationTitle,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  controller.alertDeliveryStatus,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white70,
                      ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          FilledButton(
            onPressed: controller.showReportForm,
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFFF2D4D4),
              foregroundColor: const Color(0xFF6A1010),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            ),
            child: const Text('Ver'),
          ),
        ],
      ),
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
                'Teclado Seguro Local',
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
                ? 'Las teclas se reflejan aquí y alimentan el buffer local de revisión.'
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
                onPressed: controller.openNotificationSettings,
                child: const Text('Notificaciones'),
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
            assessment.notificationTitle,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            '${assessment.categoryLabel} • Severidad ${assessment.riskProbability.toStringAsFixed(2)}',
            style: const TextStyle(color: Colors.white),
          ),
          const SizedBox(height: 6),
          Text(
            assessment.notificationBody,
            style: const TextStyle(color: Colors.white70),
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
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: <Widget>[
              FilledButton(
                onPressed: controller.showReportForm,
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFFF2D4D4),
                  foregroundColor: const Color(0xFF6A1010),
                ),
                child: const Text('Abrir formulario'),
              ),
              FilledButton.tonal(
                onPressed: controller.clearContextBuffer,
                style: FilledButton.styleFrom(
                  foregroundColor: Colors.white,
                ),
                child: const Text('Purgar buffer'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            controller.alertDeliveryStatus,
            style: const TextStyle(color: Colors.white),
          ),
          if (controller.lastReceipt != null) ...<Widget>[
            const SizedBox(height: 8),
            Text(
              'Comprobante local: ${controller.lastReceipt!.reciboInmutabilidad}',
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ],
      ),
    );
  }
}

class _LastLocalReportCard extends StatelessWidget {
  const _LastLocalReportCard({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    final report = controller.lastLocalReport;
    if (report == null) {
      return const SizedBox.shrink();
    }

    return _SectionCard(
      title: 'Última denuncia local',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Text(
            'Se generó una simulación local. No se envió información a ningún servidor.',
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: <Widget>[
              _StatusPill(
                label: 'Categoría',
                value: report.riskCategoryLabel,
              ),
              _StatusPill(
                label: 'Eventos',
                value: '${report.eventCount}',
              ),
              _StatusPill(
                label: 'App',
                value: report.originApp ?? 'n/a',
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Hora: ${_formatTimestamp(report.createdAt)}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
          ),
          if (report.signals.isNotEmpty) ...<Widget>[
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: report.signals
                  .map(
                    (signal) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEDE6DA),
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text(signal),
                    ),
                  )
                  .toList(),
            ),
          ],
          const SizedBox(height: 12),
          Text(
            report.comment.isEmpty
                ? 'Comentario: sin comentario adicional.'
                : 'Comentario: ${report.comment}',
          ),
          if (controller.lastReceipt != null) ...<Widget>[
            const SizedBox(height: 8),
            Text(
              'Comprobante local: ${controller.lastReceipt!.reciboInmutabilidad}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF625E57),
                    fontWeight: FontWeight.w600,
                  ),
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
                child: const Text('Cargar agenda'),
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
                  'Si coincide con un contacto confiable, el buffer se purga y entra en modo suspendido.',
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
          const SizedBox(height: 8),
          Text(
            'La gestión completa de contactos de confianza vive en la app principal.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
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
            'Este buffer es volátil: se purga cada 5 minutos, por pérdida de foco o si el usuario descarta la alerta.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF625E57),
                ),
          ),
        ],
      ),
    );
  }
}

class _FloatingReportComposer extends StatelessWidget {
  const _FloatingReportComposer({
    required this.controller,
    required this.reportCommentController,
  });

  final KeyboardController controller;
  final TextEditingController reportCommentController;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      ignoring: !controller.reportFormVisible,
      child: AnimatedSlide(
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOutCubic,
        offset:
            controller.reportFormVisible ? Offset.zero : const Offset(0, 1.2),
        child: AnimatedOpacity(
          duration: const Duration(milliseconds: 180),
          opacity: controller.reportFormVisible ? 1 : 0,
          child: Align(
            alignment: Alignment.bottomCenter,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Material(
                elevation: 18,
                borderRadius: BorderRadius.circular(28),
                color: const Color(0xFFFEFBF6),
                child: Container(
                  width: 560,
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(28),
                    border: Border.all(color: const Color(0xFFD9CCB5)),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Row(
                        children: <Widget>[
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  controller.riskAssessment.notificationTitle,
                                  style: Theme.of(context)
                                      .textTheme
                                      .titleMedium
                                      ?.copyWith(
                                        fontWeight: FontWeight.w800,
                                      ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Formulario local sobre el teclado. La denuncia se simula y se conserva solo dentro del dispositivo.',
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.copyWith(
                                        color: const Color(0xFF625E57),
                                      ),
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            onPressed: controller.hideReportForm,
                            icon: const Icon(Icons.close),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      CheckboxListTile(
                        value: controller.reportIntentConfirmed,
                        onChanged: (value) =>
                            controller.setReportIntentConfirmed(value ?? false),
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Check de Denuncia'),
                        subtitle: const Text(
                          'Confirmo que deseo preparar la denuncia solo en este dispositivo.',
                        ),
                      ),
                      if (controller.reportIntentConfirmed) ...<Widget>[
                        const SizedBox(height: 12),
                        TextField(
                          controller: reportCommentController,
                          minLines: 2,
                          maxLines: 4,
                          onChanged: controller.updateReportComment,
                          decoration: const InputDecoration(
                            labelText: 'Comentario rápido',
                            hintText:
                                'Ej. El perfil me ofreció empleo y pidió mover la conversación a otro canal.',
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: <Widget>[
                            OutlinedButton(
                              onPressed: controller.hideReportForm,
                              child: const Text('Cancelar'),
                            ),
                            const Spacer(),
                            FilledButton(
                              onPressed: controller.canSubmitReport
                                  ? controller.sendRiskAlert
                                  : null,
                              child: Text(
                                controller.sendingAlert
                                    ? 'Guardando...'
                                    : 'Guardar denuncia local',
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _InlineReportComposer extends StatelessWidget {
  const _InlineReportComposer({
    required this.controller,
    required this.reportCommentController,
  });

  final KeyboardController controller;
  final TextEditingController reportCommentController;

  @override
  Widget build(BuildContext context) {
    return Material(
      elevation: 8,
      borderRadius: BorderRadius.circular(22),
      color: const Color(0xFFFEFBF6),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: const Color(0xFFD9CCB5)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Row(
              children: <Widget>[
                Expanded(
                  child: Text(
                    controller.riskAssessment.notificationTitle,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
                IconButton(
                  onPressed: controller.hideReportForm,
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            Text(
              'Denuncia local simulada. No sale del dispositivo.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF625E57),
                  ),
            ),
            const SizedBox(height: 10),
            CheckboxListTile(
              value: controller.reportIntentConfirmed,
              onChanged: (value) =>
                  controller.setReportIntentConfirmed(value ?? false),
              dense: true,
              contentPadding: EdgeInsets.zero,
              title: const Text('Confirmar'),
              subtitle: const Text(
                'Guardar denuncia local a partir del texto escrito.',
              ),
            ),
            if (controller.reportIntentConfirmed) ...<Widget>[
              const SizedBox(height: 10),
              TextField(
                controller: reportCommentController,
                minLines: 2,
                maxLines: 3,
                onChanged: controller.updateReportComment,
                decoration: const InputDecoration(
                  labelText: 'Comentario rápido',
                  hintText: 'Ej. Me pidió OTP y edad.',
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: <Widget>[
                  OutlinedButton(
                    onPressed: controller.hideReportForm,
                    child: const Text('Cancelar'),
                  ),
                  const Spacer(),
                  FilledButton(
                    onPressed: controller.canSubmitReport
                        ? controller.sendRiskAlert
                        : null,
                    child: Text(
                      controller.sendingAlert
                          ? 'Guardando...'
                          : 'Guardar local',
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
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

String _formatTimestamp(DateTime value) {
  final local = value.toLocal();
  final month = local.month.toString().padLeft(2, '0');
  final day = local.day.toString().padLeft(2, '0');
  final hour = local.hour.toString().padLeft(2, '0');
  final minute = local.minute.toString().padLeft(2, '0');
  return '${local.year}-$month-$day $hour:$minute';
}
