# 03. Arquitectura General del Sistema

## Visión general de la arquitectura

FlowLens se concibe como una plataforma distribuida compuesta por múltiples sistemas independientes que colaboran entre sí para simular un ecosistema bancario y, al mismo tiempo, permitir el análisis de actividad transaccional desde una aplicación externa especializada.

La arquitectura se diseñó bajo un enfoque desacoplado, donde cada banco mantiene su propia lógica de negocio y su propia base de datos, mientras que el análisis transaccional se realiza desde un sistema independiente con capacidad de conectarse a distintas entidades. Esta separación permite representar de forma más realista cómo operan los bancos y cómo una capa externa de monitoreo puede observar patrones dentro de una red financiera.

La solución estará compuesta, en esta etapa, por cuatro bloques principales:

1. Bancos simulados independientes.
2. Mecanismo de comunicación interbancaria.
3. Aplicación externa de analytics.
4. Interfaz de usuario para operación y visualización.

---

## Componentes principales de la arquitectura

### 1. Bancos simulados independientes

Cada banco será una aplicación autónoma con las siguientes características:

- backend propio;
- base de datos propia;
- usuarios propios;
- cuentas propias;
- historial local de transacciones;
- lógica de transferencias internas;
- capacidad de recibir o enviar transferencias interbancarias.

Cada entidad bancaria funcionará de manera independiente del resto. Esto significa que podrá operar y registrar su actividad aun cuando otros bancos o incluso el módulo de analytics no estén disponibles temporalmente.

La independencia de cada banco es una decisión arquitectónica fundamental, ya que permite simular un entorno donde las entidades financieras no comparten directamente su base de datos ni dependen de una sola aplicación central para operar.

---

### 2. Comunicación interbancaria

La arquitectura contempla un mecanismo para permitir la transferencia de fondos entre bancos diferentes.

Cuando una cuenta de un banco necesite enviar dinero a una cuenta perteneciente a otra entidad, el sistema deberá:

- identificar el banco destino;
- validar la operación en el banco origen;
- enviar una solicitud de acreditación al banco receptor;
- registrar el movimiento en ambas entidades;
- manejar estados de éxito, error o rechazo.

Esta comunicación se realizará mediante APIs REST, lo que permite un diseño claro, entendible y adecuado para el alcance demostrativo del proyecto.

La comunicación interbancaria representa el puente operativo entre bancos independientes y es uno de los elementos centrales del sistema, ya que permite construir una verdadera red de movimientos entre entidades.

---

### 3. Aplicación externa de analytics

El módulo de analytics será una aplicación independiente del core bancario. Su función no será ejecutar transacciones ni administrar cuentas, sino conectarse a los bancos, recopilar información relevante y analizarla desde una perspectiva de monitoreo y trazabilidad.

Entre sus responsabilidades principales estarán:

- consultar transacciones de los bancos registrados;
- consolidar información para análisis;
- aplicar reglas de detección de riesgo;
- generar alertas;
- clasificar niveles de riesgo;
- permitir seguimiento profundo de cuentas;
- visualizar relaciones y redes transaccionales.

Esta decisión de separar analytics del sistema bancario principal fortalece el diseño del proyecto, porque distingue con claridad dos responsabilidades distintas:

- operar transacciones;
- analizar transacciones.

---

### 4. Interfaz de usuario

El sistema contará con una capa de presentación orientada a dos tipos principales de interacción:

#### Interfaz bancaria

Permitirá a los usuarios:

- registrarse;
- iniciar sesión;
- consultar cuentas;
- ver saldo;
- revisar historial;
- realizar transferencias.

#### Interfaz analítica

Permitirá a usuarios autorizados:

- consultar alertas;
- revisar transacciones sospechosas;
- analizar cuentas;
- visualizar relaciones entre entidades;
- dar seguimiento profundo a cuentas específicas.

Esta separación mejora la claridad del sistema y ayuda a diferenciar los perfiles de uso y los permisos asociados a cada rol.

---

## Estructura distribuida del sistema

La arquitectura general de FlowLens puede representarse conceptualmente así:

```text
Cliente / Navegador
        |
        v
Frontend / Interfaces
   |           |
   |           +-----------------------------+
   |                                         |
   v                                         v
Banco A API                              Analytics API
   |                                         |
   v                                         |
Banco A DB                                  |
                                             |
   +-------------------+---------------------+
                       |
                       v
                  Comunicación
                  interbancaria
                       |
           +-----------+-----------+
           |                       |
           v                       v
      Banco B API             Banco C API
           |                       |
           v                       v
      Banco B DB              Banco C DB
```

Esta representación muestra que cada banco conserva su autonomía, mientras el sistema de analytics observa el ecosistema desde fuera y la comunicación interbancaria permite intercambios entre entidades.

---

## Principios arquitectónicos del sistema

La arquitectura de FlowLens se apoya en los siguientes principios:

### Separación de responsabilidades

Cada módulo cumple una función clara:

- los bancos operan;
- la capa interbancaria comunica;
- analytics analiza;
- la interfaz presenta.

### Desacoplamiento

Cada banco puede existir como una unidad separada con su propia persistencia y lógica, sin depender internamente de la base de datos de otros bancos.

### Escalabilidad conceptual

Aunque el MVP iniciará con dos bancos, la arquitectura está preparada para incorporar nuevas entidades con cambios razonables en el sistema.

### Trazabilidad

Toda transacción debe quedar registrada de forma que pueda ser consultada, rastreada y analizada posteriormente.

