import 'dart:async';

import 'package:flutter/material.dart';

import '../models/capture_item.dart';
import '../platform/native_capture_bridge.dart';
import '../services/capture_coordinator.dart';
import '../services/whitelist_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.whitelist,
    required this.coordinator,
    required this.bridge,
  });

  final WhitelistService whitelist;
  final CaptureCoordinator coordinator;
  final NativeCaptureBridge bridge;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _contactController = TextEditingController();
  final TextEditingController _senderController =
      TextEditingController(text: 'Contacto Demo');
  final TextEditingController _messageController =
      TextEditingController(text: 'Mensaje de prueba para el buffer.');

  Map<String, dynamic> _platformSummary = const <String, dynamic>{};

  @override
  void initState() {
    super.initState();
    widget.bridge.start();
    _refreshSummary();
  }

  @override
  void dispose() {
    widget.bridge.dispose();
    _contactController.dispose();
    _senderController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _refreshSummary() async {
    final summary = await widget.bridge.getPlatformSummary();
    if (!mounted) {
      return;
    }
    setState(() {
      _platformSummary = summary;
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge(<Listenable>[
        widget.coordinator,
        widget.whitelist,
      ]),
      builder: (context, child) {
        final items = widget.coordinator.recentItems;

        return Scaffold(
          appBar: AppBar(
            title: const Text('TensorFlowKeyboard'),
            actions: <Widget>[
              IconButton(
                onPressed: _refreshSummary,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(20),
            children: <Widget>[
              _NoticeCard(message: widget.coordinator.statusMessage),
              const SizedBox(height: 16),
              _SectionCard(
                title: 'Estado de servicios',
                child: Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: <Widget>[
                    _StatusChip(
                      label: 'IME',
                      value: _platformSummary['imeEnabled'] == true ? 'Activo' : 'Pendiente',
                    ),
                    _StatusChip(
                      label: 'Accessibility',
                      value: _platformSummary['accessibilityEnabled'] == true
                          ? 'Registrado'
                          : 'Pendiente',
                    ),
                    _StatusChip(
                      label: 'Notifications',
                      value: _platformSummary['notificationEnabled'] == true
                          ? 'Registrado'
                          : 'Pendiente',
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _SectionCard(
                title: 'Acciones del sistema',
                child: Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: <Widget>[
                    FilledButton(
                      onPressed: widget.bridge.openInputMethodSettings,
                      child: const Text('Configurar teclado'),
                    ),
                    FilledButton.tonal(
                      onPressed: widget.bridge.openAccessibilitySettings,
                      child: const Text('Accessibility'),
                    ),
                    FilledButton.tonal(
                      onPressed: widget.bridge.openNotificationSettings,
                      child: const Text('Notifications'),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _SectionCard(
                title: 'Whitelist',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    TextField(
                      controller: _contactController,
                          decoration: InputDecoration(
                        labelText: 'Agregar contacto de confianza',
                        suffixIcon: IconButton(
                          onPressed: () {
                            unawaited(
                              widget.whitelist
                                  .addContact(_contactController.text),
                            );
                            _contactController.clear();
                          },
                          icon: const Icon(Icons.person_add_alt_1),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: widget.whitelist.contacts
                          .map(
                            (contact) => InputChip(
                              label: Text(contact),
                              onDeleted: () {
                                unawaited(
                                  widget.whitelist.removeContact(contact),
                                );
                              },
                            ),
                          )
                          .toList(),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _SectionCard(
                title: 'Simulación segura',
                child: Column(
                  children: <Widget>[
                    TextField(
                      controller: _senderController,
                      decoration: const InputDecoration(labelText: 'Remitente'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _messageController,
                      minLines: 2,
                      maxLines: 3,
                      decoration: const InputDecoration(labelText: 'Mensaje'),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: <Widget>[
                        FilledButton(
                          onPressed: () {
                            widget.coordinator.simulate(
                              senderName: _senderController.text,
                              content: _messageController.text,
                            );
                          },
                          child: const Text('Simular en Flutter'),
                        ),
                        FilledButton.tonal(
                          onPressed: () {
                            widget.bridge.seedNativeSimulation(
                              senderName: _senderController.text,
                              content: _messageController.text,
                            );
                          },
                          child: const Text('Simular en Android'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _SectionCard(
                title: 'Buffer circular en RAM (20)',
                child: items.isEmpty
                    ? const Text('Todavía no hay eventos aceptados.')
                    : Column(
                        children: items
                            .map(
                              (item) => Card(
                                margin: const EdgeInsets.only(bottom: 10),
                                child: ListTile(
                                  title: Text(item.senderName ?? 'Sin remitente'),
                                  subtitle: Text(item.content),
                                  trailing: Text(item.source.label),
                                ),
                              ),
                            )
                            .toList(),
                      ),
              ),
              const SizedBox(height: 16),
              const _SectionCard(
                title: 'Notas',
                child: Text(
                  'La captura real de texto en otras apps y el contenido de notificaciones quedó deshabilitada por diseño. El scaffold mantiene esos puntos separados para integrar procesamiento local permitido más adelante.',
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _NoticeCard extends StatelessWidget {
  const _NoticeCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF113B33),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        message,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.w600,
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
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFD5CEC1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
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
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFE2ECE7),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text('$label: $value'),
    );
  }
}
