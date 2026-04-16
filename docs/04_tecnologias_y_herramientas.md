# 04. Tecnologías y Herramientas

## Introducción

La construcción de FlowLens requiere un conjunto de tecnologías que permitan desarrollar una plataforma distribuida, modular, entendible y desplegable en una VPS. La selección tecnológica del proyecto responde a criterios de simplicidad, rapidez de desarrollo, mantenibilidad, compatibilidad entre componentes y capacidad de demostrar de forma clara el funcionamiento del sistema.

Dado que el objetivo principal es construir una solución funcional para simulación bancaria, comunicación entre entidades y análisis transaccional, se priorizarán herramientas modernas, estables y bien documentadas, evitando complejidad innecesaria en esta etapa del proyecto.

---

## Tecnologías principales del proyecto

### Python

Python será el lenguaje principal del backend de FlowLens.

Se eligió porque:

- permite desarrollar lógica de negocio de forma clara;
- facilita la construcción rápida de APIs;
- tiene excelente soporte para análisis de datos;
- resulta ideal para implementar reglas de riesgo y trazabilidad;
- posee un ecosistema maduro para desarrollo web y scripts de simulación.

Además, Python permite mantener consistencia entre los módulos bancarios, el switch interbancario y la aplicación de analytics.

---

### FastAPI

FastAPI será el framework principal para desarrollar las APIs del sistema.

Se eligió porque:

- permite construir APIs rápidas y modernas;
- genera documentación automática con Swagger;
- facilita el modelado de endpoints;
- se integra bien con Pydantic y SQLAlchemy;
- es adecuado para arquitecturas modulares y servicios independientes.

FastAPI se utilizará en:

- los bancos simulados;
- el módulo de comunicación interbancaria;
- la aplicación de analytics.

---

### SQLAlchemy

SQLAlchemy se utilizará como ORM principal para el modelado y acceso a las bases de datos.

Se eligió porque:

- permite definir entidades del sistema de forma estructurada;
- facilita la relación entre tablas y objetos;
- ayuda a mantener una lógica de persistencia ordenada;
- funciona bien tanto con SQLite como con PostgreSQL;
- ofrece flexibilidad para escalar el proyecto más adelante.

Su uso permitirá modelar elementos clave como usuarios, cuentas, transacciones, bancos registrados y alertas de riesgo.

---

### Pydantic

Pydantic será utilizado para definir esquemas de entrada y salida de datos en las APIs.

Se eligió porque:

- valida automáticamente los datos recibidos;
- mejora la seguridad y consistencia de la información;
- permite definir modelos claros para requests y responses;
- se integra de forma natural con FastAPI.

Su papel será fundamental para asegurar que las operaciones bancarias y analíticas reciban datos estructurados y válidos.

---

## Tecnologías de base de datos

### SQLite

SQLite será la base de datos inicial para el desarrollo del MVP.

Se eligió porque:

- es simple de configurar;
- no requiere un servidor de base de datos adicional;
- permite avanzar rápidamente en prototipado;
- es ideal para entornos de demostración y pruebas iniciales;
- facilita la separación de una base de datos por banco.

En esta etapa, cada banco tendrá su propia base de datos SQLite, reforzando el enfoque distribuido del sistema. La aplicación de analytics también podrá utilizar una base local si se requiere persistir alertas, registros o configuraciones.

---

### PostgreSQL (proyección futura)

Aunque el MVP se desarrollará inicialmente con SQLite, PostgreSQL se considera una opción natural para una evolución posterior del proyecto.

Se contempla porque:

- soporta mejor concurrencia;
- ofrece más robustez en entornos con múltiples usuarios;
- resulta adecuado para despliegues más cercanos a producción;
- escala mejor para mayores volúmenes de datos.

No obstante, PostgreSQL no será obligatorio en la primera fase, ya que se busca priorizar simplicidad y velocidad de implementación.

---

## Tecnologías del frontend

### React

React será utilizado para construir la interfaz de usuario del sistema.

Se eligió porque:

- permite desarrollar interfaces dinámicas y reutilizables;
- facilita la organización por componentes;
- resulta muy útil para dashboards y paneles interactivos;
- tiene gran compatibilidad con librerías de visualización;
- es ampliamente utilizado y bien documentado.

React permitirá construir tanto la parte operativa bancaria como la visualización analítica del sistema.

---

### Vite

Vite será utilizado como herramienta de desarrollo y construcción del frontend.

Se eligió porque:

- ofrece un entorno de desarrollo rápido;
- simplifica la configuración inicial;
- mejora la experiencia durante el desarrollo;
- genera builds eficientes para despliegue.

La combinación React + Vite permitirá crear una interfaz moderna y ligera para FlowLens.

---

### HTML, CSS y JavaScript

Aunque React abstrae buena parte de la construcción visual, el proyecto seguirá apoyándose en HTML, CSS y JavaScript como base de la interfaz.

Estas tecnologías serán necesarias para:

- estructurar pantallas;
- diseñar estilos visuales;
- controlar interacciones del usuario;
- garantizar una experiencia clara y funcional.

---

## Tecnologías para visualización y análisis

### Librería de visualización de red

Para representar la red de transacciones se utilizará una librería orientada a grafos o flujos visuales, como por ejemplo React Flow o Cytoscape.js.

