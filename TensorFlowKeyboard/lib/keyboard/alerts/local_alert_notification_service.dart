import 'dart:async';
import 'dart:convert';
import 'dart:ui';

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import '../../app/app_preferences_store.dart';
import '../ml/risk_assessment.dart';

const String _riskAlertChannelId = 'security_risk_alerts';
const String _riskAlertCategoryId = 'risk_alert_category';
const int _riskAlertNotificationId = 9171;
const String _actionOpenReportForm = 'open_report_form';
const String _actionDiscardAlert = 'discard_alert';

@pragma('vm:entry-point')
void notificationTapBackground(NotificationResponse response) {
  DartPluginRegistrant.ensureInitialized();
  WidgetsFlutterBinding.ensureInitialized();
  unawaited(
    AppPreferencesStore.instance.setPendingNotificationIntent(
      PendingNotificationIntent(
        actionId: _normalizeActionId(response),
        payload: response.payload,
      ),
    ),
  );
}

class LocalAlertCommand {
  const LocalAlertCommand({
    required this.actionId,
    this.payload,
  });

  final String actionId;
  final String? payload;

  bool get shouldOpenReportForm => actionId == _actionOpenReportForm;
  bool get shouldPurgeBuffer => actionId == _actionDiscardAlert;
}

class LocalAlertNotificationService {
  LocalAlertNotificationService._();

  static final LocalAlertNotificationService instance =
      LocalAlertNotificationService._();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  final StreamController<LocalAlertCommand> _commands =
      StreamController<LocalAlertCommand>.broadcast();

  bool _initialized = false;
  bool _available = true;

  Stream<LocalAlertCommand> get commands => _commands.stream;
  bool get isAvailable => _available;

  Future<void> initialize() async {
    if (_initialized) {
      await _emitPersistedAction();
      return;
    }

    try {
      const androidSettings =
          AndroidInitializationSettings('ic_keyboard_alert');
      final darwinSettings = DarwinInitializationSettings(
        requestAlertPermission: false,
        requestBadgePermission: false,
        requestSoundPermission: false,
        notificationCategories: <DarwinNotificationCategory>[
          DarwinNotificationCategory(
            _riskAlertCategoryId,
            actions: <DarwinNotificationAction>[
              DarwinNotificationAction.plain(
                _actionOpenReportForm,
                'Abrir formulario',
                options: <DarwinNotificationActionOption>{
                  DarwinNotificationActionOption.foreground,
                },
              ),
              DarwinNotificationAction.plain(
                _actionDiscardAlert,
                'Descartar',
                options: <DarwinNotificationActionOption>{
                  DarwinNotificationActionOption.destructive,
                  DarwinNotificationActionOption.foreground,
                },
              ),
            ],
          ),
        ],
      );
      final initializationSettings = InitializationSettings(
        android: androidSettings,
        iOS: darwinSettings,
        macOS: darwinSettings,
      );

      await _plugin.initialize(
        settings: initializationSettings,
        onDidReceiveNotificationResponse: _handleNotificationResponse,
        onDidReceiveBackgroundNotificationResponse: notificationTapBackground,
      );

      final androidImplementation =
          _plugin.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
      await androidImplementation?.createNotificationChannel(
        const AndroidNotificationChannel(
          _riskAlertChannelId,
          'Alertas locales de seguridad',
          description:
              'Alertas generadas por reglas locales dentro del teclado seguro.',
          importance: Importance.high,
        ),
      );

      final launchDetails = await _plugin.getNotificationAppLaunchDetails();
      if (launchDetails?.didNotificationLaunchApp == true &&
          launchDetails?.notificationResponse != null) {
        _handleNotificationResponse(launchDetails!.notificationResponse!);
      }

      await _emitPersistedAction();
      _initialized = true;
    } on MissingPluginException {
      _available = false;
    } catch (_) {
      _available = false;
    }
  }

  Future<void> requestPermissions() async {
    if (!_available) {
      return;
    }

    try {
      final androidImplementation =
          _plugin.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
      await androidImplementation?.requestNotificationsPermission();

      final iosImplementation = _plugin.resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin>();
      await iosImplementation?.requestPermissions(
        alert: true,
        badge: false,
        sound: true,
      );

      final macImplementation = _plugin.resolvePlatformSpecificImplementation<
          MacOSFlutterLocalNotificationsPlugin>();
      await macImplementation?.requestPermissions(
        alert: true,
        badge: false,
        sound: true,
      );
    } on MissingPluginException {
      _available = false;
    }
  }

  Future<void> showRiskAlert(
    RiskAssessment assessment, {
    String? originApp,
  }) async {
    if (!_available) {
      return;
    }
    await initialize();
    if (!_available) {
      return;
    }

    final payload = jsonEncode(
      <String, dynamic>{
        'category': assessment.category.name,
        'origin_app': originApp,
        'risk_probability': assessment.riskProbability,
      },
    );

    const androidDetails = AndroidNotificationDetails(
      _riskAlertChannelId,
      'Alertas locales de seguridad',
      channelDescription:
          'Alertas generadas por reglas locales dentro del teclado seguro.',
      importance: Importance.max,
      priority: Priority.high,
      category: AndroidNotificationCategory.message,
      ticker: 'Teclado Seguro alerta local',
      onlyAlertOnce: true,
      ongoing: true,
      autoCancel: false,
      icon: 'ic_keyboard_alert',
      actions: <AndroidNotificationAction>[
        AndroidNotificationAction(
          _actionOpenReportForm,
          'Abrir formulario',
          showsUserInterface: true,
          cancelNotification: false,
        ),
        AndroidNotificationAction(
          _actionDiscardAlert,
          'Descartar',
          showsUserInterface: true,
        ),
      ],
    );
    const darwinDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: false,
      presentSound: true,
      categoryIdentifier: _riskAlertCategoryId,
    );

    await _plugin.show(
      id: _riskAlertNotificationId,
      title: assessment.notificationTitle,
      body: assessment.notificationBody,
      notificationDetails: const NotificationDetails(
        android: androidDetails,
        iOS: darwinDetails,
        macOS: darwinDetails,
      ),
      payload: payload,
    );
  }

  Future<void> cancelRiskAlert() async {
    if (!_available) {
      return;
    }
    try {
      await _plugin.cancel(id: _riskAlertNotificationId);
    } on MissingPluginException {
      _available = false;
    }
  }

  void _handleNotificationResponse(NotificationResponse response) {
    final command = LocalAlertCommand(
      actionId: _normalizeActionId(response),
      payload: response.payload,
    );
    _commands.add(command);
  }

  Future<void> _emitPersistedAction() async {
    final pending =
        await AppPreferencesStore.instance.consumePendingNotificationIntent();
    if (pending == null) {
      return;
    }
    _commands.add(
      LocalAlertCommand(
        actionId: pending.actionId,
        payload: pending.payload,
      ),
    );
  }
}

String _normalizeActionId(NotificationResponse response) {
  final actionId = response.actionId;
  if (actionId == _actionDiscardAlert) {
    return _actionDiscardAlert;
  }
  if (actionId == _actionOpenReportForm ||
      response.notificationResponseType ==
          NotificationResponseType.selectedNotification) {
    return _actionOpenReportForm;
  }
  return actionId ?? _actionOpenReportForm;
}
