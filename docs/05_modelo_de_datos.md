# 05. Modelo de Datos

## Introducción

El modelo de datos de FlowLens está diseñado para representar un ecosistema bancario distribuido, donde múltiples bancos operan de forma independiente con sus propias bases de datos, pero pueden intercambiar transacciones y ser observados por una aplicación externa de analytics.

La estructura de datos busca cubrir dos dimensiones principales del sistema:

1. la operación bancaria simulada;
2. el análisis transaccional y la trazabilidad de cuentas.

Por esta razón, el modelo se divide conceptualmente en dos grandes bloques:

- entidades del dominio bancario;
- entidades del dominio analítico.

Además, se contempla la existencia de datos compartidos a nivel lógico, como códigos de banco, identificadores de cuentas y metadatos de transacción, que permiten interoperabilidad entre módulos sin romper la independencia de cada entidad.

---

## Objetivo del modelo de datos

El propósito del modelo de datos es:

- representar correctamente usuarios, cuentas y transacciones;
- permitir el registro local de operaciones en cada banco;
- facilitar la comunicación entre bancos;
- permitir la consulta y análisis de movimientos desde analytics;
- soportar seguimiento profundo de cuentas;
- dejar una base clara para implementar reglas de riesgo y visualización de redes.

---

## Principios de diseño del modelo

El diseño del modelo de datos se apoya en los siguientes principios:

### Independencia por banco

Cada banco mantiene su propia persistencia, por lo que sus entidades operativas viven en su propia base de datos.

### Identificación clara de entidades

Cada cuenta, transacción y banco debe poder identificarse de forma única y comprensible.

### Trazabilidad

Toda operación relevante debe quedar registrada con suficiente contexto para poder ser analizada posteriormente.

### Escalabilidad conceptual

El modelo debe permitir agregar nuevas entidades y nuevos bancos sin rediseñar completamente la estructura.

### Compatibilidad analítica

Los datos operativos deben ser lo suficientemente consistentes para que analytics pueda interpretarlos y consolidarlos.

---

## Entidades principales del dominio bancario

### 1. Bank

La entidad **Bank** representa una institución bancaria simulada dentro del ecosistema.

Aunque cada banco puede existir como sistema independiente, esta entidad también puede utilizarse en módulos como analytics o en un registro central para identificar las entidades participantes.

#### Atributos sugeridos

- `id`
- `name`
- `code`
- `api_url`
- `status`
- `created_at`

#### Descripción de atributos

- **id**: identificador interno del banco.
- **name**: nombre oficial o visible del banco.
- **code**: código corto único que identifica a la entidad, por ejemplo `BKA` o `BKB`.
- **api_url**: dirección base de la API del banco para integraciones.
- **status**: estado de disponibilidad o activación del banco dentro del ecosistema.
- **created_at**: fecha de registro de la entidad.

#### Justificación

La existencia de un código único de banco es esencial para enrutar transacciones interbancarias, identificar a qué entidad pertenece una cuenta y facilitar el análisis global de la red.

---

### 2. User

La entidad **User** representa al cliente de un banco.

#### Atributos sugeridos

- `id`
- `full_name`
- `email`
- `hashed_password`
- `role`
- `created_at`

#### Descripción de atributos

- **id**: identificador único del usuario.
- **full_name**: nombre completo del cliente.
- **email**: correo electrónico del usuario, utilizado para autenticación y contacto.
- **hashed_password**: contraseña protegida mediante hash.
- **role**: rol del usuario dentro del sistema, por ejemplo `client`, `analyst` o `admin`, según el módulo.
- **created_at**: fecha de creación del usuario.

#### Justificación

El usuario es la entidad que opera cuentas dentro del banco. Su información debe permitir autenticación segura y trazabilidad de propiedad sobre las cuentas.

---

### 3. Account

La entidad **Account** representa una cuenta bancaria perteneciente a un usuario y emitida por un banco específico.

#### Atributos sugeridos

- `id`
- `account_number`
- `user_id`
- `bank_code`
- `balance`
- `currency`
- `status`
- `created_at`

#### Descripción de atributos

