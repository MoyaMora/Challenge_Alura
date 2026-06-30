
#Importacion de librerias:
import pandas as pd

# CONFIGURACIÓN PARA TERMINAL: Fuerza a pandas a mostrar todas las columnas 
# y extiende el ancho de las mismas, del data frame csv:
#pd.set_option('display.max_columns', None)
#pd.set_option('display.width', 100)


def preparar_reviews_csv_para_llm(ruta_csv, max_characters=2000):
    """
    Carga un archivo CSV de reseñas, une la columna 'reviewText'
    y la recorta al tamaño máximo especificado para el LLM.
    """
    try:
        # Cargamos el DataFrame:
        df = pd.read_csv(ruta_csv)
        
        # Extraemos la columna llamada reviewText del data frame.
        # si no esta manda un error:
        if "reviewText" not in df.columns:
            # error de ortografia:
            raise KeyError("La columna 'reviewText' no existe en el archivo CSV.")
        
        # Guardamos solo los comentarios de la columna reviewText del data frame:    
        columna_reviews = df["reviewText"].dropna().astype(str) # dropna() evita errores si hay celdas vacías
        
        # Unimos todas las reseñas del data frame con el separador ####
        reviews_unidas = "####".join(columna_reviews)
        
        # Recortamos los caracteres al límite del contexto del LLM, esto por los tokens de las IAs de pago.
        texto_recortado = reviews_unidas[:max_characters]
        
        # Mensajes informativos en la terminal para verificar que todo va bien
        print(f"✅ Archivo cargado exitosamente. Total de filas: {len(df)}")
        print(f"📊 Longitud del texto enviado al LLM: {len(texto_recortado)} caracteres.\n")
        
        return texto_recortado

    # Mensaje para errores comunes:
    except FileNotFoundError:
        # Por si falla la ruta dada, como me paso pero se ve elegante el error:
        print(f"❌ Error: No se encontró el archivo en la ruta: {ruta_csv}")
        return None
    
    except Exception as e:
        # Quien sabe que error ocurra pero me paso igual xD y lo agregamos por si acaso:
        print(f"❌ Ocurrió un error inesperado: {e}")
        return None
