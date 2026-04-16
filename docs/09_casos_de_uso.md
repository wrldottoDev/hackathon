# 09. Casos de Uso

## Introducción

Los casos de uso de FlowLens describen las interacciones principales entre los actores del sistema y los distintos módulos que componen la plataforma. Su propósito es representar, de forma estructurada y comprensible, cómo los usuarios y componentes externos participan en los procesos clave del proyecto.

Dado que FlowLens está compuesto por bancos simulados, comunicación interbancaria y un módulo externo de analytics, los casos de uso se organizan en torno a los actores principales y a las acciones más relevantes dentro del ecosistema.

Estos casos de uso permiten visualizar el comportamiento esperado del sistema desde la perspectiva operativa y analítica, y sirven como puente entre los requisitos funcionales y la implementación técnica.

---

## Actores del sistema

### Usuario bancario

Persona que interactúa con uno de los bancos simulados para registrarse, iniciar sesión, consultar cuentas y realizar transferencias.

### Analista

Usuario autorizado que accede al módulo de analytics para revisar alertas, analizar transacciones y dar seguimiento profundo a cuentas.

### Banco emisor

Entidad bancaria desde la cual se origina una transferencia.

### Banco receptor

Entidad bancaria que recibe una transferencia interbancaria.

### Sistema de analytics

Aplicación externa encargada de consultar información transaccional, detectar patrones sospechosos y generar alertas.

### Módulo interbancario

Componente encargado de permitir la comunicación entre bancos para ejecutar transferencias entre entidades distintas.

---

## Lista general de casos de uso

- CU-01. Registrar usuario bancario
- CU-02. Iniciar sesión en un banco
- CU-03. Crear cuenta bancaria
- CU-04. Consultar saldo
- CU-05. Consultar historial de transacciones
- CU-06. Realizar transferencia interna
- CU-07. Realizar transferencia interbancaria
- CU-08. Recibir transferencia interbancaria
- CU-09. Registrar bancos en analytics
- CU-10. Consultar transacciones desde analytics
- CU-11. Generar alerta de riesgo
- CU-12. Consultar alertas analíticas
- CU-13. Visualizar red de transacciones
- CU-14. Iniciar seguimiento profundo de cuenta
- CU-15. Consultar resumen analítico de una cuenta

---

## CU-01. Registrar usuario bancario

### Actor principal

Usuario bancario

### Descripción

Permite que una persona cree su usuario dentro de uno de los bancos simulados del sistema.

### Precondiciones

- El banco debe estar disponible.
- El usuario no debe estar registrado previamente con el mismo correo.

### Flujo principal

1. El usuario accede al formulario de registro.
2. Ingresa sus datos personales básicos.
3. El sistema valida la información.
4. El sistema crea el usuario en la base de datos del banco.
5. El sistema confirma el registro exitoso.

### Postcondiciones

- El usuario queda registrado en el banco.
- El usuario puede proceder a iniciar sesión.

---

## CU-02. Iniciar sesión en un banco

### Actor principal

Usuario bancario

### Descripción

Permite a un usuario autenticarse dentro del banco al que pertenece.

### Precondiciones

- El usuario debe estar registrado.
- Debe ingresar credenciales válidas.

### Flujo principal

1. El usuario accede al formulario de inicio de sesión.
2. Ingresa correo y contraseña.
3. El sistema valida credenciales.
4. El sistema otorga acceso al entorno bancario correspondiente.

### Postcondiciones

- El usuario accede a sus funciones bancarias autorizadas.

---

## CU-03. Crear cuenta bancaria

### Actor principal

Usuario bancario o sistema

### Descripción

Permite asociar una cuenta bancaria a un usuario dentro de un banco específico.

### Precondiciones

- El usuario debe estar autenticado o validado por el sistema.
- El banco debe encontrarse operativo.

### Flujo principal

1. El usuario solicita la creación de una cuenta o el sistema la crea según la lógica definida.
2. El sistema genera un número de cuenta único.
3. El sistema asocia la cuenta al usuario y al banco correspondiente.
4. El sistema registra la cuenta en la base de datos.

### Postcondiciones

- El usuario dispone de una cuenta activa para operar.

---

## CU-04. Consultar saldo

### Actor principal

Usuario bancario

### Descripción

Permite al usuario visualizar el saldo actual de una de sus cuentas.

