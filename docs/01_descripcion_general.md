# 01. Descripción General del Proyecto

## Nombre del proyecto

**FlowLens**  
_Plataforma distribuida de simulación bancaria y análisis de transacciones sospechosas_

---

## Descripción general

FlowLens es una plataforma tecnológica compuesta por múltiples bancos simulados, cada uno con su propia base de datos y backend independiente, capaces de ejecutar operaciones bancarias internas e interbancarias dentro de un entorno controlado. Sobre este ecosistema se incorpora una aplicación externa de análisis transaccional, diseñada para conectarse a los bancos participantes, observar sus movimientos financieros y detectar patrones sospechosos mediante reglas de riesgo, trazabilidad de cuentas y visualización de redes de transacciones.

El sistema busca reproducir, de manera demostrativa y académica, un escenario cercano al funcionamiento de un ecosistema financiero moderno, donde diferentes entidades bancarias operan de forma separada, pero pueden intercambiar fondos y ser observadas por un módulo especializado de analytics. Este módulo no forma parte del core bancario de cada entidad, sino que funciona como una aplicación independiente con capacidad de integrarse con múltiples bancos, recolectar información transaccional y generar alertas de riesgo.

El proyecto se plantea como una simulación funcional y no como una plataforma financiera real. Su propósito principal es demostrar cómo una arquitectura distribuida puede combinar operaciones bancarias, comunicación entre entidades y análisis de comportamiento transaccional para identificar actividades atípicas o sospechosas.

---

## Propósito del proyecto

El propósito de FlowLens es diseñar e implementar una plataforma distribuida que permita simular operaciones bancarias reales y, al mismo tiempo, demostrar el valor de un sistema de análisis externo capaz de monitorear cuentas, transferencias y relaciones entre entidades para detectar patrones asociados a fraude, fragmentación de montos, cadenas rápidas de movimiento de dinero, concentración de transferencias y otras señales de riesgo.

El proyecto busca unir tres dimensiones fundamentales:

1. **Operación bancaria simulada**, donde los usuarios puedan registrarse, crear cuentas y transferir fondos.
2. **Comunicación interbancaria**, donde bancos independientes puedan intercambiar transacciones mediante APIs.
3. **Análisis transaccional profundo**, donde una aplicación especializada pueda estudiar movimientos, generar alertas y visualizar relaciones entre cuentas y bancos.

---

## Contexto del problema

En los ecosistemas financieros reales, el análisis de transacciones no se limita a revisar una operación aislada. Muchas veces es necesario observar el contexto completo: quién envía, quién recibe, con qué frecuencia se mueve el dinero, qué tan rápido cambia de manos, si existen patrones repetitivos y cómo se conectan distintas cuentas dentro de una red.

Los sistemas bancarios tradicionales suelen centrarse en la ejecución de operaciones, mientras que los procesos de análisis, monitoreo y detección de comportamientos sospechosos se apoyan en módulos especializados o equipos analíticos con acceso a información transaccional consolidada. Esta separación entre operación y análisis es importante porque permite que los bancos sigan funcionando de forma independiente, mientras una capa adicional agrega inteligencia y observabilidad.

A partir de esta necesidad surge FlowLens como una plataforma que simula ese escenario: varios bancos autónomos operando entre sí, un mecanismo de comunicación interbancaria y una aplicación externa que permite estudiar el recorrido del dinero dentro de la red.

---

## Enfoque de la solución

La solución propuesta se basa en una arquitectura distribuida compuesta por cuatro grandes componentes:

### 1. Bancos simulados independientes

Cada banco contará con su propio backend, su propia lógica de negocio y su propia base de datos. Esto permitirá representar entidades autónomas y desacopladas, tal como ocurre en un entorno financiero real.

### 2. Comunicación interbancaria

Los bancos podrán intercambiar transacciones entre sí mediante APIs, permitiendo transferencias entre cuentas que pertenecen a entidades distintas.

### 3. Aplicación externa de analytics

Se desarrollará una aplicación independiente encargada de conectarse a los bancos, consultar transacciones, analizar patrones de comportamiento y generar alertas de riesgo.

### 4. Seguimiento profundo de cuentas

El sistema permitirá que un analista autorizado seleccione una cuenta específica y acceda a una vista de seguimiento profundo, en la que podrá observar su historial, sus contrapartes frecuentes, la velocidad de movimiento del dinero, cadenas de transferencia, montos relevantes, alertas generadas y conexiones dentro de la red.

---

## Naturaleza del proyecto

Este proyecto tiene una naturaleza:

- **demostrativa**, porque modela un ecosistema bancario sin procesar dinero real;
- **académica y técnica**, porque busca evidenciar diseño de arquitectura, integración por APIs y análisis de datos;
- **experimental**, porque permite probar reglas de riesgo y seguimiento transaccional en un entorno controlado;
- **escalable conceptualmente**, porque la arquitectura puede extenderse a más bancos, más reglas de análisis y mayores niveles de complejidad.

---

## Alcance conceptual de la plataforma

