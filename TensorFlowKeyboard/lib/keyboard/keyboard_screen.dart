import 'package:flutter/material.dart';

import 'keyboard_controller.dart';
import 'widgets/qwerty_keyboard.dart';
import 'widgets/security_alert_bar.dart';

class KeyboardScreen extends StatefulWidget {
  const KeyboardScreen({super.key});

  @override
  State<KeyboardScreen> createState() => _KeyboardScreenState();
}

class _KeyboardScreenState extends State<KeyboardScreen> {
  late final KeyboardController _controller;

  @override
  void initState() {
    super.initState();
    _controller = KeyboardController();
    _controller.hydrate();
  }

  @override
  void dispose() {
    _controller.disposeSafely();
    super.dispose();
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
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    _Header(controller: _controller),
                    const SizedBox(height: 12),
                    SecurityAlertBar(
                      alerts: KeyboardController.securityAlerts,
                      secureModeEnabled: _controller.secureModeEnabled,
                    ),
                    const SizedBox(height: 12),
                    _DraftPreview(controller: _controller),
                    const Spacer(),
                    QwertyKeyboard(controller: _controller),
                  ],
                ),
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
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
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
