#Importando librerias:
from librerias_backend import *

# CARGAR VARIABLES DE ENTORNO DESDE EL ARCHIVO .ENV
# Esto busca el archivo .env y carga sus variables
# en la memoria del sistema. Cargando la API_KEY de Groq:
load_dotenv()

# Importo mis librerias creadas para proesar y cargar datos de:
# csv y pdf.
from llamando_archivo_csv import preparar_reviews_csv_subido_para_llm
from llamando_archivo_pdf import preparar_pdf_subido_para_llm

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
#from chromadb.utils import embedding_functions

# Esto descargará el modelo una sola vez y lo correrá localmente sin pedirte llaves API
modelo_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2" # Ó el modelo que se quiera utilizar.
)

# Fragmentos guardados del archivo pdf o csv:
# Creamos o recuperamos las colecciones vectoriales para cada formato.
coleccion_pdf = chroma_client.get_or_create_collection(name="datos_pdf", embedding_function=modelo_embeddings)
coleccion_csv = chroma_client.get_or_create_collection(name="datos_csv", embedding_function=modelo_embeddings)

# Configurador para dividir textos largos en fragmentos (Chunks)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,      # Tamaño máximo de caracteres por fragmento
    chunk_overlap=100    # Solapamiento esto sirve para no perder contexto entre fragmentos
)

#--------------------------------------------------------------------------
# Iniciamos con los ENDPOINTS DE CARGA DE ARCHIVOS PDF Y CSV.
# Ejecutamos las funciones importadas para cargar los conocimientos
print("Cargando base de conocimientos...")

