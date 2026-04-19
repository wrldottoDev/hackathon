import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:basic_utils/basic_utils.dart';
import 'package:cryptography/cryptography.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'package:pointycastle/export.dart';

import 'secure_alert_models.dart';
import 'secure_transport_settings_store.dart';

typedef PublicKeyLoader = Future<String> Function();
typedef SecureTransportSettingsLoader = Future<SecureTransportSettings>
    Function();

class SecureTransportException implements Exception {
  const SecureTransportException(this.message);

  final String message;

  @override
  String toString() => message;
}

class SecureTransport {
  SecureTransport({
    http.Client? httpClient,
    Uri? baseUri,
    String? sgtTag,
    PublicKeyLoader? publicKeyLoader,
    SecureTransportSettingsLoader? settingsLoader,
  })  : _httpClient = httpClient ?? http.Client(),
        _ownsHttpClient = httpClient == null,
        _baseUri = baseUri ?? _defaultBaseUri,
        sgtTag = sgtTag ?? _defaultSgtTag,
        _publicKeyLoader = publicKeyLoader ?? _loadBundledPublicKey,
        _settingsLoader =
            settingsLoader ?? SecureTransportSettingsStore.instance.load;

  static const String _defaultSgtTag = 'CONATT-SECURE-ENTRY';
  static const String _defaultPublicKeyAsset =
      'assets/security/alert_server_public.pem';
  static final Uri _defaultBaseUri = Uri.parse(
    const String.fromEnvironment(
      'SECURE_ALERTS_BASE_URL',
      defaultValue: 'https://analytics.lynqcr.com',
    ),
  );
  static const Duration _requestTimeout = Duration(seconds: 15);

  final http.Client _httpClient;
  final bool _ownsHttpClient;
  final Uri _baseUri;
  final String sgtTag;
  final PublicKeyLoader _publicKeyLoader;
  final SecureTransportSettingsLoader _settingsLoader;
  final AesGcm _aesGcm = AesGcm.with256bits();

  static Uri get defaultBaseUri => _defaultBaseUri;
  static String get defaultSgtTag => _defaultSgtTag;

  Future<SecureAlertReceipt> sendAlert(SecureAlertReport report) async {
    final envelope = await buildEncryptedEnvelope(report);
    final settings = await _settingsLoader();
    final endpoint = _resolveBaseUri(settings);
    final activeSgtTag = _resolveSgtTag(settings);
    late final http.Response response;

    try {
      response = await _httpClient
          .post(
            endpoint.resolve('/api/v1/alertas'),
            headers: <String, String>{
              'Content-Type': 'application/json',
              'X-SGT-Tag': activeSgtTag,
            },
            body: jsonEncode(envelope),
          )
          .timeout(_requestTimeout);
    } on TimeoutException {
      throw const SecureTransportException(
        'Tiempo de espera agotado al contactar el servidor de alertas.',
      );
    } on SocketException {
      throw const SecureTransportException(
        'No se pudo conectar con el servidor de alertas. Verifica la URL y la conectividad.',
      );
    } on http.ClientException {
      throw const SecureTransportException(
        'La conexión con el servidor de alertas falló. Revisa la URL configurada y el certificado HTTPS.',
      );
    }

    if (response.statusCode != 201) {
      throw SecureTransportException(
        _buildFailureMessage(response),
      );
    }

    final payload = jsonDecode(response.body);
    if (payload is! Map<String, dynamic>) {
      throw const SecureTransportException(
        'Respuesta inválida del servidor de alertas.',
      );
    }
    return SecureAlertReceipt.fromJson(payload);
  }

  Future<Map<String, dynamic>> buildEncryptedEnvelope(
    SecureAlertReport report,
  ) async {
    final publicKeyPem = await _publicKeyLoader();
    final publicKey = CryptoUtils.rsaPublicKeyFromPem(publicKeyPem);
    final encodedPayload = Uint8List.fromList(
      utf8.encode(jsonEncode(report.toJson())),
    );
    final sessionKey = await _aesGcm.newSecretKey();
    final sessionKeyBytes = Uint8List.fromList(await sessionKey.extractBytes());
    final secretBox = await _aesGcm.encrypt(
      encodedPayload,
      secretKey: sessionKey,
      nonce: _aesGcm.newNonce(),
    );

    return <String, dynamic>{
      'algorithm': 'RSA-OAEP-256/AES-256-GCM',
      'key_fingerprint': await _fingerprint(publicKeyPem),
      'encrypted_key':
          base64Encode(_encryptSessionKey(sessionKeyBytes, publicKey)),
      'nonce': base64Encode(secretBox.nonce),
      'ciphertext': base64Encode(secretBox.cipherText),
      'mac': base64Encode(secretBox.mac.bytes),
    };
  }

  void dispose() {
    if (_ownsHttpClient) {
      _httpClient.close();
    }
  }

  Uri _resolveBaseUri(SecureTransportSettings settings) {
    final configuredBaseUrl = settings.baseUrl;
    if (configuredBaseUrl == null || configuredBaseUrl.isEmpty) {
      return _baseUri;
    }

    final parsedUri = Uri.tryParse(configuredBaseUrl);
    if (parsedUri == null || !parsedUri.hasAuthority) {
      throw const SecureTransportException(
        'La URL configurada para el servidor de alertas no es válida.',
      );
    }
    return parsedUri;
  }

  String _resolveSgtTag(SecureTransportSettings settings) {
    final configuredTag = settings.sgtTag;
    if (configuredTag == null || configuredTag.isEmpty) {
      return sgtTag;
    }
    return configuredTag;
  }

  String _buildFailureMessage(http.Response response) {
    final genericMessage =
        'No se pudo entregar la alerta cifrada. Servidor respondió ${response.statusCode}.';
    if (response.body.trim().isEmpty) {
      return genericMessage;
    }

    try {
      final payload = jsonDecode(response.body);
      if (payload is Map<String, dynamic>) {
        final detail = payload['detail']?.toString().trim();
        if (detail != null && detail.isNotEmpty) {
          return '$genericMessage $detail';
        }
      }
    } catch (_) {
      // The backend may return plain text or HTML on infra failures.
    }

    return genericMessage;
  }

  Uint8List _encryptSessionKey(Uint8List sessionKey, RSAPublicKey publicKey) {
    final encryptor = OAEPEncoding.withSHA256(RSAEngine())
      ..init(true, PublicKeyParameter<RSAPublicKey>(publicKey));
    return encryptor.process(sessionKey);
  }

  Future<String> _fingerprint(String pem) async {
    final body = pem
        .split('\n')
        .where(
          (line) =>
              !line.startsWith('-----BEGIN') && !line.startsWith('-----END'),
        )
        .join();
    final digest = await Sha256().hash(base64Decode(body));
    return _toHex(digest.bytes);
  }

  String _toHex(List<int> bytes) {
    final buffer = StringBuffer();
    for (final byte in bytes) {
      buffer.write(byte.toRadixString(16).padLeft(2, '0'));
    }
    return buffer.toString();
  }

  static Future<String> _loadBundledPublicKey() {
    return rootBundle.loadString(_defaultPublicKeyAsset);
  }
}
