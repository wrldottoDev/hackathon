import 'package:flutter/material.dart';

class SecurityAlertBar extends StatelessWidget {
  const SecurityAlertBar({
    super.key,
    required this.alerts,
    required this.secureModeEnabled,
  });

  final List<String> alerts;
  final bool secureModeEnabled;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF173B35),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              const Icon(Icons.shield_outlined, color: Colors.white),
              const SizedBox(width: 10),
              Text(
                'Alertas de Seguridad',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const Spacer(),
              AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: secureModeEnabled
                      ? const Color(0xFFE36D5B)
                      : const Color(0xFF2E5B54),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Text(
                  secureModeEnabled ? 'Seguro' : 'Monitoreo',
                  style: const TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: alerts
                .map(
                  (alert) => Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFF254B44),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      alert,
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}
