Imaginemos el siguiente escenario: fuimos contratades por una empresa; Puede ser una fintech (tecnología financiera), una consultora o una startup (empresa emergente), que tiene grandes volúmenes de documentos internos: manuales, informes, políticas y hojas de cálculo. El problema es que las personas pierden horas buscando información dentro de sus archivos. 

La solución que se requiere es un agente de inteligencia artificial que cualquier persona colaboradora pueda usar para hacer preguntas y recibir respuestas directas en lenguaje natural, sin necesidad de abrir ningún documento.

Explicando las tres etapas del proyecto.

El desafío tiene tres partes principales. Expliquemos cada una:

1. Primero, elegiremos un documento; Puede ser un PDF o un CSV, crearemos código que lea y procese ese
   archivo. Es decir, nuestra aplicación entenderá el contenido que hay dentro del documento. Ese documento puede tratar sobre:
   
      1.1 Políticas internas de la empresa.
      1.2 Datos de ventas de productos.
      1.3 Documentación sobre las herramientas y tecnologías que la empresa utiliza. 
   
   También pondremos a disposición un documento de sugerencia, pero podremos utilizar los 
   documentos que queramos y personalizar nuestro agente, porque este proyecto es nuestro.

2. En segundo lugar; Construiremos un agente de IA que pueda responder preguntas sobre ese documento.
   Alguien podría escribir, por ejemplo:
     
     2.1 “¿Cuál fue el producto más vendido en diciembre de 2015?”
     2.2 “¿Qué lenguajes de programación se usan en el back-end (parte del servidor) de la plataforma de
         ventas de la empresa?”.
   
   El agente encuentra la respuesta en el documento y la devuelve de forma clara. Así de simple.

3. Y aquí está el gran diferencial, vamos a hacer el deploy (implementación) de ese agente en la nube de
   Oracle (OCI). Eso significa que nuestra aplicación saldrá de nuestra computadora y estará accesible públicamente; Ejecutándose de verdad en la nube.

Describiendo tecnologías y entregables:

Ahora, hablemos de las tecnologías. No hace falta alarmarnos por la lista. Sugerimos:
   a) Python (Python) para escribir el código. 
   b) LangChain (LangChain) para montar el agente.
   c) PyPDF (PyPDF) o Pandas (Pandas) para leer los documentos.
   d) Un modelo de lenguaje que puede ser:
         -> Gemma.
         -> ChatGPT. 
         -> Cohere. 
u otro, para hacer que la magia suceda. 

Para el deploy (implementación), la sugerencia es:
   e) OCI Compute (OCI Compute).

pero estas son sugerencias, no obligaciones. Si contamos con una herramienta que conocemos mejor y que tenga más sentido para nuestro proyecto, podemos usarla. 

El proyecto, como dijimos, es de quien lo crea. Lo importante es que la solución que presentemos funcione.

Hablemos entonces de lo que necesitamos entregar. Debemos publicar el código en GitHub, con:

1. Un repositorio organizado.
2. Un historial de commits (confirmaciones).
3. Un README bien elaborado, con:
   3.1 Una descripción de la arquitectura que montamos.
   3.2 Ejemplos de preguntas y respuestas que el agente puede resolver.
   3.3 Instrucciones para quien quiera ejecutar el proyecto.
   3.4 Un enlace o una captura de pantalla de la aplicación corriendo en OCI, para comprobar que el deploy (implementación) realmente funcionó.