- **id**: identificador interno de la cuenta.
- **account_number**: número de cuenta único, idealmente con un formato que incorpore el banco, por ejemplo `BKA-000001`.
- **user_id**: referencia al usuario propietario de la cuenta.
- **bank_code**: código del banco al que pertenece la cuenta.
- **balance**: saldo actual disponible en la cuenta.
- **currency**: moneda de la cuenta, por ejemplo `CRC`.
- **status**: estado de la cuenta, como activa, bloqueada o suspendida.
- **created_at**: fecha de creación de la cuenta.

#### Justificación

La cuenta es el eje principal del sistema bancario. Su diseño debe permitir saber claramente quién es su propietario, a qué banco pertenece y cuál es su estado financiero actual.

---

### 4. Transaction

La entidad **Transaction** representa un movimiento de dinero entre cuentas.

#### Atributos sugeridos

- `id`
- `source_account_number`
- `destination_account_number`
- `source_bank_code`
- `destination_bank_code`
- `amount`
- `currency`
- `transaction_type`
- `status`
- `channel`
- `location`
- `description`
- `created_at`

#### Descripción de atributos

- **id**: identificador único de la transacción.
- **source_account_number**: cuenta origen de la operación.
- **destination_account_number**: cuenta destino de la operación.
- **source_bank_code**: banco emisor.
- **destination_bank_code**: banco receptor.
- **amount**: monto transferido.
- **currency**: moneda utilizada en la operación.
- **transaction_type**: tipo de movimiento, por ejemplo transferencia interna, interbancaria, depósito o retiro.
- **status**: estado de la operación, como pendiente, completada, fallida o marcada.
- **channel**: canal por el cual se ejecutó la operación, por ejemplo web, mobile, api o atm.
- **location**: ubicación o referencia contextual del origen de la operación.
- **description**: detalle descriptivo opcional.
- **created_at**: fecha y hora exacta de la transacción.

#### Justificación

La transacción es la entidad más importante para analytics, porque a partir de ella se construyen reglas de riesgo, cadenas de trazabilidad, grafos de relaciones y alertas.

---

## Entidades principales del dominio analítico

### 5. RiskAlert

La entidad **RiskAlert** representa una alerta generada por el sistema de analytics al detectar un patrón sospechoso o una operación que supera un umbral de riesgo.

#### Atributos sugeridos

- `id`
- `transaction_id`
- `account_number`
- `bank_code`
- `score`
- `level`
- `reason`
- `pattern_type`
- `created_at`

#### Descripción de atributos

- **id**: identificador de la alerta.
- **transaction_id**: transacción asociada a la alerta, si aplica.
- **account_number**: cuenta relacionada con el hallazgo.
- **bank_code**: banco al que pertenece la cuenta observada.
- **score**: puntaje numérico de riesgo.
- **level**: clasificación del riesgo, por ejemplo `low`, `medium` o `high`.
- **reason**: explicación legible del motivo de la alerta.
- **pattern_type**: categoría del patrón detectado, como anomalía, fragmentación, cadena rápida o concentración.
- **created_at**: fecha de generación de la alerta.

#### Justificación

La alerta permite traducir el análisis técnico en una salida comprensible para el analista, facilitando priorización, seguimiento y visualización.

---

### 6. BankRegistry

La entidad **BankRegistry** puede utilizarse dentro del módulo de analytics para mantener un registro de los bancos disponibles para monitoreo.

#### Atributos sugeridos

- `id`
- `bank_name`
- `bank_code`
- `api_url`
- `status`
- `created_at`

#### Justificación

Esta entidad facilita administrar qué bancos forman parte del ecosistema y cuáles están habilitados para ser observados por el sistema analítico.

---

### 7. AnalysisTrace o FollowUpRecord

Como parte del seguimiento profundo, puede contemplarse una entidad orientada a registrar hallazgos o consultas analíticas sobre una cuenta específica.

#### Atributos sugeridos

- `id`
- `account_number`
- `bank_code`
- `summary`
- `risk_score`
- `notes`
- `created_at`

#### Justificación

Aunque no es estrictamente necesaria en la primera iteración, esta entidad puede ser útil si se desea persistir resúmenes de seguimiento profundo o resultados analíticos acumulados.

---

## Relaciones principales entre entidades

### Relación User - Account

- Un usuario puede tener una o varias cuentas.
- Cada cuenta pertenece a un único usuario.

**Tipo de relación:** uno a muchos.

---

### Relación Bank - Account

- Un banco puede emitir muchas cuentas.
- Cada cuenta pertenece a un único banco.

**Tipo de relación:** uno a muchos.