La plataforma cubrirá, en esta etapa, los siguientes aspectos:

- registro de usuarios en bancos simulados;
- creación de cuentas bancarias;
- transferencias internas dentro de un mismo banco;
- transferencias interbancarias entre bancos diferentes;
- consulta de saldos e historial de transacciones;
- monitoreo centralizado desde una aplicación externa;
- generación de alertas de riesgo;
- análisis de patrones sospechosos;
- visualización de redes transaccionales;
- seguimiento profundo de cuentas seleccionadas por un analista.

No forma parte del alcance de esta etapa:

- operar con dinero real;
- integrarse con bancos reales;
- exponer información financiera real de terceros;
- reemplazar obligaciones regulatorias reales;
- ofrecer servicios financieros productivos al público.

---

## Justificación del proyecto

La propuesta tiene valor porque no se limita a construir un banco simulado simple, sino que presenta un ecosistema completo en el que varias entidades pueden operar de manera independiente mientras una capa externa de análisis observa el comportamiento global de la red.

Esto permite demostrar conocimientos y capacidades en áreas clave como:

- arquitectura distribuida;
- diseño de APIs;
- modelado de datos;
- integración entre servicios;
- lógica de negocio bancaria;
- análisis transaccional;
- trazabilidad de operaciones;
- visualización de relaciones entre cuentas y entidades;
- diseño de sistemas orientados a monitoreo y prevención.

Además, el proyecto incorpora una visión más cercana a escenarios reales al separar claramente la operación bancaria del análisis transaccional, lo cual fortalece tanto su diseño técnico como su valor de presentación.

---

## Usuarios o actores principales

Dentro del sistema se identifican los siguientes actores principales:

### Usuario bancario

Persona que interactúa con un banco simulado para registrarse, consultar su cuenta, revisar su saldo y realizar transferencias.

### Banco simulado

Entidad que administra usuarios, cuentas y movimientos dentro de su propio entorno y base de datos.

### Switch o capa interbancaria

Componente encargado de facilitar o enrutar la comunicación entre bancos durante transferencias entre entidades distintas.

### Analista

Usuario autorizado que accede a la aplicación de analytics para monitorear transacciones, revisar alertas, visualizar redes y dar seguimiento profundo a cuentas específicas.

### Sistema de analytics

Aplicación independiente que recopila y analiza información transaccional proveniente de múltiples bancos.

---

## Visión general de funcionamiento

De forma resumida, el funcionamiento esperado de la plataforma será el siguiente:

1. Un usuario se registra en un banco simulado.
2. El banco le crea una cuenta bancaria dentro de su propia base de datos.
3. El usuario puede realizar transferencias a cuentas del mismo banco o de otros bancos.
4. Cuando la transferencia es interna, se procesa dentro del mismo backend bancario.
5. Cuando la transferencia es interbancaria, se envía a través de la capa de comunicación correspondiente hacia el banco destino.
6. Cada banco registra sus operaciones localmente.
7. La aplicación de analytics consulta transacciones desde los bancos registrados.
8. El módulo analítico evalúa movimientos, calcula niveles de riesgo, detecta patrones y genera alertas.
9. Un analista puede seleccionar una cuenta y revisar un seguimiento profundo de su actividad y relaciones dentro de la red.

---

## Valor diferencial del sistema

El principal valor diferencial de FlowLens radica en que combina, dentro de una sola propuesta, los siguientes elementos:

- múltiples bancos independientes con bases de datos separadas;
- transferencias internas e interbancarias;
- una aplicación externa de analytics desacoplada;
- monitoreo centralizado de transacciones;
- análisis de patrones sospechosos;
- trazabilidad profunda de cuentas;
- visualización de la red de movimiento del dinero.

Esta combinación convierte al proyecto en una plataforma integral de simulación y análisis, más robusta y realista que un simple prototipo bancario aislado.

---

## Consideraciones de cumplimiento y legalidad del entorno demo

La plataforma será implementada como un entorno demostrativo y académico, utilizando datos sintéticos o anonimizados no reidentificables, con el fin de evitar la exposición pública de información financiera real de terceros.

El módulo de seguimiento profundo y las vistas analíticas sensibles estarán concebidos como herramientas de acceso restringido para usuarios autorizados dentro del entorno de prueba. En consecuencia, el proyecto no pretende vulnerar principios de confidencialidad bancaria ni sustituir funciones regulatorias reales, sino simular técnicamente cómo operaría una solución de monitoreo transaccional en un contexto controlado.

---

## Resultado esperado

Al finalizar el desarrollo, se espera contar con una plataforma funcional desplegable en una VPS, accesible para pruebas controladas, capaz de demostrar:

- operación de bancos simulados independientes;
- intercambio de transacciones entre bancos;
- monitoreo externo de actividad financiera;
- generación de alertas de riesgo;
- seguimiento analítico profundo de cuentas;
- visualización comprensible de patrones y relaciones transaccionales.

Con ello, FlowLens se consolidará como un prototipo técnico sólido, coherente y bien fundamentado, apto para demostración pública controlada y presentación formal.
