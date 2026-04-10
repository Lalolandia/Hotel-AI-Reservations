# app/routes/chat_routes.py
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import current_user
from app import db
from app.models.chat import Chat
from app.models.habitacion import Habitacion
from app.models.paquete import Paquete
from groq import Groq
import os

chat_bp = Blueprint('chat', __name__)


def _get_hotel_context() -> str:
    """Construye el contexto del hotel con habitaciones y paquetes de la BD."""
    habitaciones = Habitacion.query.all()
    paquetes     = Paquete.query.all()

    hab_texto = ""
    for h in habitaciones:
        if h.tipo and h.estado == 'disponible':
            hab_texto += (
                f"\n- Habitación #{h.numero} | Tipo: {h.tipo.nombre} | "
                f"Piso: {h.piso or '—'} | Capacidad: {h.tipo.capacidad} persona(s) | "
                f"Precio: ${h.tipo.precio_noche}/noche | "
                f"Descripción: {h.tipo.descripcion or 'Sin descripción'}"
            )

    if not hab_texto:
        hab_texto = "\n- No hay habitaciones disponibles en este momento."

    paq_texto = ""
    for p in paquetes:
        paq_texto += (
            f"\n- {p.nombre} | Precio: ${p.precio_total} | "
            f"Descripción: {p.descripcion or 'Sin descripción'}"
        )

    if not paq_texto:
        paq_texto = "\n- No hay paquetes disponibles en este momento."

    return f"HABITACIONES DISPONIBLES:{hab_texto}\n\nPAQUETES TURÍSTICOS:{paq_texto}"


def _get_system_prompt() -> str:
    context = _get_hotel_context()
    return f"""Eres HotelBot, el asistente virtual del hotel HotelAI en San José, Costa Rica.
Tu misión es ayudar a los huéspedes a encontrar la habitación y paquete ideal según sus preferencias.

INFORMACIÓN ACTUAL DEL HOTEL:
{context}

INSTRUCCIONES:
1. Saluda de forma cálida al inicio de la conversación.
2. Haz preguntas para entender sus necesidades: cuántas personas viajan, fechas, tipo de experiencia (descanso, aventura, romance, familia), preferencias de vista, presupuesto.
3. Recomienda 1 o 2 habitaciones específicas y justifica por qué son ideales.
4. Si aplica, sugiere un paquete turístico complementario.
5. Usa tono amigable y profesional. Puedes usar emojis con moderación.
6. Si quieren reservar, indícales que pueden hacerlo en /reservar.
7. Responde SIEMPRE en español.
8. Mantén respuestas concisas (máximo 3-4 párrafos).
9. Si preguntan algo fuera del hotel, redirige amablemente la conversación."""


@chat_bp.route('/chat')
def chat():
    session['chat_history'] = []
    return render_template('chatAI/chat.html')


@chat_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data    = request.json
    mensaje = data.get('mensaje', '').strip()

    if not mensaje:
        return jsonify({'error': 'Mensaje vacío'}), 400

    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'GROQ_API_KEY no configurado en .env'}), 500

    # Recuperar historial de sesión
    history = session.get('chat_history', [])

    # Armar mensajes para Groq: system + historial + mensaje actual
    messages = [{"role": "system", "content": _get_system_prompt()}]

    for msg in history:
        messages.append({"role": msg['role'], "content": msg['content']})

    messages.append({"role": "user", "content": mensaje})

    # Limitar contexto a últimos 20 mensajes + system
    if len(messages) > 21:
        messages = [messages[0]] + messages[-20:]

    try:
        client   = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model       = "llama-3.1-8b-instant",  # gratis, rápido
            messages    = messages,
            max_tokens  = 1024,
            temperature = 0.7,
        )
        respuesta = response.choices[0].message.content

    except Exception as e:
        return jsonify({'error': f'Error al contactar el asistente: {str(e)}'}), 500

    # Actualizar historial
    history.append({'role': 'user',      'content': mensaje})
    history.append({'role': 'assistant', 'content': respuesta})

    if len(history) > 20:
        history = history[-20:]

    session['chat_history'] = history
    session.modified = True

    # Guardar en BD si hay usuario logueado
    if current_user.is_authenticated:
        try:
            registro = Chat(
                cliente_id      = current_user.id,
                mensaje_usuario = mensaje,
                respuesta_ia    = respuesta
            )
            db.session.add(registro)
            db.session.commit()
        except Exception:
            pass

    return jsonify({'respuesta': respuesta})


@chat_bp.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    session['chat_history'] = []
    session.modified = True
    return jsonify({'ok': True})