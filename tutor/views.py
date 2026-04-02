import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from .models import ConversationLog
from .prompts import build_debug_prompt, build_explain_prompt, build_chat_prompt


def get_openai_client():
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def call_openai(system_prompt: str, user_message: str, messages: list = None) -> str:
    client = get_openai_client()

    if messages:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
    else:
        full_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=full_messages,
        temperature=0.3,
        max_tokens=2000,
    )

    return response.choices[0].message.content.strip()


class DebugView(APIView):
    def post(self, request):
        code = request.data.get("code", "").strip()
        error = request.data.get("error", "").strip()

        if not code:
            return Response({"error": "Please provide the code you want to debug."}, status=400)
        if not error:
            return Response({"error": "Please provide the error message."}, status=400)

        try:
            system_prompt, user_message = build_debug_prompt(code, error)
            ai_response = call_openai(system_prompt, user_message)

            ConversationLog.objects.create(
                mode="debug",
                user_input=f"CODE:\n{code}\n\nERROR:\n{error}",
                ai_response=ai_response,
            )

            return Response({"result": ai_response}, status=200)

        except ValueError as e:
            return Response({"error": str(e)}, status=500)
        except Exception as e:
            return Response({"error": f"AI service error: {str(e)}"}, status=500)


class ExplainView(APIView):
    def post(self, request):
        content = request.data.get("content", "").strip()

        if not content:
            return Response({"error": "Please provide code or a concept to explain."}, status=400)

        try:
            system_prompt, user_message = build_explain_prompt(content)
            ai_response = call_openai(system_prompt, user_message)

            ConversationLog.objects.create(
                mode="explain",
                user_input=content,
                ai_response=ai_response,
            )

            return Response({"result": ai_response}, status=200)

        except ValueError as e:
            return Response({"error": str(e)}, status=500)
        except Exception as e:
            return Response({"error": f"AI service error: {str(e)}"}, status=500)


class ChatView(APIView):
    def post(self, request):
        question = request.data.get("question", "").strip()
        history = request.data.get("history", [])

        if not question:
            return Response({"error": "Please ask a question."}, status=400)

        if not isinstance(history, list):
            history = []

        try:
            system_prompt, messages = build_chat_prompt(question, history)
            ai_response = call_openai(system_prompt, None, messages)

            ConversationLog.objects.create(
                mode="chat",
                user_input=question,
                ai_response=ai_response,
            )

            return Response({"result": ai_response}, status=200)

        except ValueError as e:
            return Response({"error": str(e)}, status=500)
        except Exception as e:
            return Response({"error": f"AI service error: {str(e)}"}, status=500)
