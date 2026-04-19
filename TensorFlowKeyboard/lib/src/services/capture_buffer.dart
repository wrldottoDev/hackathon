import 'dart:collection';

import 'package:flutter/foundation.dart';

class CircularCaptureBuffer<T> extends ChangeNotifier {
  CircularCaptureBuffer({required this.capacity})
      : assert(capacity > 0, 'capacity must be greater than zero');

  final int capacity;
  final ListQueue<T> _items = ListQueue<T>();

  void add(T item) {
    if (_items.length == capacity) {
      _items.removeFirst();
    }
    _items.addLast(item);
    notifyListeners();
  }

  void clear() {
    if (_items.isEmpty) {
      return;
    }
    _items.clear();
    notifyListeners();
  }

  List<T> get items => List<T>.unmodifiable(_items.toList().reversed);
  int get length => _items.length;
}
