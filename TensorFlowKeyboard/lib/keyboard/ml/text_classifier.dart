import 'dart:async';
import 'dart:typed_data';

import 'package:tflite_flutter/tflite_flutter.dart';

import '../context/telemetry_entry.dart';
import 'risk_assessment.dart';
import 'text_preprocessor.dart';

abstract interface class TextClassifierBackend {
  Future<void> initialize();
  Future<double> predict({
    required Float32List inputVector,
    required List<String> tokens,
  });
  Future<void> close();
  String get status;
}

class TextClassifier {
  TextClassifier({
    TextPreprocessor? preprocessor,
    TextClassifierBackend? backend,
    this.threshold = 0.8,
  })  : _preprocessor = preprocessor ?? TextPreprocessor(),
        _backend = backend ?? _TfliteTextClassifierBackend();

  final TextPreprocessor _preprocessor;
  final TextClassifierBackend _backend;
  final double threshold;

  bool _initialized = false;
  Future<void>? _initialization;

  Future<void> initialize() async {
    if (_initialized) {
      return;
    }
    _initialization ??= _backend.initialize().then((_) {
      _initialized = true;
    });
    await _initialization;
  }

  Future<RiskAssessment> analyzeBuffer(List<TelemetryEntry> entries) async {
    if (entries.isEmpty) {
      return RiskAssessment(
        riskProbability: 0,
        threshold: threshold,
        tokens: const <String>[],
        modelStatus: _backend.status,
        category: RiskCategory.idle,
      );
    }

    if (!_initialized) {
      await initialize();
    }

    final prepared = await _preprocessor.preprocess(entries);
    if (prepared.tokens.isEmpty) {
      return RiskAssessment(
        riskProbability: 0,
        threshold: threshold,
        tokens: const <String>[],
        modelStatus: _backend.status,
        category: RiskCategory.idle,
      );
    }

    final probability = await _backend.predict(
      inputVector: prepared.vector,
      tokens: prepared.tokens,
    );

    return RiskAssessment(
      riskProbability: probability,
      threshold: threshold,
      tokens: prepared.tokens,
      modelStatus: _backend.status,
      category: RiskCategory.infer(prepared.tokens),
    );
  }

  Future<void> close() => _backend.close();
}

class _TfliteTextClassifierBackend implements TextClassifierBackend {
  _TfliteTextClassifierBackend();

  static const String _modelAssetPath =
      'assets/models/text_risk_classifier.tflite';

  Interpreter? _interpreter;
  IsolateInterpreter? _isolateInterpreter;
  String _status = 'Modelo local pendiente de carga.';

  @override
  String get status => _status;

  @override
  Future<void> initialize() async {
    try {
      final options = InterpreterOptions()..threads = 2;
      _interpreter = await Interpreter.fromAsset(
        _modelAssetPath,
        options: options,
      );
      _isolateInterpreter = await IsolateInterpreter.create(
        address: _interpreter!.address,
      );
      _status = 'Modelo TFLite cargado desde assets.';
    } catch (error) {
      _status = 'Modelo no disponible, usando fallback heurístico: $error';
    }
  }

  @override
  Future<double> predict({
    required Float32List inputVector,
    required List<String> tokens,
  }) async {
    if (_isolateInterpreter == null) {
      return _heuristicProbability(tokens);
    }

    try {
      final input = <List<double>>[inputVector.toList(growable: false)];
      final output = List<List<double>>.generate(
        1,
        (_) => List<double>.filled(1, 0),
      );
      await _isolateInterpreter!.run(input, output);
      return output.first.first.clamp(0.0, 1.0);
    } catch (error) {
      _status = 'Inferencia TFLite falló, usando fallback heurístico: $error';
      return _heuristicProbability(tokens);
    }
  }

  @override
  Future<void> close() async {
    await _isolateInterpreter?.close();
    _interpreter?.close();
  }

  double _heuristicProbability(List<String> tokens) {
    const weightedTerms = <String, double>{
      'otp': 0.55,
      'token': 0.25,
      'urgente': 0.3,
      'urgent': 0.3,
      'clave': 0.25,
      'password': 0.45,
      'verification': 0.35,
      'verify': 0.35,
      'banco': 0.25,
      'bank': 0.25,
      'transfer': 0.25,
      'transferencia': 0.25,
      'codigo': 0.3,
      'code': 0.3,
      'enlace': 0.2,
      'link': 0.2,
      'pago': 0.2,
      'payment': 0.2,
    };

    var score = 0.0;
    for (final token in tokens) {
      score += weightedTerms[token] ?? 0;
    }
    return score.clamp(0.0, 1.0);
  }
}
