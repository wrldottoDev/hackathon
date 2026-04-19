import 'package:flutter_test/flutter_test.dart';
import 'package:tensorflow_keyboard/keyboard/context/telemetry_entry.dart';
import 'package:tensorflow_keyboard/keyboard/ml/risk_assessment.dart';
import 'package:tensorflow_keyboard/keyboard/ml/text_classifier.dart';
import 'package:tensorflow_keyboard/keyboard/ml/text_preprocessor.dart';

void main() {
  test('preprocessor creates a 256-dim vector and strips stop words', () async {
    final preprocessor = TextPreprocessor(inputDimension: 256);
    final result = await preprocessor.preprocess(
      <TelemetryEntry>[
        TelemetryEntry(
          source: 'Keyboard',
          originApp: 'com.whatsapp',
          payload: 'the otp urgente password code',
          timestamp: DateTime.now(),
        ),
      ],
    );

    expect(result.vector.length, 256);
    expect(
      result.tokens,
      containsAll(<String>['otp', 'urgente', 'password', 'code']),
    );
    expect(result.tokens, isNot(contains('the')));
  });

  test('classifier detects grooming from age plus secrecy phrases', () async {
    final classifier = TextClassifier();

    final result = await classifier.analyzeBuffer(
      <TelemetryEntry>[
        TelemetryEntry(
          source: 'Keyboard',
          originApp: 'com.instagram.android',
          payload: 'Tengo 15 años, no le digas a nadie y mandame una foto',
          timestamp: DateTime.now(),
        ),
      ],
    );

    expect(result.shouldTriggerAlert, isTrue);
    expect(result.category, RiskCategory.grooming);
    expect(result.tokens, contains('15 años'));
  });

  test('classifier detects financial fraud from otp plus code patterns',
      () async {
    final classifier = TextClassifier();

    final result = await classifier.analyzeBuffer(
      <TelemetryEntry>[
        TelemetryEntry(
          source: 'Speech To Text',
          originApp: 'com.whatsapp',
          payload: 'Banco: verifica tu cuenta con el OTP 554433',
          timestamp: DateTime.now(),
        ),
      ],
    );

    expect(result.shouldTriggerAlert, isTrue);
    expect(result.category, RiskCategory.fraudeFinanciero);
    expect(result.tokens, contains('código sensible + números'));
  });

  test('classifier stays idle with harmless text', () async {
    final classifier = TextClassifier();

    final result = await classifier.analyzeBuffer(
      <TelemetryEntry>[
        TelemetryEntry(
          source: 'Speech To Text',
          originApp: 'com.whatsapp',
          payload: 'hola todo bien nos vemos luego',
          timestamp: DateTime.now(),
        ),
      ],
    );

    expect(result.shouldTriggerAlert, isFalse);
    expect(result.category, RiskCategory.idle);
  });
}