### Precondiciones

- El usuario debe haber iniciado sesión.
- La cuenta debe existir y pertenecer al usuario.

### Flujo principal

1. El usuario accede al módulo de cuentas.
2. Selecciona una cuenta.
3. El sistema recupera el saldo actual.
4. El sistema muestra la información al usuario.

### Postcondiciones

- El usuario obtiene visibilidad del saldo disponible.

---

## CU-05. Consultar historial de transacciones

### Actor principal

Usuario bancario

### Descripción

Permite revisar el historial de movimientos asociados a una cuenta.

### Precondiciones

- El usuario debe estar autenticado.
- La cuenta debe pertenecer al usuario.

### Flujo principal

1. El usuario accede al historial de movimientos.
2. El sistema consulta las transacciones de la cuenta.
3. El sistema muestra la lista de operaciones registradas.

### Postcondiciones

- El usuario visualiza el historial de la cuenta seleccionada.

---

## CU-06. Realizar transferencia interna

### Actor principal

Usuario bancario

### Descripción

Permite transferir dinero entre cuentas del mismo banco.

### Precondiciones

- El usuario debe estar autenticado.
- La cuenta origen debe pertenecer al usuario.
- La cuenta origen debe tener saldo suficiente.
- La cuenta destino debe existir dentro del mismo banco.

### Flujo principal

1. El usuario accede al formulario de transferencia.
2. Selecciona cuenta origen, cuenta destino y monto.
3. El sistema valida los datos.
4. El sistema verifica que ambas cuentas pertenezcan al mismo banco.
5. El sistema descuenta el monto de la cuenta origen.
6. El sistema acredita el monto en la cuenta destino.
7. El sistema registra la transacción.
8. El sistema confirma el resultado.

### Postcondiciones

- La transacción queda registrada.
- Los saldos quedan actualizados.

---

## CU-07. Realizar transferencia interbancaria

### Actor principal

Usuario bancario

### Descripción

Permite enviar dinero desde una cuenta de un banco hacia una cuenta perteneciente a otro banco.

### Precondiciones

- El usuario debe estar autenticado.
- La cuenta origen debe pertenecer al usuario.
- La cuenta origen debe tener saldo suficiente.
- La cuenta destino debe corresponder a un banco identificado dentro del ecosistema.

### Flujo principal

1. El usuario ingresa los datos de la transferencia.
2. El banco origen valida saldo, formato de cuenta y banco destino.
3. El sistema identifica que la operación es interbancaria.
4. El banco origen inicia la comunicación con el banco receptor.
5. El banco receptor valida la cuenta destino.
6. El banco receptor acredita el monto.
7. El banco origen registra la operación como completada.
8. Ambos bancos registran la transacción según su participación.
9. El sistema informa el resultado al usuario.

### Postcondiciones

- La transferencia queda registrada en ambas entidades.
- El saldo del emisor y del receptor queda actualizado según corresponda.

---

## CU-08. Recibir transferencia interbancaria

### Actor principal

Banco receptor

### Descripción

Permite que un banco procese una solicitud de transferencia proveniente de otra entidad.

### Precondiciones

- El banco receptor debe estar disponible.
- La cuenta destino debe existir y estar habilitada.

### Flujo principal

1. El banco receptor recibe la solicitud.
2. Valida la cuenta destino.
3. Valida los datos mínimos de la operación.
4. Acredita el monto en la cuenta destino.
5. Registra la transacción localmente.
6. Devuelve respuesta al banco emisor.

### Postcondiciones

- La cuenta destino recibe el monto correspondiente.
- La transacción queda registrada.

---

## CU-09. Registrar bancos en analytics

### Actor principal

Analista o administrador del módulo analítico

### Descripción

Permite registrar bancos disponibles para ser monitoreados por el sistema de analytics.

### Precondiciones

- El usuario debe tener permisos suficientes.
- El banco debe contar con una API accesible dentro del entorno del sistema.

### Flujo principal

1. El analista accede al módulo de registro de bancos.
2. Ingresa nombre, código y URL de integración.
3. El sistema almacena la información.
4. El banco queda disponible para futuras consultas analíticas.

### Postcondiciones

- El banco queda incorporado al ecosistema monitoreado.

---

## CU-10. Consultar transacciones desde analytics

### Actor principal

Sistema de analytics

### Descripción

