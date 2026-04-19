import 'package:flutter/foundation.dart';

import '../context/telemetry_entry.dart';

class TextPreprocessingResult {
  const TextPreprocessingResult({
    required this.vector,
    required this.tokens,
    required this.normalizedText,
  });

  final Float32List vector;
  final List<String> tokens;
  final String normalizedText;
}

class TextPreprocessor {
  TextPreprocessor({
    this.inputDimension = 256,
    Map<String, int>? vocabulary,
  }) : vocabulary = vocabulary ?? const <String, int>{};

  final int inputDimension;

  // Ready to be replaced by a real token dictionary exported from training.
  final Map<String, int> vocabulary;

  static const Set<String> _stopWords = <String>{
    'a',
    'al',
    'and',
    'as',
    'at',
    'con',
    'de',
    'del',
    'el',
    'en',
    'es',
    'for',
    'i',
    'in',
    'la',
    'las',
    'los',
    'me',
    'mi',
    'my',
    'of',
    'or',
    'para',
    'por',
    'que',
    'se',
    'si',
    'the',
    'to',
    'tu',
    'un',
    'una',
    'y',
    'yo',
  };

  Future<TextPreprocessingResult> preprocess(
    List<TelemetryEntry> entries,
  ) async {
    final payload = <String, Object>{
      'dimension': inputDimension,
      'vocabulary': vocabulary,
      'texts': entries
          .map((entry) => '${entry.originApp} ${entry.payload}')
          .toList(growable: false),
    };

    final raw = await compute(_buildInputVector, payload);
    return TextPreprocessingResult(
      vector: Float32List.fromList(
        (raw['vector'] as List<Object?>).cast<double>(),
      ),
      tokens: (raw['tokens'] as List<Object?>).cast<String>(),
      normalizedText: (raw['normalizedText'] as String?) ?? '',
    );
  }

  static Map<String, Object> _buildInputVector(Map<String, Object> payload) {
    final dimension = payload['dimension'] as int;
    final vocabulary = (payload['vocabulary'] as Map<Object?, Object?>).map(
      (key, value) => MapEntry(
        key.toString(),
        int.tryParse(value.toString()) ?? -1,
      ),
    );
    final texts = (payload['texts'] as List<Object?>).cast<String>();

    final normalized = texts
        .join(' ')
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9áéíóúñü\s]'), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();

    final tokens = normalized
        .split(' ')
        .where((token) => token.isNotEmpty)
        .where((token) => !_stopWords.contains(token))
        .toList(growable: false);

    final vector = List<double>.filled(dimension, 0);
    for (final token in tokens) {
      final directIndex = vocabulary[token];
      final index = (directIndex != null && directIndex >= 0)
          ? directIndex % dimension
          : token.hashCode.abs() % dimension;
      vector[index] += 1;
    }

    final maxValue = vector.fold<double>(0, (max, value) => value > max ? value : max);
    if (maxValue > 0) {
      for (var i = 0; i < vector.length; i++) {
        vector[i] = vector[i] / maxValue;
      }
    }

    return <String, Object>{
      'vector': vector,
      'tokens': tokens.take(24).toList(growable: false),
      'normalizedText': normalized,
    };
  }
}
