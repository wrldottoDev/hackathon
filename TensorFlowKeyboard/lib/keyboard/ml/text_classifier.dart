import '../context/telemetry_entry.dart';
import 'risk_assessment.dart';
import 'text_preprocessor.dart';

class TextClassifier {
  TextClassifier({
    TextPreprocessor? preprocessor,
    this.threshold = 0.58,
  }) : _preprocessor = preprocessor ?? TextPreprocessor();

  final TextPreprocessor _preprocessor;
  final double threshold;

  bool _initialized = false;

  Future<void> initialize() async {
    _initialized = true;
  }

  Future<RiskAssessment> analyzeBuffer(List<TelemetryEntry> entries) async {
    if (entries.isEmpty) {
      return RiskAssessment(
        riskProbability: 0,
        threshold: threshold,
        tokens: const <String>[],
        modelStatus: 'Sin texto reciente para evaluar.',
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
        modelStatus: 'No hubo palabras relevantes luego de limpiar el texto.',
        category: RiskCategory.idle,
      );
    }

    final evaluation = _evaluateSignals(
      normalizedText: prepared.normalizedText,
      rawTokens: prepared.tokens,
    );

    return RiskAssessment(
      riskProbability: evaluation.score,
      threshold: threshold,
      tokens: evaluation.signals,
      modelStatus: evaluation.status,
      category: evaluation.category,
    );
  }

  Future<void> close() async {}
}

class _KeywordEvaluation {
  const _KeywordEvaluation({
    required this.score,
    required this.category,
    required this.signals,
    required this.status,
  });

  final double score;
  final RiskCategory category;
  final List<String> signals;
  final String status;
}

