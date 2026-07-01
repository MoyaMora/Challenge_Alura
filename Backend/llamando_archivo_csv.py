
#Importacion de librerias.
#Librerias para tratar y cargar archivo csv:
from librerias_backend import *


# CONFIGURACIÓN PARA TERMINAL: Fuerza a pandas a mostrar todas las columnas 
# y extiende el ancho de las mismas, del data frame csv:
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', 100)


def preparar_reviews_csv_subido_para_llm(archivo_bytes):

    # Recibe los bytes de un archivo CSV subido por la API,
    # extrae las reseñas de la columna 'reviewText' 
    # y las devuelve como una lista de textos limpios 
    # para indexar directamente en la base de datos vectorial.
    # param archivo_bytes: Bytes del archivo cargado desde FastAPI
    # return: List[str] con cada reseña individual, o None si falla

    try:
        # Cargamos el DataFrame directamente desde los bytes en memoria
        df = pd.read_csv(io.BytesIO(archivo_bytes))

        # Verificamos la columna mandatoria
        if "reviewText" not in df.columns:
            raise KeyError(
                "La columna 'reviewText' no existe en el archivo CSV."
            )

        # Filtramos valores nulos, convertimos a string y limpiamos espacios extraños
        columna_reviews = df["reviewText"].dropna().astype(str)

        # Convertimos a una lista de reseñas individuales eliminando espacios en blanco en los extremos
        lista_reviews = [review.strip() for review in columna_reviews if review.strip()]

        print(f"CSV procesado exitosamente. Total de filas válidas: {len(lista_reviews)}")
        return lista_reviews

    except Exception as e:
        print(f"Error al procesar el CSV subido: {e}")
        return None
