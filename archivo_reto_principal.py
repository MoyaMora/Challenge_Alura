import os
# Libreria para la base de datos  vectorial
import chromadb
# Cargamos la libreria lel modelo de IA con la que trabajaremos
from groq import Groq

from pydantic import BaseModel, Field
# Librerias para aplicacion 
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# libreria para poner en fastapi texto
from typing import Literal


# Importación de librerías para partir texto y generar embeddings locales
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Usamos un modelo de embeddings ligero de HuggingFace
# que corre localmente sin llaves de API
from chromadb.utils import embedding_functions

# Cargando las variables de entorno:
# API_KEY de Groq.
# Direción URL donde corre mi backend de FastAPI
from dotenv import load_dotenv

# CARGAR VARIABLES DE ENTORNO DESDE EL ARCHIVO .ENV
# Esto busca el archivo .env y carga sus variables
# en la memoria del sistema. Cargando la API_KEY de Groq:
load_dotenv()

# Importo mis librerias creadas para proesar y cargar datos de:
# csv y pdf.
from llamando_archivo_csv import preparar_reviews_csv_para_llm
from llamando_archivo_pdf import preparar_pdf_para_llm

# Iniciando la creación de la aplicacion con fastapi:
app = FastAPI(
    title="Agente de IA Multidocumento con RAG - Desafío OCI",
    description="""API pública con soporte RAG real utilizando ChromaDB y Groq
                 para consultar documentos extensos sin desbordar el contexto.""",
)

# Validación de seguridad al arrancar el servidor,
# Verificamos que la API_KEY este:
if not os.environ.get("GROQ_API_KEY"):
    print("⚠️ ADVERTENCIA: La variable de entorno 'GROQ_API_KEY' no está configurada.")

# Ending de ERROR: en la página creada por fastapi si la persona teclea alguna frase
#  que no sea csv o pdf para escoger el documento a subir, marca error.
@app.exception_handler(RequestValidationError)
async def manejador_error_validacion(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Datos de consulta inválidos",
            "mensaje_alerta": "Por favor, asegúrate de enviar un formato correcto. El campo 'fuente' solo acepta 'csv' o 'pdf'.",
            "detalles_tecnicos": exc.errors()
        }
    )

# Aqui comienza la configuración de la base de datos vectorial (RAG)
# Inicializamos ChromaDB en memoria
chroma_client = chromadb.Client()

# Usamos un modelo de embeddings ligero de HuggingFace que corre localmente sin llaves de API
from chromadb.utils import embedding_functions

# Esto descargará el modelo una sola vez y lo correrá localmente sin pedirte llaves API
modelo_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2" # Ó el modelo que se quiera utilizar.
)

# Creamos o recuperamos las colecciones vectoriales para cada formato
coleccion_csv = chroma_client.get_or_create_collection(name="datos_csv", embedding_function=modelo_embeddings)
coleccion_pdf = chroma_client.get_or_create_collection(name="datos_pdf", embedding_function=modelo_embeddings)

# Configurador para dividir textos largos en fragmentos (Chunks)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,      # Tamaño máximo de caracteres por fragmento
    chunk_overlap=100    # Solapamiento esto sirve para no perder contexto entre fragmentos
)

#--------------------------------------------------------------------------

