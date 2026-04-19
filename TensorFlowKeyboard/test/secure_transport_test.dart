import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:tensorflow_keyboard/keyboard/network/secure_alert_models.dart';
import 'package:tensorflow_keyboard/keyboard/network/secure_transport.dart';
import 'package:tensorflow_keyboard/keyboard/network/secure_transport_settings_store.dart';

const String _publicKeyPem = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvdh6gqfsikNiBtMQqBpQ
KGpMaKKnxMDi/uU3Gf3FwYGV7fE1cQdJp2Msz109T8EFUl73Uje8rZXWX/JRmFbF
w/vVpqDniGGG9OLa9fgxynkI2wIFq2IUmFnmNBEtucwCREQUid6+TMgXKyr1JC/M
4upEXH6A+fPDaEAHchQse7I7GslP53wEkvgKvXtmMaMTt1faOP/HAj+exx3GxxFl
X79sfo9pvWFEhWjTwjdeYcJDuA1JdF5c1B1svMabm927IgTl4t+H3Au5blCZVLxI
++Q49UuxkuBvKRijmHFgLNH4gvMVNRlrhswoP3P7+sIqxqQCbItSoBm5Ohz42mqL
KwIDAQAB
-----END PUBLIC KEY-----
''';

void main() {
  test('sends encrypted alert with SGT header', () async {
    final client = MockClient((request) async {
      expect(
        request.headers.entries.any(
          (entry) =>
              entry.key.toLowerCase() == 'x-sgt-tag' &&
              entry.value == 'CONATT-SECURE-ENTRY',
        ),
        isTrue,
      );

      final body = jsonDecode(request.body) as Map<String, dynamic>;
      expect(body['algorithm'], 'RSA-OAEP-256/AES-256-GCM');
      expect(body['ciphertext'], isNotEmpty);
      expect(body['encrypted_key'], isNotEmpty);
      expect(request.body.contains('mensaje'), isFalse);

      return http.Response(
        jsonEncode(<String, dynamic>{
          'id': 41,
          'hash_denuncia': 'abc123',
          'recibo_inmutabilidad': 'abc123',
          'timestamp': '2026-04-18T12:00:00Z',
          'estado_investigacion': 'pendiente',
        }),
        201,
        headers: const <String, String>{
          'content-type': 'application/json',
        },
      );
    });

    final transport = SecureTransport(
      httpClient: client,
      baseUri: Uri.parse('http://127.0.0.1:8000'),
      publicKeyLoader: () async => _publicKeyPem,
    );

    final receipt = await transport.sendAlert(
      SecureAlertReport(
        riskProbability: 0.92,
        bufferEntries: <SecureAlertBufferEntry>[
          SecureAlertBufferEntry(
            source: 'Keyboard',
            originApp: 'com.whatsapp',
            payload: 'mensaje sensible',
            timestamp: DateTime.utc(2026, 4, 18, 12),
          ),
        ],
        metadata: const <String, dynamic>{
          'host_mode': 'preview',
          'secure_mode': true,
        },
        extractedEntities: const <String>['otp', 'urgente'],
        originApp: 'com.whatsapp',
        createdAt: DateTime.utc(2026, 4, 18, 12),
      ),
    );

    expect(receipt.id, 41);
    expect(receipt.hashDenuncia, 'abc123');
    expect(receipt.estadoInvestigacion, 'pendiente');
  });

  test('uses runtime transport settings overrides', () async {
    final client = MockClient((request) async {
      expect(
        request.url.toString(),
        'https://analytics.vps.example.com/api/v1/alertas',
      );
      expect(
        request.headers['X-SGT-Tag'],
        'CONATT-VPS-ENTRY',
      );

      return http.Response(
        jsonEncode(<String, dynamic>{
          'id': 99,
          'hash_denuncia': 'xyz999',
          'recibo_inmutabilidad': 'xyz999',
          'timestamp': '2026-04-19T10:00:00Z',
          'estado_investigacion': 'pendiente',
        }),
        201,
        headers: const <String, String>{
          'content-type': 'application/json',
        },
      );
    });

    final transport = SecureTransport(
      httpClient: client,
      publicKeyLoader: () async => _publicKeyPem,
      settingsLoader: () async => const SecureTransportSettings(
        baseUrl: 'https://analytics.vps.example.com',
        sgtTag: 'CONATT-VPS-ENTRY',
      ),
    );

    final receipt = await transport.sendAlert(
      SecureAlertReport(
        riskProbability: 0.88,
        bufferEntries: <SecureAlertBufferEntry>[
          SecureAlertBufferEntry(
            source: 'Keyboard',
            originApp: 'com.telegram',
            payload: 'mensaje de prueba',
            timestamp: DateTime.utc(2026, 4, 19, 10),
          ),
        ],
        metadata: const <String, dynamic>{
          'host_mode': 'preview',
          'secure_mode': true,
        },
        extractedEntities: const <String>['prueba'],
        originApp: 'com.telegram',
        createdAt: DateTime.utc(2026, 4, 19, 10),
      ),
    );

    expect(receipt.id, 99);
    expect(receipt.hashDenuncia, 'xyz999');
  });
}
