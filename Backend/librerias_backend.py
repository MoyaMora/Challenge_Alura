# Libreria para poder cargar la api_key del archivo -> .env
import os

# Libreria para la base de datos  vectorial
import chromadb

# Cargamos la libreria lel modelo de IA con la que trabajaremos
from groq import Groq

# Libreria para gestionar, validar y asegurar que los datos que entran
# y salen de la API sean exactamente lo que esperas.
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

#Librerias para cargar archivos pdf:
from pypdf import PdfReader

#Librerias para tratar y cargar archivo csv:
import pandas as pd
import io

