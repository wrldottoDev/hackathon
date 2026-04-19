import 'package:flutter/material.dart';

import '../keyboard_controller.dart';

class QwertyKeyboard extends StatelessWidget {
  const QwertyKeyboard({
    super.key,
    required this.controller,
  });

  final KeyboardController controller;

  static const List<List<String>> _rows = <List<String>>[
    <String>['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    <String>['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    <String>['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        for (final row in _rows) ...<Widget>[
          _KeyRow(
            keys: row,
            onTap: controller.insertText,
          ),
          const SizedBox(height: 10),
        ],
        Row(
          children: <Widget>[
            Expanded(
              flex: 3,
              child: _SecureModeKey(controller: controller),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 4,
              child: _ActionKey(
                label: 'Espacio',
                onTap: controller.insertSpace,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 2,
              child: _ActionKey(
                label: '⌫',
                onTap: controller.backspace,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 2,
              child: _ActionKey(
                label: '↵',
                onTap: controller.insertNewLine,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _KeyRow extends StatelessWidget {
  const _KeyRow({
    required this.keys,
    required this.onTap,
  });

  final List<String> keys;
  final Future<void> Function(String key) onTap;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: keys
          .map(
            (key) => Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: _LetterKey(
                  label: key,
                  onTap: () => onTap(key.toLowerCase()),
                ),
              ),
            ),
          )
          .toList(),
    );
  }
}

class _LetterKey extends StatelessWidget {
  const _LetterKey({
    required this.label,
    required this.onTap,
  });

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: SizedBox(
          height: 52,
          child: Center(
            child: Text(
              label,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ActionKey extends StatelessWidget {
  const _ActionKey({
    required this.label,
    required this.onTap,
  });

  final String label;
  final Future<void> Function() onTap;

  @override
  Widget build(BuildContext context) {
    return FilledButton.tonal(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(56),
        backgroundColor: const Color(0xFFDDE7E2),
        foregroundColor: const Color(0xFF163D37),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
        ),
      ),
      onPressed: onTap,
      child: Text(label),
    );
  }
}

class _SecureModeKey extends StatelessWidget {
  const _SecureModeKey({required this.controller});

  final KeyboardController controller;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onLongPressStart: (_) => controller.setSecureMode(true),
      onLongPressEnd: (_) => controller.setSecureMode(false),
      onLongPressCancel: () => controller.setSecureMode(false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        height: 56,
        decoration: BoxDecoration(
          color: controller.secureModeEnabled
              ? const Color(0xFFB34040)
              : const Color(0xFF163D37),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Center(
          child: Text(
            controller.secureModeEnabled
                ? 'Modo Seguro activo'
                : 'Mantén: Modo Seguro',
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }
}
