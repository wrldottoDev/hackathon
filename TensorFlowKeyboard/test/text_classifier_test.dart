import 'dart:typed_data';

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
    expect(result.tokens, containsAll(<String>['otp', 'urgente', 'password', 'code']));
    expect(result.tokens, isNot(contains('the')));
  });

  test('classifier triggers alert when backend score is above threshold', () async {
    final classifier = TextClassifier(
      backend: _FakeBackend(probability: 0.91),
    );

    final result = await classifier.analyzeBuffer(
      <TelemetryEntry>[
        TelemetryEntry(
          source: 'Keyboard',
          originApp: 'com.instagram.android',
          payload: 'otp urgente password',
          timestamp: DateTime.now(),
        ),
      ],
    );

    expect(result.shouldTriggerAlert, isTrue);
    expect(result.riskProbability, 0.91);
    expect(result.category, RiskCategory.fraudeFinanciero);
  });

  test('classifier stays quiet when backend score is below threshold', () async {
    final classifier = TextClassifier(
      backend: _FakeBackend(probability: 0.24),
    );

    final result = await classifier.analyzeBuffer(
      <TelemetryEntry>[
        TelemetryEntry(
          source: 'Speech To Text',
          originApp: 'com.whatsapp',
          payload: 'hola todo bien',
          timestamp: DateTime.now(),
        ),
      ],
    );

    expect(result.shouldTriggerAlert, isFalse);
    expect(result.riskProbability, 0.24);
    expect(result.category, RiskCategory.riesgoGenerico);
  });
}

class _FakeBackend implements TextClassifierBackend {
  _FakeBackend({required this.probability});

  final double probability;

  @override
  String get status => 'fake-backend';

  @override
  Future<void> close() async {}

  @override
  Future<void> initialize() async {}

  @override
  Future<double> predict({
    required Float32List inputVector,
    required List<String> tokens,
  }) async {
    return probability;
  }
}
