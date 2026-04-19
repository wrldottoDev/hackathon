enum RiskCategory {
  idle,
  grooming,
  trata,
  sextorsion,
  fraudeFinanciero,
  riesgoGenerico;

  String get label {
    switch (this) {
      case RiskCategory.idle:
        return 'Sin riesgo';
      case RiskCategory.grooming:
        return 'Posible Grooming';
      case RiskCategory.trata:
        return 'Riesgo de Trata';
      case RiskCategory.sextorsion:
        return 'Posible Sextorsión';
      case RiskCategory.fraudeFinanciero:
        return 'Fraude Financiero';
      case RiskCategory.riesgoGenerico:
        return 'Riesgo Genérico';
    }
  }

  String get notificationTitle {
    switch (this) {
      case RiskCategory.grooming:
        return 'Posible grooming detectado';
      case RiskCategory.trata:
        return 'Posible captación detectada';
      case RiskCategory.sextorsion:
        return 'Posible sextorsión detectada';
      case RiskCategory.fraudeFinanciero:
        return 'Posible fraude financiero';
      case RiskCategory.riesgoGenerico:
        return 'Riesgo digital local';
      case RiskCategory.idle:
        return 'Sin hallazgos activos';
    }
  }

  String get notificationBody {
    switch (this) {
      case RiskCategory.grooming:
        return 'Las reglas locales detectaron frases compatibles con grooming.';
      case RiskCategory.trata:
        return 'Las reglas locales detectaron frases compatibles con captación o trata.';
      case RiskCategory.sextorsion:
        return 'Las reglas locales detectaron amenazas o coerción sexual.';
      case RiskCategory.fraudeFinanciero:
        return 'Las reglas locales detectaron patrones de fraude o robo de credenciales.';
      case RiskCategory.riesgoGenerico:
        return 'Las reglas locales detectaron un patrón riesgoso que conviene revisar.';
      case RiskCategory.idle:
        return 'No hay coincidencias locales relevantes.';
    }
  }

  static RiskCategory infer(Iterable<String> tokens) {
    final tokenSet = tokens.map((token) => token.toLowerCase()).toSet();
    final scores = <RiskCategory, double>{
      RiskCategory.grooming: _scoreMatches(
        tokenSet,
        const <String, double>{
          'menor': 0.75,
          'niña': 0.65,
          'nina': 0.65,
          'niño': 0.65,
          'nino': 0.65,
          'secreto': 0.45,
          'privado': 0.35,
          'foto': 0.2,
          'videollamada': 0.35,
          'regalo': 0.25,
        },
      ),
      RiskCategory.trata: _scoreMatches(
        tokenSet,
        const <String, double>{
          'empleo': 0.45,
          'trabajo': 0.45,
          'agencia': 0.3,
          'viaje': 0.35,
          'traslado': 0.35,
          'frontera': 0.35,
          'pasaporte': 0.45,
          'modelo': 0.25,
          'contrato': 0.2,
          'adelanto': 0.2,
        },
      ),
      RiskCategory.sextorsion: _scoreMatches(
        tokenSet,
        const <String, double>{
          'desnudo': 0.65,
          'foto': 0.2,
          'video': 0.2,
          'íntimo': 0.55,
          'intimo': 0.55,
          'amenaza': 0.45,
          'filtrar': 0.45,
          'publicar': 0.35,
          'vergüenza': 0.35,
          'verguenza': 0.35,
        },
      ),
      RiskCategory.fraudeFinanciero: _scoreMatches(
        tokenSet,
        const <String, double>{
          'otp': 0.75,
          'token': 0.45,
          'clave': 0.45,
          'password': 0.65,
          'codigo': 0.35,
          'banco': 0.35,
          'transferencia': 0.3,
          'transfer': 0.3,
          'sinpe': 0.35,
          'link': 0.2,
          'enlace': 0.2,
        },
      ),
    };

    var bestCategory = RiskCategory.riesgoGenerico;
    var bestScore = 0.0;
    for (final entry in scores.entries) {
      if (entry.value > bestScore) {
        bestCategory = entry.key;
        bestScore = entry.value;
      }
    }

    if (bestScore <= 0) {
      return RiskCategory.riesgoGenerico;
    }
    return bestCategory;
  }

  static double _scoreMatches(
    Set<String> tokens,
    Map<String, double> weightedTerms,
  ) {
    var score = 0.0;
    for (final token in tokens) {
      score += weightedTerms[token] ?? 0.0;
    }
    return score;
  }
}

class RiskAssessment {
  const RiskAssessment({
    required this.riskProbability,
    required this.threshold,
    required this.tokens,
    required this.modelStatus,
    required this.category,
  });

  final double riskProbability;
  final double threshold;
  final List<String> tokens;
  final String modelStatus;
  final RiskCategory category;

  bool get shouldTriggerAlert => riskProbability > threshold;
  String get notificationTitle => category.notificationTitle;
  String get notificationBody => category.notificationBody;
  String get categoryLabel => category.label;

  String get alertFingerprint =>
      '${category.name}:${tokens.take(8).join("|")}:${riskProbability.toStringAsFixed(2)}';

  static const idle = RiskAssessment(
    riskProbability: 0,
    threshold: 0.58,
    tokens: <String>[],
    modelStatus: 'Motor local por palabras listo.',
    category: RiskCategory.idle,
  );
}
