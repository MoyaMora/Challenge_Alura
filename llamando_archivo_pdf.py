from pypdf import PdfReader

def preparar_pdf_para_llm(ruta_pdf, max_characters=2000):
    texto_completo = []
    
    try:
        with open(ruta_pdf, "rb") as archivo:
            lector = PdfReader(archivo)
            
            for pagina in lector.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo.append(texto_pagina)
                    
        # 1. Unimos todo el texto primero
        texto_unido = "\n".join(texto_completo)
        
        # 2. CORRECCIÓN CLAVE: Forzamos el recorte estricto aquí
        texto_recortado = texto_unido[:max_characters]
        
        print(f"✅ PDF recortado con éxito a {len(texto_recortado)} caracteres.")
        return texto_recortado

    except Exception as e:
        print(f"❌ Error al leer PDF: {e}")
        return None