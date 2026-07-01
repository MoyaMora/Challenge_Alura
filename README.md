# 🤖 Agente de IA para Consulta Inteligente de Documentos

## 📖 Descripción del proyecto

Imaginemos el siguiente escenario:

Una empresa (ya sea una fintech, una consultora o una startup) cuenta con una gran cantidad de documentos internos, como:

- Manuales
- Informes
- Políticas
- Hojas de cálculo

El problema es que las personas colaboradoras invierten mucho tiempo buscando información dentro de estos documentos.

### Objetivo

Desarrollar un **agente de Inteligencia Artificial** que permita realizar preguntas en lenguaje natural y obtener respuestas precisas sin necesidad de abrir o revisar manualmente los documentos.

---

# 🚀 Etapas del proyecto

## 1. Procesamiento de documentos

El primer paso consiste en seleccionar uno o más documentos (PDF o CSV) y procesarlos para que la aplicación pueda comprender su contenido.

Los documentos pueden contener información como:

- 📄 Políticas internas de la empresa.
- 📊 Datos de ventas.
- 💻 Documentación técnica.
- 📚 Manuales de usuario.
- 📈 Reportes internos.

> **Nota:** Se proporciona un documento de ejemplo, pero cada participante puede utilizar cualquier documento que desee para personalizar su agente.

---

## 2. Construcción del agente de IA

Una vez procesado el documento, el siguiente paso consiste en crear un agente capaz de responder preguntas sobre su contenido.

### Ejemplos de consultas

**Pregunta**

> ¿Cuál fue el producto más vendido en diciembre de 2015?

**Pregunta**

> ¿Qué lenguajes de programación utiliza el backend de la plataforma?

El agente deberá localizar la información dentro del documento y responder de manera clara y precisa.

---

## 3. Despliegue en Oracle Cloud (OCI)

Finalmente, el agente deberá publicarse en la nube utilizando **Oracle Cloud Infrastructure (OCI)**.

El objetivo es que la aplicación deje de ejecutarse únicamente en el equipo local y quede disponible públicamente.

---

# 🛠 Tecnologías sugeridas

Las siguientes tecnologías son únicamente una recomendación.

Puedes utilizar cualquier herramienta que se adapte mejor a tu solución.

|        Tecnología        |          Uso            |
|--------------------------|-------------------------|
| Python                   | Desarrollo del proyecto |
| LangChain                | Construcción del agente |
| PyPDF                    | Lectura de archivos PDF |
| Pandas                   | Lectura de archivos CSV |
| ChatGPT / Gemma / Cohere | Modelo de lenguaje      |
| OCI Compute              | Despliegue en la nube   |

> **Importante:** Estas herramientas son sugerencias, no requisitos obligatorios.

---

# 📦 Entregables

El proyecto deberá publicarse en un repositorio de GitHub que incluya:

- Un repositorio organizado.
- Historial de commits.
- Código fuente completo.
- Archivo **README.md**.

---

# 📄 Contenido mínimo del README

El README deberá incluir:

## 1. Descripción de la arquitectura

Explicar cómo está construida la solución.

---

## 2. Ejemplos de uso

Mostrar preguntas que el agente puede responder.

**Ejemplo**

```
Pregunta:
¿Cuál fue el producto más vendido en diciembre de 2015?

Respuesta:
El producto más vendido fue...
```

---

## 3. Instrucciones de instalación

Explicar cómo ejecutar el proyecto localmente.

---

## 4. Evidencia del despliegue

Agregar alguno de los siguientes elementos:

- Enlace público de la aplicación.
- Captura de pantalla.
- URL del despliegue en OCI.

Esto servirá para demostrar que el proyecto fue desplegado correctamente.
