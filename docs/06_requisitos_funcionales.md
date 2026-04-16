# 06. Requisitos Funcionales

## Introducción

Los requisitos funcionales de FlowLens describen las capacidades y comportamientos que el sistema debe ofrecer para cumplir su objetivo como plataforma distribuida de simulación bancaria y análisis transaccional.

Estos requisitos se organizan en función de los principales módulos del proyecto:

- módulo bancario;
- módulo interbancario;
- módulo de analytics;
- módulo de seguimiento profundo;
- módulo de autenticación y acceso;
- módulo de visualización.

Cada requisito funcional define una necesidad concreta del sistema y servirá como base para el diseño, implementación, pruebas y validación del proyecto.

---

## Requisitos funcionales del módulo bancario

### RF-01. Registro de usuarios

El sistema debe permitir registrar usuarios dentro de cada banco simulado.

### RF-02. Inicio de sesión de usuarios

El sistema debe permitir que un usuario registrado inicie sesión con sus credenciales.

### RF-03. Gestión de cuentas bancarias

El sistema debe permitir crear cuentas bancarias asociadas a un usuario dentro de un banco específico.

### RF-04. Consulta de saldo

El sistema debe permitir al usuario consultar el saldo actual de sus cuentas.

### RF-05. Consulta de historial de transacciones

El sistema debe permitir al usuario consultar el historial de movimientos de sus cuentas.

### RF-06. Transferencias internas

El sistema debe permitir realizar transferencias entre cuentas pertenecientes al mismo banco.

### RF-07. Validación de saldo suficiente

El sistema debe validar que la cuenta origen tenga fondos suficientes antes de ejecutar una transferencia.

### RF-08. Registro de transacciones

El sistema debe registrar toda transacción realizada dentro del banco, independientemente de si fue interna o interbancaria.

### RF-09. Identificación de cuenta por banco

El sistema debe identificar a qué banco pertenece una cuenta a partir de su número de cuenta o código asociado.

---

## Requisitos funcionales del módulo interbancario

### RF-10. Envío de transferencias interbancarias

El sistema debe permitir enviar transferencias desde una cuenta de un banco hacia una cuenta perteneciente a otro banco.

### RF-11. Recepción de transferencias interbancarias

El sistema debe permitir que un banco receptor procese y registre transferencias provenientes de otro banco.

### RF-12. Registro dual de operación interbancaria

El sistema debe registrar la participación de la operación tanto en el banco emisor como en el banco receptor.

### RF-13. Validación de banco destino

El sistema debe validar la existencia o identificación del banco destino antes de procesar una transferencia interbancaria.

### RF-14. Manejo de estado de transacción

El sistema debe gestionar estados de transacción, como pendiente, completada, fallida o rechazada.

### RF-15. Exposición de endpoints de integración

Cada banco debe exponer endpoints que permitan interoperabilidad con otros bancos y con el sistema de analytics.

---

## Requisitos funcionales del módulo de analytics

### RF-16. Registro de bancos a monitorear

El sistema de analytics debe permitir registrar o identificar los bancos participantes del ecosistema.

### RF-17. Consulta de transacciones desde bancos externos

El sistema de analytics debe poder consultar transacciones desde los bancos registrados mediante APIs.

### RF-18. Consolidación de información transaccional

El sistema de analytics debe consolidar datos suficientes para realizar análisis sobre actividad financiera simulada.

### RF-19. Evaluación de riesgo transaccional

El sistema de analytics debe evaluar transacciones usando reglas predefinidas de riesgo.

### RF-20. Generación de alertas

El sistema de analytics debe generar alertas cuando detecte patrones sospechosos o transacciones con riesgo relevante.

### RF-21. Clasificación de alertas

El sistema debe clasificar las alertas por nivel de riesgo, por ejemplo bajo, medio o alto.

### RF-22. Consulta de alertas

El sistema debe permitir consultar las alertas generadas por el módulo analítico.

### RF-23. Resumen de riesgo

El sistema debe permitir visualizar un resumen de alertas y patrones detectados dentro del ecosistema.

---

## Requisitos funcionales del módulo de seguimiento profundo

### RF-24. Selección de cuenta para seguimiento

El sistema debe permitir que un analista autorizado seleccione una cuenta para realizar seguimiento profundo.

### RF-25. Consulta de historial detallado de una cuenta

El sistema debe mostrar el historial completo o relevante de transacciones de una cuenta seleccionada.

### RF-26. Identificación de contrapartes frecuentes

El sistema debe permitir observar las cuentas o entidades con las que una cuenta interactúa con mayor frecuencia.

### RF-27. Visualización de relaciones directas e indirectas

El sistema debe permitir visualizar relaciones transaccionales directas e indirectas asociadas a una cuenta.

### RF-28. Consulta de alertas asociadas a una cuenta

El sistema debe mostrar alertas relacionadas con la cuenta seleccionada.

### RF-29. Resumen de comportamiento transaccional

El sistema debe presentar métricas o indicadores relevantes sobre la actividad de una cuenta, como frecuencia, montos promedio o concentración de transferencias.

### RF-30. Seguimiento analítico contextual

El sistema debe permitir interpretar una cuenta dentro de su contexto de red, y no solo como un elemento aislado.

---

## Requisitos funcionales del módulo de visualización

### RF-31. Visualización de red transaccional

El sistema debe representar gráficamente relaciones entre cuentas y transacciones.

### RF-32. Representación de nodos y conexiones

La visualización debe mostrar cuentas como nodos y transacciones como conexiones o relaciones.

### RF-33. Identificación visual de riesgo

La visualización debe permitir resaltar cuentas, transacciones o relaciones con indicadores de riesgo.

### RF-34. Consulta de información desde interfaz web

El sistema debe permitir consultar información bancaria y analítica desde una interfaz accesible por navegador.

---

## Requisitos funcionales del módulo de autenticación y acceso

### RF-35. Autenticación de usuarios bancarios

El sistema debe autenticar a los usuarios bancarios antes de permitir acceso a cuentas y operaciones.

### RF-36. Autenticación de analistas

El sistema debe autenticar a los usuarios autorizados del módulo de analytics.

### RF-37. Restricción de acceso por rol

El sistema debe restringir funcionalidades según el tipo de usuario o rol definido.

### RF-38. Protección de vistas sensibles

El sistema debe proteger vistas sensibles, como seguimiento profundo, alertas y análisis detallado.

---

## Requisitos funcionales del entorno de despliegue y prueba

### RF-39. Acceso desde entorno VPS

El sistema debe poder ejecutarse en una VPS y ser accesible para pruebas controladas mediante navegador o APIs.

### RF-40. Disponibilidad de entorno demostrativo

El sistema debe ofrecer un entorno demostrativo funcional para que terceros puedan interactuar con la plataforma sin necesidad de configuración local compleja.

---

## Observaciones generales sobre los requisitos funcionales

Los requisitos funcionales definidos en este documento corresponden al comportamiento esperado del sistema dentro de su alcance actual como MVP distribuido y demostrativo.

Aunque algunos módulos podrán evolucionar en versiones futuras, esta base funcional ya permite construir una plataforma sólida capaz de:

- operar bancos simulados;
- comunicar entidades distintas;
- registrar y consultar movimientos;
- analizar transacciones;
- generar alertas;
- dar seguimiento profundo a cuentas;
- visualizar redes de relaciones.

Por lo tanto, estos requisitos constituyen una referencia central para orientar el desarrollo técnico de FlowLens.