_KeywordEvaluation _evaluateSignals({
  required String normalizedText,
  required List<String> rawTokens,
}) {
  final simplifiedText = _simplifyText(normalizedText);
  final tokenSet = rawTokens
      .map(_simplifyToken)
      .where((token) => !_ignoredTokens.contains(token))
      .toSet();

  final groomingSignals = <String>[];
  final trataSignals = <String>[];
  final sextorsionSignals = <String>[];
  final fraudeSignals = <String>[];
  final genericSignals = <String>[];

  var groomingScore = 0.0;
  var trataScore = 0.0;
  var sextorsionScore = 0.0;
  var fraudeScore = 0.0;
  var genericScore = 0.0;

  final minorAgeMatches = RegExp(r'\b(\d{1,2})\s+anos\b')
      .allMatches(simplifiedText)
      .map((match) => int.tryParse(match.group(1) ?? ''))
      .whereType<int>()
      .where((age) => age < 18)
      .toList(growable: false);
  if (minorAgeMatches.isNotEmpty) {
    groomingScore += 0.78;
    groomingSignals.add('${minorAgeMatches.first} años');
  }

  if (_containsAnyPhrase(simplifiedText, const <String>[
    'cuantos anos tienes',
    'que edad tienes',
    'eres menor',
    'estas sola',
    'no le digas a nadie',
  ])) {
    groomingScore += 0.34;
    groomingSignals.add('pregunta de edad o secreto');
  }

  groomingScore += _matchWeightedTerms(
    tokenSet,
    const <String, double>{
      'nina': 0.18,
      'nino': 0.18,
      'menor': 0.18,
      'colegio': 0.14,
      'uniforme': 0.14,
      'foto': 0.12,
      'videollamada': 0.16,
      'privado': 0.12,
      'regalo': 0.12,
      'secreto': 0.16,
      'sola': 0.12,
    },
    groomingSignals,
  );

  if (minorAgeMatches.isNotEmpty &&
      _containsAnyTerm(tokenSet, const <String>[
        'foto',
        'videollamada',
        'privado',
        'secreto',
      ])) {
    groomingScore += 0.18;
    groomingSignals.add('menor + contacto privado');
  }

  trataScore += _matchWeightedTerms(
    tokenSet,
    const <String, double>{
      'trabajo': 0.16,
      'empleo': 0.16,
      'modelo': 0.22,
      'agencia': 0.18,
      'casting': 0.18,
      'hotel': 0.18,
      'viaje': 0.16,
      'pasaporte': 0.2,
      'frontera': 0.18,
      'jaco': 0.24,
      'mesera': 0.18,
      'masajista': 0.18,
      'adelanto': 0.16,
      'discreta': 0.14,
    },
    trataSignals,
  );
  if (_containsAnyPhrase(simplifiedText, const <String>[
    'buscamos chicas',
    'oportunidad de trabajo',
    'te pagamos el viaje',
    'trabajo en hotel',
    'modelo para eventos',
  ])) {
    trataScore += 0.34;
    trataSignals.add('oferta laboral sospechosa');
  }
  if (_containsAllTerms(tokenSet, const <String>['modelo', 'hotel']) ||
      _containsAllTerms(tokenSet, const <String>['trabajo', 'jaco']) ||
      _containsAllTerms(tokenSet, const <String>['viaje', 'pasaporte'])) {
    trataScore += 0.18;
    trataSignals.add('combinación de captación');
  }

  sextorsionScore += _matchWeightedTerms(
    tokenSet,
    const <String, double>{
      'desnudo': 0.24,
      'desnuda': 0.24,
      'nudes': 0.24,
      'intimo': 0.22,
      'foto': 0.12,
      'video': 0.12,
      'viral': 0.16,
      'filtrar': 0.2,
      'publicar': 0.18,
      'familia': 0.12,
      'pagar': 0.18,
      'dinero': 0.12,
    },
    sextorsionSignals,
  );
  if (_containsAnyPhrase(simplifiedText, const <String>[
    'si no pagas',
    'voy a publicar',
    'voy a filtrar',
    'se lo mando a tu familia',
    'subo tus fotos',
  ])) {
    sextorsionScore += 0.4;
    sextorsionSignals.add('amenaza de difusión');
  }
  if (_containsAnyTerm(tokenSet, const <String>['foto', 'video']) &&
      _containsAnyTerm(
          tokenSet, const <String>['pagar', 'filtrar', 'publicar'])) {
    sextorsionScore += 0.18;
    sextorsionSignals.add('contenido íntimo + presión');
  }

  fraudeScore += _matchWeightedTerms(
    tokenSet,
    const <String, double>{
      'otp': 0.34,
      'codigo': 0.24,
      'clave': 0.22,
      'password': 0.26,
      'banco': 0.22,
      'sinpe': 0.22,
      'tarjeta': 0.2,
      'cuenta': 0.16,
      'link': 0.16,
      'enlace': 0.16,
      'verifica': 0.18,
      'verificacion': 0.18,
      'token': 0.18,
      'transferencia': 0.16,
    },
    fraudeSignals,
  );
  if (RegExp(r'\b(?:otp|codigo|clave)\b.*\b\d{4,8}\b')
          .hasMatch(simplifiedText) ||
      RegExp(r'\b\d{4,8}\b.*\b(?:otp|codigo|clave)\b')
          .hasMatch(simplifiedText)) {
    fraudeScore += 0.38;
    fraudeSignals.add('código sensible + números');
  }
  if (_containsAnyPhrase(simplifiedText, const <String>[
    'verifica tu cuenta',
    'actualiza tu banco',
    'te enviamos un link',
    'codigo de seguridad',
  ])) {
    fraudeScore += 0.3;
    fraudeSignals.add('frase típica de fraude');
  }
  if (_containsAllTerms(tokenSet, const <String>['banco', 'link']) ||
      _containsAllTerms(tokenSet, const <String>['sinpe', 'codigo'])) {
    fraudeScore += 0.16;
    fraudeSignals.add('combinación bancaria');
  }

  genericScore += _matchWeightedTerms(
    tokenSet,
    const <String, double>{
      'urgente': 0.16,
      'secreto': 0.16,
      'borralo': 0.2,
      'eliminalo': 0.2,
      'telegram': 0.14,
      'whatsapp': 0.1,
      'pago': 0.1,
    },
    genericSignals,
  );
  if (_containsAnyPhrase(simplifiedText, const <String>[
    'hablame por telegram',
    'borra este chat',
    'esto queda entre nosotros',
  ])) {
    genericScore += 0.24;
    genericSignals.add('desvío o secreto');
  }

  final scores = <RiskCategory, double>{
    RiskCategory.grooming: groomingScore.clamp(0.0, 1.0),
    RiskCategory.trata: trataScore.clamp(0.0, 1.0),
    RiskCategory.sextorsion: sextorsionScore.clamp(0.0, 1.0),
    RiskCategory.fraudeFinanciero: fraudeScore.clamp(0.0, 1.0),
    RiskCategory.riesgoGenerico: genericScore.clamp(0.0, 1.0),
  };
  final signalsByCategory = <RiskCategory, List<String>>{
    RiskCategory.grooming: groomingSignals,
    RiskCategory.trata: trataSignals,
    RiskCategory.sextorsion: sextorsionSignals,
    RiskCategory.fraudeFinanciero: fraudeSignals,
    RiskCategory.riesgoGenerico: genericSignals,
  };

  var bestCategory = RiskCategory.idle;
  var bestScore = 0.0;
  for (final entry in scores.entries) {
    if (entry.value > bestScore) {
      bestCategory = entry.key;
      bestScore = entry.value;
    }
  }

  final bestSignals = signalsByCategory[bestCategory] ?? const <String>[];
  if (bestScore <= 0) {
    return const _KeywordEvaluation(
      score: 0,
      category: RiskCategory.idle,
      signals: <String>[],
      status: 'Reglas locales activas, sin coincidencias todavía.',
    );
  }

  final visibleSignals = bestSignals.take(8).toList(growable: false);
  final status = visibleSignals.isEmpty
      ? 'Reglas locales activas con una coincidencia débil.'
      : 'Reglas locales activas. Coincidencias: ${visibleSignals.join(', ')}.';

  return _KeywordEvaluation(
    score: bestScore.clamp(0.0, 1.0),
    category: bestCategory,
    signals: visibleSignals,
    status: status,
  );
}

