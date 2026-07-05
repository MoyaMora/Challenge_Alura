#Creando la interfaz grafica llamando los endpoints de fastapi.

# IMPORTAMOS TODAS LAS LIBRERÍAS EXTERNAS DESDE EL ARCHIVO DE DEPENDENCIAS
from librerias_frontend import *

# Limitando el tamaño del archivo a subir:
#st.set_option('server.maxUploadSize', 2048)

#Cargando variables de entorno donde se encuentra nuestra API_URL:
load_dotenv()

# Leemos la URL del archivo .env. Si no existe, le ponemos una por defecto.
API_URL = os.getenv("API_URL")
print(f"El backend está configurado para correr en: {API_URL}")

# Desactivar advertencia de paralelismo en la interfaz
os.environ["TOKENIZERS_PARALLELISM"] = "false"

st.set_page_config(page_title="Buscador RAG Multidocumento", page_icon="🤖", layout="centered")
st.title("Asistente RAG Multi-Documento")
st.subheader("Carga archivos PDF o CSV y consulta cualquier tipo de información con IA (RAG).")

# Selector visual del tipo de archivo
tipo_fuente = st.radio("Selecciona el tipo de documento:",
    (
        "📄 PDF (Documentos)",
        "📊 CSV (Datos estructurados)"
    ),
    horizontal=True)

# Guardando seleccion de documento.
fuente_key = "pdf" if "PDF" in tipo_fuente else "csv"

# SECCIÓN 1: CARGA DE ARCHIVOS 
st.header("1. Sube tu archivo ")
#st.caption("📌 Tamaño máximo permitido: 200MB | Formatos: PDF o CSV")

extensiones = ["pdf"] if fuente_key == "pdf" else ["csv"]
archivo_subido = st.file_uploader(f"Elige un archivo y haz clic .{fuente_key}", type=extensiones)

if archivo_subido is not None:
    if st.button(f"Procesar .{fuente_key.upper()} en Base Vectorial"):
        with st.spinner("Procesando y generando vectores locales..."):
            files = {"file": (archivo_subido.name, archivo_subido.getvalue(), f"application/{fuente_key}")}
            endpoint = "/subir-pdf" if fuente_key == "pdf" else "/subir-csv"
            try:
                response = requests.post(f"{API_URL}{endpoint}", files=files)
                if response.status_code == 200:
                    st.success(f"¡Archivo {archivo_subido.name} indexado con éxito!")
                else:
                    st.error(f"Error de la API: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ No se pudo conectar con la API. ¿Olvidaste encender FastAPI en el puerto 8000?")

st.markdown("---")

# SECCIÓN 2: CONSULTAS
st.header("2. Realiza tú consulta")
pregunta = st.text_input(f"Haz una pregunta sobre los datos del archivo {fuente_key.upper()}:")

if pregunta:
    if st.button("Enviar Pregunta a la IA"):
        with st.spinner("Buscando evidencias y generando respuesta..."):
            try:
                payload = {"pregunta": pregunta, "fuente": fuente_key}
                response = requests.post(f"{API_URL}/preguntar", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("### 📝 Respuesta del Agente:")
                    st.info(data.get("respuesta_agente", "No se recibió respuesta."))
                    
                    contextos = data.get("contexto_utilizado_rag", [])
                    if contextos:
                        with st.expander("🔍 Ver fragmentos utilizados como evidencia (RAG)"):
                            for idx, ctx in enumerate(contextos):
                                texto_limpio = ctx.replace("\n", " ")
                                st.caption(f"**Fragmento {idx + 1}:**")
                                st.write(texto_limpio)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Error de conexión. Verifica que Uvicorn esté encendido en el puerto 8000.")