### Observabilidad

El sistema debe facilitar la revisión del comportamiento financiero simulado mediante alertas, consultas y visualizaciones de red.

### Mantenibilidad

La estructura modular busca facilitar el entendimiento, desarrollo y evolución del proyecto.

---

## Relación entre los módulos

### Relación banco-usuario

Cada usuario pertenece a un banco específico y opera sus cuentas dentro de esa entidad.

### Relación banco-cuenta

Cada cuenta es emitida y administrada por un único banco.

### Relación banco-transacción

Cada banco registra localmente las transacciones en las que participa, ya sea como entidad emisora, receptora o ambas en el caso de operaciones internas.

### Relación banco-analytics

El módulo de analytics consulta información expuesta por los bancos para construir análisis, alertas y redes de relaciones.

### Relación entre bancos

Los bancos se comunican mediante APIs para completar transferencias interbancarias.

---

## Flujo general de operación

El flujo general esperado del sistema será el siguiente:

1. Un usuario accede al frontend de un banco.
2. El usuario se registra o inicia sesión.
3. El banco crea o consulta sus cuentas dentro de su propia base de datos.
4. El usuario realiza una transferencia.
5. Si la cuenta destino pertenece al mismo banco, la operación se procesa internamente.
6. Si la cuenta destino pertenece a otro banco, se activa la comunicación interbancaria.
7. Ambos bancos registran la transacción según su participación en la operación.
8. El sistema de analytics consulta las transacciones disponibles en los bancos registrados.
9. Analytics analiza patrones, calcula riesgo y genera alertas.
10. Un analista autorizado revisa resultados, alertas y seguimiento profundo desde la interfaz analítica.

---

## Arquitectura lógica por capas

Cada banco y la aplicación de analytics pueden organizarse internamente mediante una arquitectura por capas:

### Capa de presentación

Responsable de exponer la API o la interfaz web.

### Capa de aplicación

Responsable de coordinar casos de uso y flujo de negocio.

### Capa de dominio o lógica de negocio

Responsable de implementar reglas operativas, validaciones y comportamiento del sistema.

### Capa de persistencia

Responsable de almacenar y recuperar información desde la base de datos.

Este esquema ayuda a mantener una estructura ordenada y facilita la comprensión del código.

---

## Razón de usar bases de datos separadas por banco

La decisión de que cada banco tenga su propia base de datos responde a varias razones técnicas y conceptuales:

1. Refuerza la independencia de cada entidad bancaria.
2. Simula de forma más realista un entorno distribuido.
3. Evita concentrar toda la operación en una sola base central.
4. Permite que la aplicación de analytics sea verdaderamente externa.
5. Facilita demostrar integración entre sistemas autónomos.
6. Mejora la defensa arquitectónica del proyecto durante su presentación.

Esta es una de las decisiones más importantes del diseño, ya que define tanto la identidad del sistema como su diferencia frente a un prototipo bancario convencional.

---

## Razón de separar analytics del sistema bancario

La aplicación de analytics se mantendrá separada porque su propósito es distinto al de un banco.

Un banco tiene como prioridad:

- gestionar usuarios;
- manejar cuentas;
- ejecutar transacciones;
- registrar movimientos.

Analytics, en cambio, tiene como prioridad:

- observar comportamiento;
- detectar patrones;
- generar riesgo;
- trazar relaciones;
- apoyar seguimiento analítico.

Separar ambos mundos permite una mejor organización conceptual y una presentación mucho más sólida del proyecto.

---

## Seguimiento profundo como capacidad especializada

Dentro de la arquitectura de analytics se incorpora un componente especializado de seguimiento profundo de cuentas. Este componente permitirá a un analista autorizado seleccionar una cuenta concreta y estudiar su actividad desde una perspectiva detallada.

Dicho seguimiento incluirá, según el alcance del MVP:

- historial completo de movimientos;
- contrapartes más frecuentes;
- montos promedio y montos relevantes;
- frecuencia de transferencias;
- relaciones directas e indirectas;
- alertas asociadas;
- indicios de concentración o comportamiento anómalo;
- visualización dentro de la red.

Este componente no forma parte del flujo normal de un usuario bancario, sino de la capa analítica del sistema.

---

## Consideraciones de seguridad y acceso

Aunque FlowLens será una plataforma demostrativa, la arquitectura debe contemplar controles básicos para separar accesos y proteger módulos sensibles.

En especial:

- los usuarios bancarios solo podrán acceder a sus propias cuentas y operaciones;
- los analistas autorizados accederán al módulo de analytics;
- las funciones de seguimiento profundo no deberán exponerse como consultas públicas sin control;
- la comunicación entre módulos debe ser clara y controlada.

Esto ayuda a mantener coherencia con el propósito del sistema y con las consideraciones de confidencialidad planteadas para el entorno demo.

---

## Resultado arquitectónico esperado

La arquitectura de FlowLens debe permitir construir una solución coherente, modular y fácilmente explicable, donde:

- varios bancos operan de forma independiente;
- existe comunicación entre entidades;
- un sistema externo observa la actividad de la red;
- se generan alertas y análisis útiles;
- puede darse seguimiento profundo a cuentas seleccionadas;
- el proyecto puede desplegarse en una VPS y ser probado de forma controlada.

En consecuencia, la arquitectura no solo servirá como base técnica del desarrollo, sino también como una de las principales fortalezas conceptuales del proyecto.
