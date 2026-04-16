# 07. Requisitos No Funcionales

## Introducción

Los requisitos no funcionales de FlowLens describen las condiciones de calidad que debe cumplir el sistema para ser considerado sólido, coherente, usable y técnicamente defendible.

A diferencia de los requisitos funcionales, estos no se enfocan en acciones específicas del sistema, sino en características como seguridad, mantenibilidad, rendimiento, modularidad, escalabilidad, despliegue y experiencia de uso.

Dado que FlowLens será una plataforma distribuida, desplegada en una VPS y accesible para pruebas controladas, los requisitos no funcionales son esenciales para garantizar que el sistema no solo funcione, sino que además lo haga de manera ordenada, comprensible y segura dentro de su alcance demostrativo.

---

## Requisitos no funcionales de arquitectura

### RNF-01. Arquitectura modular

El sistema debe construirse con una arquitectura modular que separe claramente los componentes bancarios, interbancarios, analíticos y de presentación.

### RNF-02. Independencia de bases de datos por banco

Cada banco debe operar con su propia base de datos independiente, sin compartir persistencia operativa con otros bancos.

### RNF-03. Desacoplamiento entre operación y análisis

El módulo de analytics debe mantenerse desacoplado de la operación interna de cada banco.

### RNF-04. Escalabilidad conceptual

La arquitectura debe permitir agregar nuevos bancos o nuevas reglas analíticas sin requerir un rediseño completo del sistema.

### RNF-05. Organización por capas

La estructura del proyecto debe facilitar la separación entre presentación, lógica de negocio, acceso a datos y análisis.

---

## Requisitos no funcionales de seguridad

### RNF-06. Protección de credenciales

Las contraseñas de los usuarios no deben almacenarse en texto plano.

### RNF-07. Autenticación de accesos sensibles

Los módulos sensibles del sistema deben requerir autenticación previa.

### RNF-08. Restricción por roles

El sistema debe aplicar restricciones de acceso según el rol del usuario, diferenciando al menos entre usuario bancario y analista autorizado.

### RNF-09. Protección de vistas analíticas

Las funciones de alertas, seguimiento profundo y análisis detallado no deben quedar expuestas públicamente sin control de acceso.

### RNF-10. Protección del entorno demostrativo

La plataforma pública debe funcionar en un entorno controlado, evitando exposición de información sensible real.

---

## Requisitos no funcionales de datos y confidencialidad

### RNF-11. Uso de datos sintéticos o anonimizados

La versión demostrativa del sistema debe operar únicamente con datos sintéticos o anonimizados no reidentificables.

### RNF-12. Protección de la trazabilidad sensible

Aunque el sistema permita seguimiento profundo y análisis de relaciones, dicha información debe presentarse de forma coherente con el carácter demostrativo y controlado del proyecto.

### RNF-13. Integridad de registros

Las transacciones y alertas deben almacenarse de forma consistente para evitar pérdida de trazabilidad.

### RNF-14. Claridad en identificación de entidades

Los datos del sistema deben mantener identificadores claros para bancos, cuentas y transacciones, de modo que puedan ser interpretados correctamente por los distintos módulos.

---

## Requisitos no funcionales de rendimiento

### RNF-15. Tiempo de respuesta razonable

Las operaciones principales del sistema deben responder en tiempos adecuados para un entorno demostrativo, evitando retrasos perceptibles innecesarios.

### RNF-16. Rendimiento adecuado en consultas analíticas básicas

Las consultas de alertas, historial y seguimiento profundo deben ejecutarse con un rendimiento suficiente para demostrar el sistema sin degradación excesiva.

### RNF-17. Soporte para pruebas concurrentes moderadas

La plataforma debe soportar múltiples interacciones de prueba en la VPS dentro del alcance del MVP.

---

## Requisitos no funcionales de disponibilidad y despliegue

### RNF-18. Despliegue en VPS Linux

El sistema debe ser compatible con despliegue en una VPS basada en Linux.

