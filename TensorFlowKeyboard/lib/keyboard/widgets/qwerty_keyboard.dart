import 'package:flutter/material.dart';

import '../keyboard_controller.dart';

class QwertyKeyboard extends StatelessWidget {
  const QwertyKeyboard({
    super.key,
    required this.controller,
    this.compact = false,
  });

  final KeyboardController controller;
  final bool compact;

  static const List<List<String>> _rows = <List<String>>[
    <String>['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    <String>['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    <String>['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    <String>['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
  ];

  @override
  Widget build(BuildContext context) {
    final rowSpacing = compact ? 6.0 : 10.0;
    return Column(
      children: <Widget>[
        for (final row in _rows) ...<Widget>[
          _KeyRow(
            keys: row,
            onTap: controller.insertText,
            compact: compact,
          ),
          SizedBox(height: rowSpacing),
        ],
        Row(
          children: <Widget>[
            Expanded(
              flex: 3,
              child: _SecureModeKey(
                controller: controller,
                compact: compact,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 4,
              child: _ActionKey(
                label: 'Espacio',
                onTap: controller.insertSpace,
                compact: compact,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 2,
              child: _ActionKey(
                label: '⌫',
                onTap: controller.backspace,
                compact: compact,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 2,
              child: _ActionKey(
                label: '↵',
                onTap: controller.insertNewLine,
                compact: compact,
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
    required this.compact,
  });

  final List<String> keys;
  final Future<void> Function(String key) onTap;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: keys
          .map(
            (key) => Expanded(
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: compact ? 2 : 4),
                child: _LetterKey(
                  label: key,
                  onTap: () => onTap(_wireValueForKey(key)),
                  compact: compact,
                ),
              ),
            ),
          )
          .toList(),
    );
  }

  String _wireValueForKey(String key) {
    final isDigit = RegExp(r'^\d$').hasMatch(key);
    return isDigit ? key : key.toLowerCase();
  }
}

class _LetterKey extends StatelessWidget {
  const _LetterKey({
    required this.label,
    required this.onTap,
    required this.compact,
  });

  final String label;
  final VoidCallback onTap;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: SizedBox(
          height: compact ? 38 : 52,
          child: Center(
            child: Text(
              label,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    fontSize: compact ? 16 : null,
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
    required this.compact,
  });

  final String label;
  final Future<void> Function() onTap;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return FilledButton.tonal(
      style: FilledButton.styleFrom(
        minimumSize: Size.fromHeight(compact ? 42 : 56),
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
  const _SecureModeKey({
    required this.controller,
    required this.compact,
  });

  final KeyboardController controller;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onLongPressStart: (_) => controller.setSecureMode(true),
      onLongPressEnd: (_) => controller.setSecureMode(false),
      onLongPressCancel: () => controller.setSecureMode(false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        height: compact ? 42 : 56,
        decoration: BoxDecoration(
          color: controller.secureModeEnabled
              ? const Color(0xFFB34040)
              : const Color(0xFF163D37),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Center(
          child: Text(
            controller.secureModeEnabled
                ? (compact ? 'Seguro' : 'Modo Seguro activo')
                : (compact ? 'Seguro' : 'Mantén: Modo Seguro'),
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: compact ? 12 : null,
                ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }
}
