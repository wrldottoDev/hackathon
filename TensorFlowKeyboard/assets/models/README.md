Place the production TensorFlow Lite model here as:

`assets/models/text_risk_classifier.tflite`

The current Dart integration will attempt to load that asset asynchronously.
If the file is absent or invalid, the app falls back to a local heuristic scorer
so the rest of the pipeline remains testable.
