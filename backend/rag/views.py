import json
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from .chroma_utils import retrieve
from .services import generate_stream
import os 
import uuid
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .utils import extract_text_from_pdf, chunk_text, DATA_DIR
from .chroma_utils import upsert_chunks
import sys
import asyncio 
from django.views import View


class DocumentUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]  # 👈 important !

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "Aucun fichier envoyé"}, status=status.HTTP_400_BAD_REQUEST)

        # Sauvegarde dans rag/data/uploads
        save_path = os.path.join(DATA_DIR, file_obj.name)
        with open(save_path, "wb+") as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        # Extraction texte
        text = extract_text_from_pdf(save_path)
        if not text:
            return Response({"error": "Impossible d’extraire du texte du PDF"}, status=status.HTTP_400_BAD_REQUEST)

        # Découpage
        raw_chunks = chunk_text(text)
        chunks = []
        for i, raw in enumerate(raw_chunks):
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": raw,
                "meta": {"filename": file_obj.name, "chunk": i}
            })

        # Indexation dans Chroma
        upsert_chunks(chunks)

        return Response({
            "message": "PDF uploadé et indexé avec succès",
            "filename": file_obj.name,
            "chunks": len(chunks)
        }, status=status.HTTP_201_CREATED)

class ChatStreamView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        question = request.data.get("message", "").strip()
        if not question:
            # ✅ toujours retourner un Response, pas None
            return Response({"error": "Aucune question fournie"}, status=400)

        # Récupération du contexte
        results = retrieve(question, top_k=5)
        docs = results.get("documents", [[]])[0]     
        metadatas = results.get("metadatas", [[]])[0]
        context_text = "\n---\n".join(docs)

        #print("==== CONTEXTE UTILISÉ ====")
        #print(context_text)
        #print("==========================")

        def event_stream():
            # sources
            yield f"event: sources\ndata: {json.dumps(metadatas)}\n\n"
            # tokens du LLM
            full_answer = ""
            try:
                for token in generate_stream(question, context_text):
                    full_answer += token
                    yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
                # réponse complète
                yield f"event: full\ndata: {json.dumps({'answer': full_answer})}\n\n"
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            # fin
            yield "event: done\ndata: {}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")



class AsyncChatStreamView(View):
    async def get(self, request, *args, **kwargs):
        question = request.GET.get("q", "").strip()
        if not question:
            return StreamingHttpResponse(
                "event: error\ndata: {\"error\": \"Aucune question fournie\"}\n\n",
                content_type="text/event-stream",
                status=400
            )

        results = retrieve(question, top_k=5)
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        context_text = "\n---\n".join(docs)

        async def event_stream():
            yield f"event: sources\ndata: {json.dumps(metadatas)}\n\n"
            full_answer = ""
            try:
                for token in generate_stream(question, context_text):
                    full_answer += token
                    yield f"event: token\ndata: {json.dumps({'text': token})}\n\n"
                    await asyncio.sleep(0)  # flush
                yield f"event: full\ndata: {json.dumps({'answer': full_answer})}\n\n"
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            yield "event: done\ndata: {}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        response["Access-Control-Allow-Origin"] = "*"
        return response