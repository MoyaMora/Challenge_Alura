from pypdf import PdfReader

def preparar_pdf_subido_para_llm(archivo_subido):

    """Procesa un PDF completo subido a la aplicación en memoria,
    extrayendo y limpiando todo su texto para ser indexado en el pipeline RAG,
    param archivo_subido: El objeto del archivo subido (File-like object de FastAPI),
    return: str con todo el texto limpio del documento o None si falla
    """
    texto_completo = []

    try:
        # pypdf lee directamente el objeto SpoolerFile que le manda FastAPI (file.file)
        lector = PdfReader(archivo_subido)

        for num_pagina, pagina in enumerate(lector.pages, start=1):
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                # Limpieza básica por página: remover espacios en blanco innecesarios en los bordes
                 lineas_limpias = [linea.strip() for linea in texto_pagina.splitlines() if linea.strip()]
                 texto_completo.append("\n".join(lineas_limpias))

        if not texto_completo:
            print("⚠️ No se pudo extraer texto de ninguna página del PDF.")
            return None

        # Unimos todo el texto conservando saltos de línea limpios entre páginas
        texto_unido = "\n\n".join(texto_completo)

        print(
            f"✅ PDF extraído con éxito. Total: {len(lector.pages)} páginas, {len(texto_unido)} caracteres listos para RAG."
        )
        return texto_unido

    except Exception as e:
        print(f"❌ Error al procesar el PDF subido: {e}")
        return None
