# Importacion de archivo py como libreria:
from llamando_archivo_csv import preparar_reviews_csv_para_llm
from llamando_archivo_pdf import preparar_pdf_para_llm

# Cargando la base de datos csv y pdf.
# Definimos las rutas de los archivos en tu computadora:
ruta_archivo_csv = "/Users/josemoya/VisualStudio/Challenge_Alura_2026/reviews_challenge.csv"
ruta_archivo_pdf = "/Users/josemoya/VisualStudio/Challenge_Alura_2026/Política_de_Uso_de_Correo_Electrónico_y_Seguridad_de_la_Información.pdf"

# Ejecutamos las funciones importadas para cargar los conocimientos
print("Cargando base de conocimientos...")
llm_input_text_csv = preparar_reviews_csv_para_llm(ruta_archivo_csv, max_characters=2000)
llm_input_text_pdf = preparar_pdf_para_llm(ruta_archivo_pdf,max_characters=2000)

# Cargando libreria para trabajar con la IA Groq:
from groq import Groq

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