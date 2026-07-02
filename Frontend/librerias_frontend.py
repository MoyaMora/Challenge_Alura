#Librerias para la API se vea bonita:
import streamlit as st
import requests
import os

# Cargando las variables de entorno:
# API_KEY de Groq.
# Direción URL donde corre mi backend de FastAPI
from dotenv import load_dotenv