double _matchWeightedTerms(
  Set<String> tokenSet,
  Map<String, double> weightedTerms,
  List<String> matchedSignals,
) {
  var score = 0.0;
  for (final entry in weightedTerms.entries) {
    if (!tokenSet.contains(entry.key)) {
      continue;
    }
    score += entry.value;
    if (!matchedSignals.contains(entry.key)) {
      matchedSignals.add(entry.key);
    }
  }
  return score;
}

bool _containsAnyPhrase(String normalizedText, List<String> phrases) {
  for (final phrase in phrases) {
    if (normalizedText.contains(phrase)) {
      return true;
    }
  }
  return false;
}

bool _containsAnyTerm(Set<String> tokenSet, List<String> terms) {
  for (final term in terms) {
    if (tokenSet.contains(term)) {
      return true;
    }
  }
  return false;
}

bool _containsAllTerms(Set<String> tokenSet, List<String> terms) {
  for (final term in terms) {
    if (!tokenSet.contains(term)) {
      return false;
    }
  }
  return true;
}

String _simplifyText(String value) {
  return value
      .replaceAll('á', 'a')
      .replaceAll('é', 'e')
      .replaceAll('í', 'i')
      .replaceAll('ó', 'o')
      .replaceAll('ú', 'u')
      .replaceAll('ü', 'u')
      .replaceAll('ñ', 'n');
}

String _simplifyToken(String token) => _simplifyText(token.toLowerCase());

const Set<String> _ignoredTokens = <String>{
  'com',
  'android',
  'instagram',
  'whatsapp',
  'telegram',
  'preview',
  'flutter',
};
