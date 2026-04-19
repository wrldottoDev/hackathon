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
        return 'Alerta de posible Grooming';
      case RiskCategory.trata:
        return 'Riesgo de Trata';
      case RiskCategory.sextorsion:
        return 'Alerta de posible Sextorsión';
      case RiskCategory.fraudeFinanciero:
        return 'Alerta de Fraude Financiero';
      case RiskCategory.riesgoGenerico:
        return 'Alerta de Riesgo Digital';
      case RiskCategory.idle:
        return 'Sin riesgo activo';
    }
  }

  String get notificationBody {
    switch (this) {
      case RiskCategory.grooming:
        return 'El análisis local detectó señales compatibles con grooming.';
      case RiskCategory.trata:
        return 'El análisis local detectó señales compatibles con trata o captación.';
      case RiskCategory.sextorsion:
        return 'El análisis local detectó amenazas o coerción de tipo sexual.';
      case RiskCategory.fraudeFinanciero:
        return 'El análisis local detectó patrones de fraude financiero o robo de credenciales.';
      case RiskCategory.riesgoGenerico:
        return 'El análisis local detectó un patrón riesgoso que requiere revisión.';
      case RiskCategory.idle:
        return 'No hay riesgo activo.';
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
    threshold: 0.8,
    tokens: <String>[],
    modelStatus: 'Sin análisis todavía.',
    category: RiskCategory.idle,
  );
}
