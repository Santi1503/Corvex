# Corvex - Chatbot para el Perfil Profesional de Santiago Gómez de la Torre Romero

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://www.python.org/)

> **Corvex** es un chatbot interactivo diseñado como microservicio para proporcionar información en tiempo real sobre el perfil profesional de Santiago Gómez de la Torre Romero. A través de la API de OpenAI, Corvex responde preguntas sobre proyectos, contacto y otros temas relevantes en su página profesional.

---

## ✨ Características

- **Interacción en tiempo real**: Corvex permite a los usuarios realizar preguntas sobre el perfil y proyectos de Santiago, proporcionando respuestas precisas y personalizadas.
- **Microservicio Independiente**: Diseñado como un servicio desacoplado, permitiendo fácil integración con otros sistemas o aplicaciones futuras.
- **API de OpenAI**: Aprovecha el poder de la IA para ofrecer respuestas contextualizadas y relevantes en cada interacción.
- **Fácil Configuración y Escalabilidad**: Estructurado para futuras expansiones, permitiendo incorporar nuevas funcionalidades con mínimo impacto.

---

## 📋 Tecnologías Utilizadas

- **Python** - Backend del chatbot.
- **FastAPI** - Para crear el microservicio y gestionar las rutas de la API.
- **OpenAI API** - Para generar respuestas basadas en IA.

---

## 📂 Estructura del Proyecto

```plaintext
Corvex/
├── app/
│   └── main.py          # Punto de entrada del microservicio
├── knowledge_base.json   
└──  unanswered_questions.log     
.env                 # API key de OpenAI
requirements.txt     # Dependencias del proyecto
README.md            # Documentación del proyecto
```
---

## 📈 Roadmap

- **Implementación de preguntas frecuentes**: Añadir respuestas automáticas a preguntas comunes.
- **Ampliación de respuestas**: Incluir información detallada de cada proyecto.
- **Soporte multilingüe**: Implementar respuestas en varios idiomas para usuarios internacionales.

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
