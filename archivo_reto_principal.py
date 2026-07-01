import os

# Libreria para la base de datos  vectorial
import chromadb

# Cargamos la libreria lel modelo de IA con la que trabajaremos
from groq import Groq

# Libreria para gestionar, validar y asegurar que los datos que entran
#  y salen de tu API sean exactamente lo que esperas.
from pydantic import BaseModel, Field

# Librerias para aplicacion, subir archivos, comunicacions http:
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# libreria para poner en fastapi texto en los botones de su interfaz:
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
coleccion_pdf = chroma_client.get_or_create_collection(name="datos_pdf", embedding_function=modelo_embeddings)
coleccion_csv = chroma_client.get_or_create_collection(name="datos_csv", embedding_function=modelo_embeddings)

# Configurador para dividir textos largos en fragmentos (Chunks)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,      # Tamaño máximo de caracteres por fragmento
    chunk_overlap=100    # Solapamiento esto sirve para no perder contexto entre fragmentos
)

#--------------------------------------------------------------------------
# Ejecutamos las funciones importadas para cargar los conocimientos
print("Cargando base de conocimientos...")

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

# Consulta web:

class Consulta(BaseModel):
    # Escoger base de conocimiento por el usuario;
    fuente: Literal['pdf','csv'] = Field(description="Tipo de base de conocimiento a consultar: 'csv' o 'pdf'")
    pregunta: str = Field(description="Escribe aquí la pregunta basada en el archivo seleccionado.")

# Endpoint de obtener datos:
@app.get("/")
def inicio():
    # obtencion de datos de cualquiera de los archivos seleccionados:
    conteo_csv = coleccion_csv.count()
    conteo_pdf = coleccion_pdf.count()
    return {
        "mensaje": "¡Bienvenido, Hazle preguntas al Agente Inteligente con RAG!",
        "estado_csv": f"Listo ({conteo_csv} fragmentos cargados)" if conteo_csv > 0 else "No cargado.",
        "estado_pdf": f"Listo ({conteo_pdf} fragmentos cargados)" if conteo_pdf > 0 else "No cargado.",
    }