Se requiere una herramienta de este tipo porque el sistema debe mostrar:

- cuentas como nodos;
- transferencias como conexiones;
- relaciones entre bancos;
- posibles patrones visuales de riesgo.

La librería final se seleccionará según facilidad de integración, claridad visual y rendimiento en el MVP.

---

### Reglas de análisis en Python

El análisis inicial de riesgo no dependerá de machine learning complejo, sino de reglas programadas en Python.

Este enfoque se elige porque:

- es más controlable;
- permite explicar mejor los criterios de detección;
- facilita justificar por qué una transacción fue marcada;
- es suficiente para un MVP sólido y defendible.

Entre las reglas que podrán implementarse se encuentran:

- montos inusualmente altos;
- múltiples transacciones pequeñas en poco tiempo;
- cadenas rápidas de movimiento de dinero;
- transferencias repetidas a un mismo destino;
- patrones de concentración.

---

## Tecnologías de autenticación y seguridad

### JWT

JWT se utilizará para la autenticación de usuarios en los módulos que lo requieran.

Se eligió porque:

- permite proteger endpoints;
- facilita la autenticación en APIs REST;
- es una solución liviana y ampliamente adoptada;
- se adapta bien a arquitecturas distribuidas.

Su uso permitirá controlar el acceso a cuentas, operaciones y vistas analíticas.

---

### Passlib o equivalente para hash de contraseñas

Las contraseñas no deberán almacenarse en texto plano.

Para ello se utilizará una librería de hashing como Passlib, ya que permite:

- proteger credenciales;
- aplicar buenas prácticas básicas de seguridad;
- separar claramente autenticación y persistencia.

Esto resulta especialmente importante si la plataforma será desplegada en una VPS y utilizada por terceros para pruebas.

---

## Herramientas de desarrollo

### Visual Studio Code

VS Code será el entorno de desarrollo principal.

Se elige porque:

- facilita trabajar con múltiples carpetas y servicios;
- tiene buena integración con Python, React y Markdown;
- simplifica navegación, depuración y organización del proyecto.

---

### Git y GitHub

Git será utilizado para control de versiones y GitHub para respaldo y gestión del repositorio.

Se eligen porque:

- permiten llevar seguimiento de cambios;
- facilitan experimentar sin perder estabilidad;
- ayudan a mantener orden durante el desarrollo;
- son esenciales para despliegue y colaboración.

---

### Markdown

La documentación del proyecto se elaborará en archivos Markdown.

Se elige porque:

- es simple;
- legible;
- portable;
- ideal para repositorios técnicos;
- fácil de convertir a otros formatos si se necesita.

---

## Herramientas de despliegue

### VPS Linux

El sistema será desplegado en una VPS con Linux.

Se eligió este entorno porque:

- permite controlar completamente la infraestructura;
- facilita hospedar múltiples servicios independientes;
- se adapta bien a APIs, frontend y bases de datos ligeras;
- resulta adecuado para pruebas públicas controladas.

---

### Nginx

Nginx se utilizará como reverse proxy y servidor web.

Se eligió porque:

- permite enrutar tráfico a múltiples servicios;
- facilita servir el frontend estático;
- mejora la organización del despliegue;
- es una herramienta estándar y confiable para VPS.

---

### Uvicorn

Uvicorn será utilizado para ejecutar las aplicaciones FastAPI.

Se eligió porque:

- es liviano;
- compatible con FastAPI;
- adecuado para desarrollo y despliegues pequeños o medianos;
- ofrece una ejecución simple de los servicios backend.

---

### systemd o equivalente

Para mantener los servicios corriendo en la VPS, se utilizará systemd o una herramienta equivalente de administración de procesos.

Esto permitirá:

- iniciar servicios automáticamente;
- reiniciarlos si fallan;
- mantener un control ordenado sobre los procesos del sistema.

---

## Herramientas auxiliares

### Swagger / OpenAPI

La documentación automática generada por FastAPI será útil para:

- probar endpoints;
- validar requests y responses;
- revisar la API durante el desarrollo;
- facilitar depuración y demostraciones.

---

### Scripts de seed y simulación

Se desarrollarán scripts en Python para:

- crear bancos;
- poblar usuarios;
- crear cuentas;
- generar transacciones;
- simular patrones sospechosos.

Estos scripts serán esenciales para demostrar el funcionamiento del sistema sin depender de interacción manual constante.

---

## Justificación general de la selección tecnológica

La pila tecnológica elegida para FlowLens responde a una estrategia clara:

- usar tecnologías modernas pero accesibles;
- mantener una curva de desarrollo razonable;
- construir un MVP sólido sin sobreingeniería;
- facilitar el despliegue en una VPS;
- permitir crecimiento progresivo del proyecto.

La selección busca equilibrio entre rapidez, claridad, mantenibilidad y capacidad de presentación.

---

## Resultado esperado de esta base tecnológica

Con estas herramientas se espera construir una plataforma capaz de:

- operar múltiples bancos simulados;
- comunicar entidades independientes;
- analizar actividad transaccional;
- generar alertas;
- visualizar redes;
- desplegarse y funcionar correctamente en un entorno real de pruebas.

En consecuencia, la base tecnológica de FlowLens no solo respalda el desarrollo del sistema, sino que también fortalece su coherencia técnica y su viabilidad como proyecto demostrativo.
