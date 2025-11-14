"""
Endpoints liés aux intentions (formulaire Rejoindre + outils admin).
"""

import csv
import io
import json
import re
from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.models import Intent
from core.serializers import IntentSerializer

from .common import logger, require_admin_token

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_MESSAGE_LENGTH = 2000
HONEYPOT_FIELDS = {"website", "nickname", "comment"}


def _parse_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    return request.POST.dict()


def _has_honeypot(data: dict) -> bool:
    return any(data.get(field) for field in HONEYPOT_FIELDS)


def _validate_payload(data: dict):
    missing = [field for field in ("nom", "email", "profil") if not data.get(field)]
    if missing:
        raise ValueError("Champs manquants: " + ", ".join(missing))
    if not EMAIL_REGEX.match(data["email"]):
        raise ValueError("Email invalide.")
    message = data.get("message") or ""
    if len(message) > MAX_MESSAGE_LENGTH:
        raise OverflowError("Message trop long.")


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def rejoindre(request):
    payload = _parse_payload(request)

    if _has_honeypot(payload):
        return Response({"ok": True, "id": None}, status=status.HTTP_200_OK)

    try:
        _validate_payload(payload)
    except OverflowError as exc:
        return Response({"ok": False, "error": str(exc)}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    except ValueError as exc:
        return Response({"ok": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    intent = Intent.objects.create(
        nom=payload["nom"],
        email=payload["email"],
        profil=payload["profil"],
        message=payload.get("message", ""),
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        document_url=payload.get("document_url", ""),
    )

    return Response({"ok": True, "id": intent.pk}, status=status.HTTP_200_OK)


def _validate_admin_request(request):
    token = require_admin_token(request)
    if not token:
        return Response({"ok": False, "error": "Token invalide."}, status=status.HTTP_401_UNAUTHORIZED)
    return None


def _apply_common_filters(queryset, params):
    from_date = params.get("from")
    if from_date:
        try:
            queryset = queryset.filter(created_at__gte=datetime.strptime(from_date, "%Y-%m-%d"))
        except ValueError:
            pass

    to_date = params.get("to")
    if to_date:
        try:
            limit_date = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(created_at__lte=limit_date)
        except ValueError:
            pass

    profil = params.get("profil")
    if profil:
        queryset = queryset.filter(profil=profil)

    search = params.get("q")
    if search:
        queryset = queryset.filter(
            Q(nom__icontains=search) | Q(email__icontains=search) | Q(message__icontains=search)
        )

    return queryset


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def admin_data(request):
    maybe_error = _validate_admin_request(request)
    if maybe_error:
        return maybe_error

    try:
        queryset = _apply_common_filters(Intent.objects.all(), request.query_params)
        limit = min(int(request.query_params.get("limit", 200)), 1000)
        offset = max(int(request.query_params.get("offset", 0)), 0)
        total_count = queryset.count()
        intents = queryset.order_by("-created_at")[offset : offset + limit]
        serializer = IntentSerializer(intents, many=True)
        return Response(
            {
                "ok": True,
                "rows": serializer.data,
                "count": len(serializer.data),
                "total": total_count,
                "limit": limit,
                "offset": offset,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Admin data error: %s", exc, exc_info=True)
        return Response({"ok": False, "error": "Erreur serveur BDD."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def export_intents(request):
    maybe_error = _validate_admin_request(request)
    if maybe_error:
        return maybe_error

    try:
        queryset = _apply_common_filters(Intent.objects.all(), request.query_params)
        intents = queryset.order_by("-created_at")[:10000]

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "nom", "email", "profil", "message", "created_at", "ip", "user_agent", "document_url"])
        for intent in intents:
            writer.writerow(
                [
                    intent.id,
                    intent.nom,
                    intent.email,
                    intent.profil,
                    intent.message,
                    intent.created_at.isoformat() if intent.created_at else "",
                    intent.ip or "",
                    intent.user_agent or "",
                    intent.document_url or "",
                ]
            )

        response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = "attachment; filename=intents.csv"
        return response
    except Exception as exc:  # noqa: BLE001
        logger.error("Export error: %s", exc, exc_info=True)
        return Response({"ok": False, "error": "Erreur serveur BDD."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([permissions.AllowAny])
def delete_intent(request, intent_id):
    maybe_error = _validate_admin_request(request)
    if maybe_error:
        return maybe_error

    try:
        intent = Intent.objects.get(pk=intent_id)
        intent.delete()
        return Response({"ok": True, "deleted": True}, status=status.HTTP_200_OK)
    except Intent.DoesNotExist:
        return Response({"ok": False, "error": "Intention non trouvée."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as exc:  # noqa: BLE001
        logger.error("Delete error: %s", exc, exc_info=True)
        return Response({"ok": False, "error": "Erreur serveur BDD."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

