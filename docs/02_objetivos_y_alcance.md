# 02. Objetivos y Alcance

## Objetivo general

Diseñar e implementar **FlowLens**, una plataforma distribuida de simulación bancaria y análisis transaccional, compuesta por múltiples bancos independientes con bases de datos separadas, capacidad de comunicación interbancaria y un módulo externo de analytics que permita monitorear movimientos, detectar patrones sospechosos y dar seguimiento profundo a cuentas dentro de un entorno demostrativo, técnico y controlado.

---

## Objetivos específicos

1. Desarrollar al menos dos bancos simulados independientes, cada uno con su propio backend, lógica de negocio y base de datos.
2. Permitir el registro de usuarios y la creación de cuentas bancarias dentro de cada banco participante.
3. Implementar transferencias internas dentro de un mismo banco y transferencias interbancarias entre bancos distintos.
4. Diseñar un mecanismo de comunicación entre bancos que permita enrutar y procesar operaciones entre entidades diferentes.
5. Construir una aplicación externa de analytics capaz de conectarse a varios bancos y consultar información transaccional relevante.
6. Implementar reglas de análisis para identificar patrones sospechosos, anomalías y comportamientos de riesgo.
7. Permitir el seguimiento profundo de una cuenta seleccionada por un analista autorizado, mostrando historial, relaciones, alertas y comportamiento transaccional.
8. Visualizar la red de transacciones y relaciones entre cuentas y bancos de forma comprensible.
9. Desplegar la solución en una VPS para pruebas controladas por usuarios y evaluadores.
10. Documentar de forma clara la arquitectura, el alcance, los requisitos, las reglas de negocio y las consideraciones de cumplimiento del proyecto.

---

## Alcance del sistema

FlowLens abarcará, en esta etapa, la simulación de un ecosistema financiero distribuido compuesto por bancos independientes que pueden operar entre sí y por una aplicación externa especializada en el monitoreo y análisis de actividad transaccional.

El alcance del sistema comprende:

- operación de bancos simulados con identidad propia;
- gestión de usuarios dentro de cada banco;
- creación y administración de cuentas bancarias simuladas;
- consulta de saldo e historial de transacciones;
- ejecución de transferencias internas;
- ejecución de transferencias interbancarias;
- intercambio de información entre bancos mediante APIs;
- monitoreo centralizado desde una aplicación de analytics;
- análisis de patrones sospechosos;
- generación de alertas de riesgo;
- seguimiento profundo de cuentas seleccionadas;
- visualización de redes transaccionales;
- despliegue funcional del sistema en un entorno VPS.

---

## Funcionalidades incluidas en esta etapa

Durante esta fase del proyecto se desarrollarán las siguientes funcionalidades principales:

### Módulo bancario

- registro de usuarios;
- autenticación de usuarios;
- creación de cuentas bancarias;
- consulta de saldo;
- consulta de historial de movimientos;
- transferencias dentro del mismo banco;
- validación de saldo disponible;
- registro persistente de transacciones.

### Módulo interbancario

- identificación del banco destino a partir de la cuenta;
- envío de solicitudes de transferencia entre bancos;
- recepción y acreditación de transferencias provenientes de otras entidades;
- registro local de operaciones emitidas y recibidas;
- manejo de estados de transacción.

### Módulo de analytics

- registro de bancos disponibles para monitoreo;
- consulta de movimientos desde múltiples bancos;
- análisis de transacciones mediante reglas de riesgo;
- generación de alertas;
- clasificación de alertas por nivel de riesgo;
- seguimiento profundo de cuentas;
- visualización de relaciones transaccionales;
- resumen de patrones sospechosos detectados.

### Módulo de presentación

- interfaz web para usuarios bancarios;
- interfaz de consulta para analista;
- panel con alertas y red de transacciones;
- acceso desde navegador para pruebas controladas.

---

## Funcionalidades fuera de alcance

En esta etapa del proyecto no se contempla implementar:

- integración con entidades financieras reales;
- uso de dinero real;
- procesamiento de pagos reales;
- conexión con sistemas regulatorios reales;
- uso de datos financieros reales de clientes;
- monitoreo de usuarios reales en producción;
- cumplimiento regulatorio operativo completo;
- alta disponibilidad empresarial;
- microservicios complejos con mensajería avanzada;
- machine learning entrenado con datasets reales;
- infraestructura bancaria productiva a gran escala.

Tampoco forma parte del alcance de esta etapa sustituir la operación real de una entidad financiera, ni ofrecer servicios financieros reales al público general.

---

## Definición del MVP

El **Producto Mínimo Viable (MVP)** de FlowLens estará compuesto por los siguientes elementos:

### 1. Dos bancos simulados independientes

Cada uno deberá contar con:

- backend propio;
- base de datos propia;
- usuarios;
- cuentas;
- transferencias internas;
- historial de transacciones.

### 2. Comunicación interbancaria funcional

El sistema deberá permitir:

- transferir dinero de una cuenta en un banco a una cuenta en otro banco;
- registrar la operación en ambas entidades;
- manejar correctamente estados básicos de éxito o error.

### 3. Aplicación externa de analytics

Deberá permitir:

- registrar o conocer los bancos participantes;
- consultar transacciones;
- aplicar reglas de análisis;
- generar alertas;
- mostrar un resumen de riesgo.

### 4. Seguimiento profundo de cuentas

El analista deberá poder:

- seleccionar una cuenta;
- revisar su historial;
- observar cuentas relacionadas;
- identificar patrones relevantes;
- consultar alertas asociadas;
- visualizar su comportamiento dentro de la red.

### 5. Visualización básica de red transaccional

El sistema deberá representar, al menos de forma inicial:

- nodos de cuentas;
- conexiones por transacción;
- relaciones entre bancos;
- indicios visuales de riesgo o actividad sospechosa.

### 6. Despliegue funcional en VPS

El proyecto deberá poder ejecutarse en un entorno accesible para pruebas controladas por terceros.

---

## Criterios de éxito del proyecto

Se considerará que el proyecto cumple sus objetivos si al finalizar el desarrollo logra demostrar, de forma funcional y comprensible, que:

1. Existen múltiples bancos simulados operando de manera independiente.
2. Cada banco gestiona su propia base de datos y sus propias transacciones.
3. Las transferencias internas e interbancarias funcionan correctamente.
4. La aplicación de analytics puede conectarse a los bancos y consultar información relevante.
5. El sistema detecta y muestra alertas de riesgo a partir de reglas definidas.
6. El seguimiento profundo de cuentas permite observar con claridad el comportamiento transaccional de una cuenta seleccionada.
7. La visualización de la red ayuda a entender relaciones y patrones dentro del ecosistema.
8. La plataforma puede ser desplegada y probada desde una VPS.
9. La documentación describe de manera clara la arquitectura, el alcance y la lógica general del sistema.
10. La solución final resulta técnicamente coherente, demostrable y apta para presentación formal o hackathon.

---

## Delimitación del entorno de prueba

La ejecución pública de FlowLens se realizará como una demostración controlada, utilizando únicamente datos sintéticos o anonimizados no reidentificables. El objetivo del despliegue será permitir la evaluación funcional del sistema, sin exponer información financiera real ni operar como una entidad bancaria verdadera.

Por esta razón, el alcance del proyecto debe entenderse siempre dentro de un entorno de simulación técnica, académica y demostrativa.