# Endpoint de carga de archivo pdf:
@app.post("/subir-pdf", summary="Sube un archivo PDF de documentos")
# Asegurandose que se sube un archivo pdf:
async def subir_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un formato .pdf válido")

    try:
         # Subiendo el archivo pdf seleccionado:
        texto_completo = preparar_pdf_subido_para_llm(file.file)

        if not texto_completo:
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")

        # RAG: Fragmentar el texto e indexarlo en la base vectorial
        chunks = text_splitter.split_text(texto_completo)

        # Limpiar registros anteriores para evitar confuciones de archivos pdf subidos:
        ids_existentes = coleccion_pdf.get()["ids"]
        if ids_existentes:
            coleccion_pdf.delete(ids=ids_existentes)

        # Insertar los nuevos vectores (Los fragmentos guardados):
        coleccion_pdf.add(
            documents=chunks,
            ids=[f"pdf_chunk_{i}" for i in range(len(chunks))]
        )

        return {"mensaje": f"PDF '{file.filename}' indexado en la Base Vectorial. {len(chunks)} fragmentos listos."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la subida del PDF: {e}")

# Endpoint para subir postear el archivo csv:

# Subir archivo csv:
@app.post("/subir-csv", summary="Sube un archivo CSV de reseñas")
# Aqui sube el archivo convertido a datos entre 0 y 1 por que pasa por la base vectorial
async def subir_csv(file: UploadFile = File(...)):
    #Verificamos si es el formato que se espera, en este caso csv.
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400,detail="El archivo debe ser un formato .csv válido")

    try:
        contenido_bytes = await file.read()
        # Ahora obtenemos una lista de reseñas directamente
        lista_de_reseñas = preparar_reviews_csv_subido_para_llm(contenido_bytes)

        if not lista_de_reseñas:
            raise HTTPException(status_code=400, detail="No se pudo procesar el archivo CSV o estaba vacío.")

        # Limpiar registros anteriores de la colección para evitar mezclar archivos
        ids_existentes = coleccion_csv.get()["ids"]
        if ids_existentes:
            coleccion_csv.delete(ids=ids_existentes)

        # RAG: Almacenamos cada reseña de la lista de forma independiente
        coleccion_csv.add(
            documents=lista_de_reseñas,
            ids=[f"csv_row_{i}" for i in range(len(lista_de_reseñas))]
        )

        return {"mensaje": f"✅ CSV '{file.filename}' indexado. {len(lista_de_reseñas)} reseñas listas de forma individual."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la subida del CSV: {e}")

#---------------------------------------------------------------------------------------
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

# Endpoint de postear datos:

@app.post("/preguntar")
def consultar_agente(consulta: Consulta):
    # Asegurando la eleccion sea de forma correcta
    # Si escribe en mayusculas o minisculas da igual.
    eleccion = consulta.fuente.lower()
    pregunta_usuario = consulta.pregunta

    # Recuperacion de la información del archivo pdf.
    # Verificando si se subio el archivo pdf:
    if eleccion == "pdf":
        if coleccion_pdf.count() == 0:
            raise HTTPException(status_code=400,
                                detail="No hay datos de PDF indexados. Usa /subir-pdf primero.")

    # Recuperando (15 en este caso) Fragmentos lo más similar posible a la pregunta del usuario.
    resultados_busqueda = coleccion_pdf.query(
            
    # La base de datos vectorial toma la pregunta,
    # la convierte automáticamente en números (un embedding o vector)
    # para poder comparar matemáticamente su significado
    # con los fragmentos de texto que ya tengo guardados.
    query_texts=[pregunta_usuario],
    # Evitando que la base de conocimiento sea muy pequeña y de error:
    # Si se obtienen menos fragmentos, me da la cantidad minima. (15,5) daria 5 fragmentos. 
    n_results=min(15, coleccion_pdf.count())
    )

    # Evitando que el documento contenga poca informacion o imagenes:
    docs = resultados_busqueda.get("documents") or []
    if len(docs) == 0 or len(docs[0]) == 0:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron resultados relevantes en la base de datos."
            )

    contexto_recuperado = "\n---\n".join(docs[0])

    # Dandole personalidad al modelo de IA:
    system_prompt = "Eres un asistente experto en comprensión lectora. " \
                    "Responde a la pregunta utilizando estrictamente los fragmentos" \
                    "del documento adjunto."
    
    contenido_completo = f"""Contexto del documento recuperado de la base 
                         de datos:\n\n{contexto_recuperado}\n\nPregunta: {pregunta_usuario}"""
    
    #Aqui va la eleccion del archivo csv
    #
    if eleccion == "csv":
        if coleccion_csv.count() == 0:
            raise HTTPException(status_code=400,
                                 detail="No hay datos de CSV indexados. Usa /subir-csv primero."
            )

    # Recuperamos los 15 fragmentos más similares a la pregunta del usuario
    resultados_busqueda = coleccion_csv.query(
        query_texts=[pregunta_usuario],
        n_results=min(15, coleccion_csv.count())
    )

    # Evitando que el documento contenga poca informacion o imagenes:
    docs = resultados_busqueda.get("documents") or []
    if len(docs) == 0 or len(docs[0]) == 0:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron resultados relevantes en la base de datos."
            )

    contexto_recuperado = "\n---\n".join(docs[0])

    # Dandole personalidad al modelo de IA:
    system_prompt = """ Eres un asistente experto en análisis de sentimientos y compresion lectora.
                         Responde a la pregunta basándote únicamente en los fragmentos del documneto
                         provisto."""
    
    contenido_completo = f"Contexto de reseñas recuperado de la base de datos:\n\n{contexto_recuperado}\n\nPregunta: {pregunta_usuario}"
    
    
    #
    # Usando la IA modelo Groq:

    try:
        # No se olvide subir la api key de groq al archivo .env
        client = Groq()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system",
                 "content": system_prompt},
                 {"role": "user",
                  "content": contenido_completo},
                ],
                temperature=0.2 # Temperatura baja para asegurar que se apegue al contexto recuperado
            )
        return{
            "fuente_utilizada": eleccion,
            "pregunta": pregunta_usuario,
            "respuesta_agente": response.choices[0].message.content,
            # Agregamos los fragmentos reales utilizados para que el usuario verifique la fuente
            "Contexto_Utilizado_Por_El_RAG": resultados_busqueda["documents"][0]
        }
    # Mandando mensaje de error:
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error con la LLModel: {e}")



