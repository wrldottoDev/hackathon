# 08. Reglas de Negocio

## Introducción

Las reglas de negocio de FlowLens definen las condiciones, restricciones y criterios que gobiernan el comportamiento del sistema dentro de su alcance como plataforma distribuida de simulación bancaria y análisis transaccional.

Estas reglas aseguran coherencia entre la lógica operativa de los bancos, la comunicación interbancaria y el módulo de analytics. Además, permiten establecer límites claros sobre cómo deben registrarse, validarse, analizarse y presentarse las operaciones dentro del ecosistema.

Las reglas aquí descritas no representan regulación bancaria real aplicable en producción, sino lineamientos internos del sistema para garantizar consistencia funcional, trazabilidad y una implementación demostrativa técnicamente sólida.

---

## Reglas de negocio del dominio bancario

### RN-01. Pertenencia única de cuenta a banco

Cada cuenta bancaria debe pertenecer a un único banco dentro del ecosistema.

### RN-02. Pertenencia única de cuenta a usuario

Cada cuenta bancaria debe estar asociada a un único usuario propietario dentro del banco que la emite.

### RN-03. Identificación obligatoria del banco en la cuenta

Toda cuenta debe contener o permitir inferir un código de banco que facilite su identificación dentro del ecosistema.

### RN-04. Unicidad del número de cuenta

El número de cuenta debe ser único dentro del sistema lógico del proyecto, evitando ambigüedad en operaciones y análisis.

### RN-05. Estado válido de cuenta para operar

Solo las cuentas activas podrán participar en transacciones normales de envío o recepción.

### RN-06. Saldo suficiente para transferir

Una cuenta no podrá ejecutar una transferencia si no posee saldo suficiente para cubrir el monto solicitado.

### RN-07. Monto válido de transacción

No se permitirá registrar ni ejecutar transacciones con monto menor o igual a cero.

### RN-08. Prohibición de transferencia a la misma cuenta

No se podrá realizar una transferencia cuyo origen y destino sean exactamente la misma cuenta.

### RN-09. Registro obligatorio de operación

Toda operación aceptada por el sistema deberá quedar registrada en la base de datos correspondiente.

### RN-10. Conservación de historial

El historial de transacciones de una cuenta debe mantenerse disponible para consulta posterior dentro del alcance del entorno de prueba.

---

## Reglas de negocio de transferencias internas

### RN-11. Validación local en transferencias internas

Cuando la cuenta origen y la cuenta destino pertenezcan al mismo banco, la validación y ejecución de la transacción deberán resolverse internamente en ese banco.

### RN-12. Actualización simultánea de saldo

Toda transferencia interna completada debe reflejar la disminución del saldo en la cuenta origen y el aumento correspondiente en la cuenta destino.

### RN-13. Registro del estado de la transacción

Toda transferencia debe registrar su estado, incluso cuando no llegue a completarse exitosamente.

---

## Reglas de negocio de transferencias interbancarias

### RN-14. Identificación previa del banco destino

Antes de procesar una transferencia interbancaria, el sistema debe identificar correctamente el banco receptor.

### RN-15. Validación previa en el banco origen

El banco origen debe validar saldo, formato de cuenta y condiciones mínimas antes de iniciar la comunicación con otro banco.

### RN-16. Registro de participación en ambos bancos

Toda transferencia interbancaria completada debe quedar reflejada tanto en el banco emisor como en el banco receptor, según la lógica definida para cada entidad.

### RN-17. Dependencia del estado final de la operación

Una transferencia interbancaria solo se considerará completada cuando el banco destino confirme la recepción y acreditación de fondos.

### RN-18. Manejo de fallos de comunicación

Si una transferencia interbancaria no puede completarse por fallo de validación o comunicación, el sistema deberá registrar el resultado con un estado adecuado.

### RN-19. Conservación del contexto interbancario

Toda transacción interbancaria debe conservar información suficiente para identificar:

- cuenta origen;
- banco origen;
- cuenta destino;
- banco destino;
- monto;
- fecha y hora;
- estado final de la operación.

---

## Reglas de negocio del módulo de analytics

### RN-20. Separación entre operación y análisis

El módulo de analytics no debe ejecutar operaciones bancarias, sino únicamente observar, consultar y analizar información transaccional proveniente de los bancos.

### RN-21. Dependencia de datos observables

El análisis de riesgo solo podrá construirse a partir de información expuesta o disponible desde los bancos integrados al ecosistema.

### RN-22. Generación condicionada de alertas