---

### Relación Account - Transaction

- Una cuenta puede participar en muchas transacciones.
- Cada transacción tiene una cuenta origen y una cuenta destino.

**Tipo de relación:** muchos a muchos resuelta mediante referencias de origen y destino dentro de la transacción.

---

### Relación Transaction - RiskAlert

- Una transacción puede generar cero o una o varias alertas, según el modelo de análisis.
- Una alerta puede asociarse a una transacción específica.

**Tipo de relación:** uno a muchos.

---

### Relación Bank - BankRegistry

Desde la perspectiva analítica, el banco puede estar representado en una tabla de registro o catálogo de entidades observadas.

---

## Lógica del número de cuenta

El número de cuenta debe tener un formato que permita identificar fácilmente a qué banco pertenece la cuenta.

### Formato sugerido

`BANKCODE-XXXXXX`

Ejemplos:

- `BKA-000001`
- `BKB-000245`

### Razones para este diseño

- facilita distinguir transferencias internas de interbancarias;
- ayuda al enrutamiento de operaciones;
- mejora la trazabilidad;
- permite al módulo de analytics identificar rápidamente la entidad emisora o receptora.

---

## Lógica de la transacción interbancaria

En una transacción interbancaria deben conservarse al menos los siguientes elementos:

- cuenta origen;
- banco origen;
- cuenta destino;
- banco destino;
- monto;
- estado;
- marca temporal.

Esto permitirá que tanto el banco emisor como el receptor registren su participación en la operación y que analytics reconstruya el trayecto del dinero dentro de la red.

---

## Atributos clave para análisis de riesgo

Existen atributos del modelo que son especialmente importantes para el componente analítico:

### `amount`

Permite detectar montos inusuales, fragmentación o valores cercanos a umbrales sospechosos.

### `created_at`

Permite analizar frecuencia, velocidad y secuencia temporal de operaciones.

### `source_account_number` y `destination_account_number`

Permiten trazar relaciones entre cuentas y construir grafos de movimiento.

### `source_bank_code` y `destination_bank_code`

Permiten analizar relaciones entre entidades y flujo interbancario.

### `channel`

Permite observar diferencias de comportamiento según el medio usado.

### `location`

Permite detectar inconsistencias o patrones geográficos simulados.

### `status`

Permite distinguir operaciones completadas, fallidas, pendientes o marcadas.

---

## Consideraciones sobre persistencia distribuida

Dado que cada banco tendrá su propia base de datos, el modelo no se implementará como una única base central compartida entre todas las entidades bancarias.

En su lugar:

- cada banco almacenará sus propios usuarios, cuentas y transacciones;
- analytics podrá mantener su propia base para alertas, configuraciones o resultados;
- la relación entre datos de distintos bancos se reconstruirá a través de integraciones por API y no mediante joins directos entre bases.

Esta decisión es coherente con la arquitectura distribuida definida para el proyecto.

---

## Posible organización por contexto

Para mantener claridad en la implementación, el modelo puede agruparse por contexto:

### Contexto bancario

- User
- Account
- Transaction

### Contexto institucional

- Bank
- BankRegistry

### Contexto analítico

- RiskAlert
- AnalysisTrace / FollowUpRecord

Esta organización conceptual facilitará posteriormente la separación del código en módulos.

---

## Modelo conceptual resumido

De forma resumida, FlowLens se apoya en la siguiente lógica de datos:

- un banco posee cuentas;
- un usuario posee cuentas;
- una cuenta participa en transacciones;
- una transacción conecta dos cuentas;
- las transacciones pueden atravesar bancos distintos;
- analytics observa transacciones;
- analytics genera alertas;
- un analista puede profundizar en una cuenta y reconstruir su comportamiento dentro de la red.

---

## Resultado esperado del modelo de datos

El modelo de datos de FlowLens debe permitir implementar una estructura coherente, trazable y preparada para análisis, asegurando que:

- los bancos mantengan independencia operativa;
- las cuentas puedan identificarse de forma clara;
- las transacciones contengan suficiente contexto;
- las alertas representen hallazgos útiles;
- el seguimiento profundo tenga base estructural;
- el sistema pueda evolucionar sin rediseños drásticos.

En consecuencia, este modelo no solo representa la información del sistema, sino que constituye una de las bases esenciales para su consistencia técnica, su implementación y su defensa conceptual.
