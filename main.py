from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import torch
import os
import json
import spacy
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Ruta de la base de conocimiento y el registro de preguntas sin respuesta, configurada en .env
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base.json")
UNANSWERED_LOG_PATH = os.getenv("UNANSWERED_LOG_PATH", "unanswered_questions.log")

# Cargar el contenido JSON de las credenciales de Firebase desde la variable de entorno
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
temp_cred_path = "(/temp/firebase_credentials.json)"

# Crear el archivo temporal de credenciales
with open(temp_cred_path, "w") as f:
    f.write(firebase_credentials_json)

# Inicializar Firebase con el archivo temporal de credenciales
cred = credentials.Certificate(temp_cred_path)
firebase_admin.initialize_app(cred)

# Inicializar la aplicación de FastAPI
app = FastAPI()

# Modelo de similitud de oraciones
model = SentenceTransformer('all-MiniLM-L6-v2')

# Inicializar spaCy para preprocesamiento en español
nlp = spacy.load("es_core_news_sm")

# Conectar a la base de datos de Firebase
db = firestore.client()

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

# Función para registrar preguntas sin respuesta en Firebase
def log_unanswered_question(question):
    # Crear una referencia a la colección en Firebase
    unanswered_questions_ref = db.collection("unanswered_questions")

    # Agregar un nuevo documento con la pregunta y la fecha
    unanswered_questions_ref.add({
        "question": question,
        "timestamp": datetime.now()
    })

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

# Endpoint para ver preguntas sin respuesta
@app.get("/corvex/unanswered_questions")
async def get_unanswered_questions():
    unanswered_questions_ref = db.collection("unanswered_questions")
    docs = unanswered_questions_ref.stream()

    unanswered_questions = [{"id": doc.id, **doc.to_dict()} for doc in docs]

    return {"unanswered_questions": unanswered_questions}