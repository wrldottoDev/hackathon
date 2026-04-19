import 'package:flutter/material.dart';

import '../app_preferences_store.dart';

class OnboardingConsentScreen extends StatefulWidget {
  const OnboardingConsentScreen({
    super.key,
    required this.initialState,
    required this.onAccepted,
  });

  final ConsentState initialState;
  final ValueChanged<ConsentState> onAccepted;

  @override
  State<OnboardingConsentScreen> createState() =>
      _OnboardingConsentScreenState();
}

class _OnboardingConsentScreenState extends State<OnboardingConsentScreen> {
  late bool _termsAccepted = widget.initialState.termsAccepted;
  late bool _accessibilityAccepted = widget.initialState.accessibilityAccepted;
  late bool _localAnalysisAccepted = widget.initialState.localAnalysisAccepted;

  bool get _canContinue =>
      _termsAccepted && _accessibilityAccepted && _localAnalysisAccepted;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: <Color>[
                Color(0xFFF7F3EB),
                Color(0xFFE5E0D2),
              ],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
            children: <Widget>[
              Text(
                'Consentimiento Informado',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
              ),
              const SizedBox(height: 10),
              Text(
                'Antes de activar el teclado seguro, el usuario debe aceptar explícitamente el uso del AccessibilityService para detectar la app activa y el análisis local por reglas sobre el texto escrito en este teclado.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: const Color(0xFF5B5B54),
                    ),
              ),
              const SizedBox(height: 20),
              const _ConsentBlock(
                title: 'Términos y condiciones',
                body:
                    'La telemetría se mantiene en RAM, se purga por foco/tiempo y la denuncia se conserva solo como simulación local si el usuario decide guardarla. No se promete recuperación forense ni monitoreo de texto externo.',
              ),
              const SizedBox(height: 14),
              const _ConsentBlock(
                title: 'Uso de AccessibilityService',
                body:
                    'Se usa para conocer únicamente la aplicación activa y activar o desactivar vigilancia local. No debe habilitarse si no comprendes este alcance.',
              ),
              const SizedBox(height: 14),
              const _ConsentBlock(
                title: 'Análisis local',
                body:
                    'Las reglas por palabras y patrones procesan solo el buffer local del teclado y el dictado voluntario. Esto puede generar falsos positivos.',
              ),
              const SizedBox(height: 18),
              CheckboxListTile(
                value: _termsAccepted,
                onChanged: (value) => setState(() {
                  _termsAccepted = value ?? false;
                }),
                contentPadding: EdgeInsets.zero,
                title: const Text('Acepto los términos y condiciones'),
              ),
              CheckboxListTile(
                value: _accessibilityAccepted,
                onChanged: (value) => setState(() {
                  _accessibilityAccepted = value ?? false;
                }),
                contentPadding: EdgeInsets.zero,
                title: const Text(
                  'Acepto habilitar AccessibilityService para detectar la app activa',
                ),
              ),
              CheckboxListTile(
                value: _localAnalysisAccepted,
                onChanged: (value) => setState(() {
                  _localAnalysisAccepted = value ?? false;
                }),
                contentPadding: EdgeInsets.zero,
                title: const Text(
                  'Acepto el análisis local de riesgo sobre el texto del teclado',
                ),
              ),
              const SizedBox(height: 18),
              FilledButton(
                onPressed: _canContinue
                    ? () {
                        widget.onAccepted(
                          ConsentState(
                            termsAccepted: _termsAccepted,
                            accessibilityAccepted: _accessibilityAccepted,
                            localAnalysisAccepted: _localAnalysisAccepted,
                          ),
                        );
                      }
                    : null,
                child: const Text('Continuar y activar configuración'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ConsentBlock extends StatelessWidget {
  const _ConsentBlock({
    required this.title,
    required this.body,
  });

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFD7CCBA)),
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
          const SizedBox(height: 8),
          Text(body),
        ],
      ),
    );
  }
}
