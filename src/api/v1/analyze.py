import base64
import django
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from src.apps.backend.models import Fingerprint, Tool
from src.lib.parsers import TLSParser


class APIAnalyzeView(APIView):
    def get(self, request):
        user_agent = request.headers.get("User-Agent", "undefined")
        client_hello = request.headers.get("X-Client-Hello")
        if not client_hello:
            return self.fallback_response(user_agent=user_agent)

        try:
            response = TLSParser(base64.b64decode(client_hello)).as_json()
            response.update(user_agent=user_agent)
            fp = \
                Fingerprint.objects.filter(hash=response["ja3_hash"], kind=Fingerprint.Kind.JA3).first() or \
                Fingerprint.objects.filter(hash=response["ja3n_hash"], kind=Fingerprint.Kind.JA3N).first()

            tools = fp.tools.all() if fp else []
            response["tools"] = [{"kind": Tool.Kind(item.kind).name, "tool": str(item)} for item in tools]
            return JsonResponse(response, status=status.HTTP_200_OK)

        except (ValueError, django.db.utils.OperationalError):
            return self.fallback_response(user_agent=user_agent)

    @staticmethod
    def fallback_response(**kwargs):
        obj = {
            "ja3_hash": "failed to generate",
            "ja3_text": "failed to generate",
            "ja3n_hash": "failed to generate",
            "ja3n_text": "failed to generate",
            "tools": ()
        }
        obj.update(**kwargs)
        return JsonResponse(obj, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
