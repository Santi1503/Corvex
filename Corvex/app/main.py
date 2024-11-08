from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import torch
import os
import json
import spacy

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Ruta de la base de conocimiento y el registro de preguntas sin respuesta, configurada en .env
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base.json")
UNANSWERED_LOG_PATH = os.getenv("UNANSWERED_LOG_PATH", "unanswered_questions.log")

# Inicializar la aplicación de FastAPI
app = FastAPI()

# Modelo de similitud de oraciones
model = SentenceTransformer('all-MiniLM-L6-v2')

# Inicializar spaCy para preprocesamiento en español
nlp = spacy.load("es_core_news_sm")

# Función de preprocesamiento para normalizar la pregunta del usuario
def preprocess_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

# Función para cargar la base de conocimiento desde un archivo JSON
def load_knowledge_base():
    with open(KNOWLEDGE_BASE_PATH, "r") as f:
        return json.load(f)["FAQs"]

# Cargar preguntas frecuentes y generar embeddings
faqs = load_knowledge_base()
questions = [faq["question"] for faq in faqs]
answers = [faq["answer"] for faq in faqs]
faq_embeddings = model.encode(questions, convert_to_tensor=True)

# Modelo de datos para las solicitudes de chat
class ChatRequest(BaseModel):
    question: str

# Función para registrar preguntas sin respuesta en un archivo de log
def log_unanswered_question(question):
    with open(UNANSWERED_LOG_PATH, "a") as f:
        f.write(question + "\n")

# Endpoint principal del chatbot
@app.post("/corvex/chat")
async def chat_with_corvex(request: ChatRequest):
    # Preprocesar la pregunta del usuario antes de la similitud
    preprocessed_question = preprocess_text(request.question)
    question_embedding = model.encode(preprocessed_question, convert_to_tensor=True)

    # Calcular la similitud con las preguntas frecuentes
    cos_scores = util.pytorch_cos_sim(question_embedding, faq_embeddings)[0]
    max_score, max_index = torch.max(cos_scores, dim=0)

    # Devolver la respuesta si la similitud es suficiente
    if max_score > 0.7:  # Puedes ajustar el umbral según la precisión deseada
        answer = answers[max_index]
    else:
        answer = "Lo siento, no tengo información sobre esa pregunta."
        log_unanswered_question(request.question)  # Registrar pregunta para revisión

    return {"answer": answer}

# Endpoint para agregar manualmente nuevas preguntas y respuestas
@app.post("/corvex/admin/add")
async def add_to_knowledge_base(question: str, answer: str):
    # Agregar la nueva pregunta y respuesta a la base de datos y recargar embeddings
    faqs.append({"question": question, "answer": answer})
    with open(KNOWLEDGE_BASE_PATH, "w") as f:
        json.dump({"FAQs": faqs}, f, indent=2)

    global faq_embeddings
    questions.append(question)
    answers.append(answer)
    faq_embeddings = model.encode(questions, convert_to_tensor=True)

    return {"message": "Pregunta y respuesta añadidas exitosamente."}

# Ruta raíz para prueba
@app.get("/")
async def root():
    return {"message": "Bienvenido a Corvex - Chatbot de Santiago"}