Una alerta solo deberá generarse cuando una regla analítica detecte una condición que supere un criterio o umbral definido.

### RN-23. Asociación de alerta con contexto suficiente

Toda alerta debe contener contexto suficiente para ser interpretada, incluyendo al menos la cuenta o transacción involucrada, el motivo y el nivel de riesgo.

### RN-24. Clasificación obligatoria de alertas

Toda alerta generada por analytics deberá clasificarse en un nivel de riesgo definido por el sistema.

### RN-25. Persistencia de alertas

Las alertas generadas deberán conservarse para consulta y revisión posterior dentro del módulo analítico.

### RN-26. Carácter explicable del análisis

Las reglas de análisis implementadas en el MVP deben ser lo suficientemente claras como para justificar por qué una operación fue marcada como sospechosa.

---

## Reglas de negocio del seguimiento profundo

### RN-27. Acceso restringido al seguimiento profundo

El seguimiento profundo de cuentas solo podrá ser consultado por usuarios autorizados del módulo analítico.

### RN-28. Selección explícita de cuenta

El seguimiento profundo deberá iniciarse a partir de la selección explícita de una cuenta por parte del analista.

### RN-29. Reconstrucción contextual de actividad

El seguimiento profundo no debe limitarse a una lista de transacciones, sino reconstruir el contexto de la cuenta dentro de la red.

### RN-30. Inclusión de relaciones relevantes

El seguimiento profundo deberá mostrar relaciones directas y, cuando sea posible dentro del alcance del MVP, relaciones indirectas significativas.

### RN-31. Inclusión de alertas asociadas

Si una cuenta seleccionada posee alertas previas o está vinculada a transacciones marcadas, dicha información deberá formar parte del seguimiento profundo.

### RN-32. Carácter analítico y no operativo

El seguimiento profundo es una función de observación y análisis, no una operación bancaria para el usuario final.

---

## Reglas de negocio de identidad y trazabilidad

### RN-33. Identificación clara de entidades

Toda cuenta, banco y transacción debe poder identificarse de forma clara dentro del sistema.

### RN-34. Trazabilidad temporal obligatoria

Toda transacción debe registrar una marca temporal que permita reconstruir su secuencia dentro del historial.

### RN-35. Trazabilidad suficiente para análisis de red

La información almacenada debe permitir reconstruir relaciones entre cuentas y bancos dentro del ecosistema.

### RN-36. Coherencia entre origen y destino

Toda transacción debe reflejar de forma consistente qué cuenta envía, qué cuenta recibe y a qué banco pertenece cada una.

---

## Reglas de negocio del entorno demo

### RN-37. Uso exclusivo de datos sintéticos o anonimizados no reidentificables

La versión demostrativa pública del sistema solo podrá operar con datos sintéticos o anonimizados no reidentificables.

### RN-38. Prohibición de exposición pública de datos reales identificables

El entorno público no deberá exponer información financiera real identificable de terceros.

### RN-39. Restricción de vistas analíticas sensibles en entorno público

Las vistas sensibles del módulo analítico no deberán quedar accesibles sin autenticación y control de acceso.

### RN-40. Coherencia con el propósito demostrativo

Toda funcionalidad del sistema debe mantenerse alineada con el carácter técnico, académico y demostrativo del proyecto.

---

## Reglas de negocio de integridad general

### RN-41. Coherencia entre saldo y operaciones

El saldo de una cuenta debe reflejar correctamente el efecto acumulado de las operaciones válidas registradas.

### RN-42. Prohibición de estados ambiguos

Las operaciones y alertas no deben quedar en estados ambiguos o sin clasificación definida.

### RN-43. Compatibilidad entre módulos

Los datos compartidos entre bancos y analytics deben seguir una estructura compatible que permita su interpretación correcta.

### RN-44. Persistencia mínima necesaria para auditoría demostrativa

El sistema debe conservar la información mínima necesaria para reconstruir operaciones, alertas y relaciones dentro del entorno de prueba.

---

## Observaciones generales sobre las reglas de negocio

Las reglas de negocio de FlowLens tienen como finalidad asegurar que el sistema conserve coherencia operativa, trazabilidad transaccional y claridad analítica a lo largo de todos sus módulos.

Estas reglas servirán como base para:

- implementar validaciones en backend;
- definir condiciones de prueba;
- construir lógica de alertas;
- justificar el comportamiento esperado del sistema;
- mantener consistencia entre documentación e implementación.

En consecuencia, las reglas de negocio constituyen un puente entre la visión conceptual del proyecto y la lógica concreta que deberá aplicarse en el desarrollo.