Permite al módulo analítico recuperar transacciones desde los bancos registrados.

### Precondiciones

- Deben existir bancos registrados.
- Debe haber conectividad con sus APIs.

### Flujo principal

1. Analytics consulta los bancos registrados.
2. Solicita información transaccional a cada banco habilitado.
3. Recupera y normaliza los datos.
4. Deja la información disponible para análisis.

### Postcondiciones

- Analytics dispone de datos para generar alertas y visualizaciones.

---

## CU-11. Generar alerta de riesgo

### Actor principal

Sistema de analytics

### Descripción

Permite generar una alerta cuando se detecta una condición sospechosa en el análisis de transacciones.

### Precondiciones

- Deben existir transacciones observables.
- Debe existir al menos una regla de análisis configurada.

### Flujo principal

1. Analytics evalúa las transacciones disponibles.
2. Detecta un patrón que cumple una regla de riesgo.
3. Calcula un puntaje o nivel de severidad.
4. Genera una alerta asociada al contexto correspondiente.
5. Registra la alerta para consulta posterior.

### Postcondiciones

- Existe una alerta disponible en el sistema analítico.

---

## CU-12. Consultar alertas analíticas

### Actor principal

Analista

### Descripción

Permite al analista visualizar las alertas generadas por el sistema.

### Precondiciones

- El analista debe haber iniciado sesión.
- Deben existir alertas registradas.

### Flujo principal

1. El analista accede al panel de alertas.
2. El sistema recupera las alertas almacenadas.
3. Muestra nivel, motivo, cuenta o transacción relacionada y fecha.

### Postcondiciones

- El analista obtiene visibilidad de los hallazgos detectados.

---

## CU-13. Visualizar red de transacciones

### Actor principal

Analista

### Descripción

Permite al analista observar relaciones entre cuentas y bancos mediante una representación gráfica o estructurada de la red transaccional.

### Precondiciones

- Deben existir transacciones registradas.
- El analista debe tener acceso al módulo de analytics.

### Flujo principal

1. El analista accede a la vista de red.
2. El sistema construye nodos y conexiones a partir de las transacciones.
3. El sistema presenta la red de relaciones.
4. El analista explora conexiones, bancos y posibles patrones.

### Postcondiciones

- El analista puede interpretar relaciones dentro del ecosistema.

---

## CU-14. Iniciar seguimiento profundo de cuenta

### Actor principal

Analista

### Descripción

Permite seleccionar una cuenta específica y revisar su actividad de manera profunda dentro del módulo analítico.

### Precondiciones

- El analista debe estar autenticado.
- La cuenta debe existir dentro del ecosistema observado.

### Flujo principal

1. El analista selecciona una cuenta.
2. El sistema consulta su historial de transacciones.
3. Recupera relaciones directas e indirectas relevantes.
4. Identifica contrapartes frecuentes.
5. Muestra alertas asociadas y métricas de comportamiento.
6. Presenta la cuenta dentro del contexto de la red.

### Postcondiciones

- El analista obtiene una visión contextual y detallada de la cuenta seleccionada.

---

## CU-15. Consultar resumen analítico de una cuenta

### Actor principal

Analista

### Descripción

Permite al analista observar un resumen consolidado del comportamiento transaccional de una cuenta.

### Precondiciones

- Debe existir información suficiente sobre la cuenta.
- El analista debe tener acceso autorizado.

### Flujo principal

1. El analista accede al resumen de una cuenta.
2. El sistema calcula o consulta indicadores relevantes.
3. Presenta métricas como frecuencia, montos promedio, concentración y alertas relacionadas.
4. El analista interpreta el comportamiento general de la cuenta.

### Postcondiciones

- El analista cuenta con una síntesis del comportamiento transaccional observado.

---

## Observaciones generales sobre los casos de uso

Los casos de uso definidos en este documento representan la operación esencial del MVP de FlowLens y permiten entender cómo interactúan los actores del sistema con sus módulos principales.

Estos casos cubren tanto la dimensión operativa de los bancos como la dimensión analítica del proyecto, incluyendo la trazabilidad profunda de cuentas y la observación de redes transaccionales.

En consecuencia, constituyen una base funcional útil para:

- orientar el desarrollo;
- validar el flujo esperado del sistema;
- diseñar pruebas;
- justificar la coherencia entre requisitos, arquitectura y comportamiento final.
