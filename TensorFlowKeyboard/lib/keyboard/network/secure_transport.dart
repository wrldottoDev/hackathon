import 'dart:convert';
import 'dart:typed_data';

import 'package:basic_utils/basic_utils.dart';
import 'package:cryptography/cryptography.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'package:pointycastle/export.dart';

import 'secure_alert_models.dart';

typedef PublicKeyLoader = Future<String> Function();

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
    this.sgtTag = _defaultSgtTag,
    PublicKeyLoader? publicKeyLoader,
  })  : _httpClient = httpClient ?? http.Client(),
        _ownsHttpClient = httpClient == null,
        _baseUri = baseUri ?? _defaultBaseUri,
        _publicKeyLoader = publicKeyLoader ?? _loadBundledPublicKey;

  static const String _defaultSgtTag = 'CONATT-SECURE-ENTRY';
  static const String _defaultPublicKeyAsset =
      'assets/security/alert_server_public.pem';
  static final Uri _defaultBaseUri = Uri.parse(
    const String.fromEnvironment(
      'SECURE_ALERTS_BASE_URL',
      defaultValue: 'http://127.0.0.1:8000',
    ),
  );

  final http.Client _httpClient;
  final bool _ownsHttpClient;
  final Uri _baseUri;
  final String sgtTag;
  final PublicKeyLoader _publicKeyLoader;
  final AesGcm _aesGcm = AesGcm.with256bits();

  Future<SecureAlertReceipt> sendAlert(SecureAlertReport report) async {
    final envelope = await buildEncryptedEnvelope(report);
    final response = await _httpClient.post(
      _baseUri.resolve('/api/v1/alertas'),
      headers: <String, String>{
        'Content-Type': 'application/json',
        'X-SGT-Tag': sgtTag,
      },
      body: jsonEncode(envelope),
    );

    if (response.statusCode != 201) {
      throw const SecureTransportException(
        'No se pudo entregar la alerta cifrada.',
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