### RNF-19. Acceso vía navegador

La plataforma debe poder utilizarse desde un navegador web moderno sin requerir instalaciones adicionales para los usuarios de prueba.

### RNF-20. Servicios desplegables por separado

Los bancos, el módulo interbancario y el sistema de analytics deben poder ejecutarse como servicios independientes.

### RNF-21. Compatibilidad con reverse proxy

La solución debe poder integrarse con un reverse proxy como Nginx para su publicación en la VPS.

### RNF-22. Reinicio controlado de servicios

La plataforma debe poder administrarse mediante mecanismos que permitan iniciar, detener y reiniciar servicios de manera ordenada.

---

## Requisitos no funcionales de mantenibilidad

### RNF-23. Código entendible

El código del sistema debe mantenerse legible y comprensible para facilitar su desarrollo y evolución.

### RNF-24. Estructura consistente del proyecto

Los archivos, carpetas y módulos deben seguir una organización coherente con la arquitectura definida.

### RNF-25. Facilidad de extensión

La estructura del sistema debe facilitar la incorporación de nuevos bancos, nuevos tipos de alertas y nuevas vistas analíticas.

### RNF-26. Documentación técnica suficiente

El proyecto debe contar con documentación clara sobre arquitectura, tecnologías, modelo de datos, requisitos y despliegue.

---

## Requisitos no funcionales de usabilidad

### RNF-27. Interfaz comprensible

La interfaz debe ser clara y comprensible para usuarios que prueben el sistema por primera vez.

### RNF-28. Navegación simple

La navegación entre módulos bancarios y analíticos debe ser ordenada y fácil de seguir.

### RNF-29. Presentación clara de alertas y hallazgos

Las alertas y los resultados analíticos deben mostrarse de forma comprensible, evitando ambigüedad innecesaria.

### RNF-30. Visualización interpretable de red

La red transaccional debe visualizarse de forma que ayude realmente a interpretar relaciones y patrones.

---

## Requisitos no funcionales de calidad técnica

### RNF-31. Validación de datos de entrada

Las APIs deben validar adecuadamente los datos recibidos antes de procesarlos.

### RNF-32. Consistencia entre módulos

Los diferentes servicios del sistema deben manejar formatos de datos compatibles para facilitar integración.

### RNF-33. Manejo básico de errores

El sistema debe manejar errores de forma controlada y comprensible, tanto a nivel de backend como de interfaz.

### RNF-34. Trazabilidad de operaciones

Las operaciones importantes deben quedar registradas de manera que puedan ser revisadas posteriormente.

### RNF-35. Coherencia del entorno demo

La experiencia pública del sistema debe mantenerse alineada con su propósito de simulación, análisis y demostración técnica.

---

## Requisitos no funcionales de presentación y defensa del proyecto

### RNF-36. Claridad conceptual

La estructura del sistema debe ser lo suficientemente clara para ser explicada y defendida en una presentación formal o hackathon.

### RNF-37. Coherencia entre diseño e implementación

La solución implementada debe reflejar la arquitectura y el alcance definidos en la documentación.

### RNF-38. Capacidad de demostración en vivo

La plataforma debe poder utilizarse en una demostración en vivo mostrando bancos, transferencias, alertas y análisis sin depender de configuraciones excesivamente complejas.

---

## Observaciones generales sobre los requisitos no funcionales

Los requisitos no funcionales definidos para FlowLens buscan garantizar que el sistema no solo sea funcional, sino también estructurado, seguro dentro de su alcance, mantenible y apto para despliegue y demostración.

Dado que se trata de una plataforma distribuida con múltiples componentes y exposición pública controlada en una VPS, estas condiciones de calidad son fundamentales para que el proyecto se perciba como una solución seria, consistente y bien pensada.

En consecuencia, los requisitos no funcionales constituyen una base crítica para orientar decisiones técnicas, validar el resultado final y fortalecer la presentación del proyecto.