# Iniciamos con los ENDPOINTS DE CARGA (Subir archivos csv y pdf):
@app.post("/subir-pdf", summary="Sube un archivo PDF de documentos")
async def subir_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un formato .pdf válido")

    try:
        texto_completo = preparar_pdf_para_llm(file.file)

        if not texto_completo:
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")

        # RAG: Fragmentar el texto e indexarlo en la base vectorial
        chunks = text_splitter.split_text(texto_completo)

        # Limpiar registros anteriores
        ids_existentes = coleccion_pdf.get()["ids"]
        if ids_existentes:
            coleccion_pdf.delete(ids=ids_existentes)

        # Insertar los nuevos vectores
        coleccion_pdf.add(
            documents=chunks,
            ids=[f"pdf_chunk_{i}" for i in range(len(chunks))]
        )

        return {"mensaje": f"PDF '{file.filename}' indexado en la Base Vectorial. {len(chunks)} fragmentos listos."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la subida del PDF: {e}")

# Cargando la base de datos csv y pdf.
# Definimos las rutas de los archivos en tu computadora:
ruta_archivo_csv = "/Users/josemoya/VisualStudio/Challenge_Alura_2026/reviews_challenge.csv"
ruta_archivo_pdf = "/Users/josemoya/VisualStudio/Challenge_Alura_2026/Política_de_Uso_de_Correo_Electrónico_y_Seguridad_de_la_Información.pdf"

# Ejecutamos las funciones importadas para cargar los conocimientos
print("Cargando base de conocimientos...")

llm_input_text_csv = preparar_reviews_csv_para_llm(ruta_archivo_csv, max_characters=2000)
llm_input_text_pdf = preparar_pdf_para_llm(ruta_archivo_pdf,max_characters=2000)



# Haciendo el chat box para que responda de forma automática:
print("¡Bienvenido al Chatbot Inteligente!")
print("Puedes preguntar sobre las reseñas de productos (CSV) o sobre el contenido del PDF.")
print("Escribe 'csv' para preguntar sobre el CSV, 'pdf' para preguntar sobre el PDF, o 'salir' para terminar.")

# Ciclo infinito:
while True:

    # Preguntando por las opciones que se tiene:
    Eleccion = input("\n¿Qué base de conocimiento quieres usar (csv/pdf/salir)? ").lower()

    # Salimos del programa:
    if Eleccion == 'salir':
        print("¡Hasta luego!")
        break
    
    # Escogio el archivo csv:
    elif Eleccion == 'csv':
        if not llm_input_text_csv:
            print("No hay texto del CSV disponible para consultar. Asegúrate de que el CSV fue procesado correctamente.")
            continue
        
        pregunta_usuario = input("Pregunta sobre las reseñas: ")
        
       # Dando el RAG al LLM para el CSV
        contenido_completo = f"He aquí un conjunto de reseñas de productos, separadas por '####':\n\n{llm_input_text_csv}\n\nBasado en estas reseñas, {pregunta_usuario}"
        system_prompt = """Eres un asistente experto en análisis de sentimientos de productos. " \
                        "Responde a la pregunta del usuario basándote únicamente en el texto de las reseñas proporcionadas.
                        Si hay informacion en ingles traduzcala a español para que el usuario entienda."""
    
    # Escogiendo el archivo pdf:
    elif Eleccion == 'pdf':
        # Validamos si hay información dentro del PDF:
        if not llm_input_text_pdf:
            print("❌ No hay texto del PDF disponible para consultar. Asegúrate de que el archivo existe y pypdf pudo leerlo.")
            continue
            
        # Si hay, capturamos la duda existencial sobre el PDF:
        pregunta_usuario = input("Pregunta sobre el documento PDF: ")
        
        # Dando el RAG al LLM para el PDF
        contenido_completo = f"A continuación se te proporciona el contenido extraído del documento PDF:\n\n{llm_input_text_pdf}\n\nBasado estrictamente en este texto, responde a la siguiente consulta: {pregunta_usuario}"
        
        # Cambiamos las instrucciones del sistema para que se comporte como un lector de PDFs espirituales/técnicos
        system_prompt = """Eres un asistente experto en comprensión lectora y análisis de documentos, 
                        experto tambien en el area de un juego de cartas llamado pokemon." \
                        " Tu objetivo es responder las preguntas del usuario utilizando única y
                        exclusivamente la información proveída del PDF. 
                        Si la respuesta no se encuentra en el texto,indícalo amablemente.
                        Si hay informacion en inglés, traduzca a español para que el usuario entienda."""

    # Si no escogio ningun archivo csv o salir, mostrar:
    else:
        print("Opción no válida. Por favor, elige 'csv', 'pdf' o 'salir'.")
        continue

    # Ya existen las variables para el modelo, procedemos a llamar a la API de groq:
    try:
        # Creando instancia cliente groq: 
        client = Groq() 

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contenido_completo}
            ]
        )
        # Imprimimos la respuesta del modelo groq:
        print("\n🤖 Respuesta del LLM:")
        print(response.choices[0].message.content)
    
    except Exception as e:
        print(f"Ocurrió un error al comunicarse con el LLM: {e}")
        print("Por favor, asegúrate de que tu clave de API sea válida y de que no hayas excedido las cuotas.")