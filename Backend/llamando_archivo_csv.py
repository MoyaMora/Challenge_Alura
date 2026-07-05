
from librerias_backend import *

def preparar_reviews_csv_subido_para_llm(archivo_bytes):
    # Ese parámetro contiene el archivo CSV en formato bytes.

    # Cuando el usuario sube un archivo en FastAPI 
    # normalmente llega así: bytes no en una direcion url
    
    try:
        # Convirtiendo los bytes en un archivo "virtual".
        # y se obtiene el data frame con pandas.
        df = pd.read_csv(io.BytesIO(archivo_bytes))
        
        # Eliminando filas vacias, donde las columnas estan vacias.
        df = df.dropna(how="all")

        # En esta lista; Aquí se guardará un texto
        # por cada fila del CSV.
        lista_reviews = []

        # Recorremos fila por fila.
        for _, row in df.iterrows():
            
            # Almacenando todas las columnas de una sola fila.
            texto = []
            
            # Recorremos columna por columna
            for columna, valor in row.items():
                # Verificamos que no este vacia la columna
                if pd.notna(valor):
                    # Creando columnda
                    texto.append(f"{columna}: {valor}")
            
            # Uniendo todo (Fila, columna), separado por un salto de linea 
            texto_fila = "\n".join(texto)

            # Guarda todo, Cada elemento representa un documento independiente
            # que después puede convertirse en un embedding y 
            # almacenarse en ChromaDB.
            lista_reviews.append(texto_fila)

        print(f"CSV procesado correctamente. Registros: {len(lista_reviews)}")

        return lista_reviews

    except Exception as e:

        print(e)

        return None
