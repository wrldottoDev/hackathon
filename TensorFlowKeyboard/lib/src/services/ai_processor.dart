import '../models/capture_item.dart';

abstract interface class CaptureProcessor {
  Future<void> process(CaptureItem item);
}

class NoopCaptureProcessor implements CaptureProcessor {
  const NoopCaptureProcessor();

  @override
  Future<void> process(CaptureItem item) async {}
}
