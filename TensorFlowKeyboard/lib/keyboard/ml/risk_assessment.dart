class RiskAssessment {
  const RiskAssessment({
    required this.riskProbability,
    required this.threshold,
    required this.tokens,
    required this.modelStatus,
  });

  final double riskProbability;
  final double threshold;
  final List<String> tokens;
  final String modelStatus;

  bool get shouldTriggerAlert => riskProbability > threshold;

  static const idle = RiskAssessment(
    riskProbability: 0,
    threshold: 0.8,
    tokens: <String>[],
    modelStatus: 'Sin análisis todavía.',
  );
}
