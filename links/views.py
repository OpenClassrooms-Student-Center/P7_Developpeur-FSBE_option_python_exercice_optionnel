import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from .store import InvalidUrl, LinkNotFound, store


def error_response(code, message, status):
    return JsonResponse({"code": code, "message": message}, status=status)


def to_json(link):
    return {
        "code": link.code,
        "url": link.url,
        "lienCourt": f"{settings.MINILIEN_BASE_URL}/r/{link.code}",
        "creeLe": link.created_at.isoformat().replace("+00:00", "Z"),
        "visites": link.visits,
    }


@require_http_methods(["GET", "POST"])
def link_list(request):
    if request.method == "GET":
        return JsonResponse([to_json(link=link) for link in store.list()], safe=False)

    try:
        body = json.loads(request.body or b"null")
    except json.JSONDecodeError:
        body = None
    if not isinstance(body, dict):
        return error_response(
            code="REQUETE_INVALIDE",
            message='Le corps de la requête doit être un JSON de la forme {"url": "..."}.',
            status=400,
        )
    try:
        link = store.create(url=body.get("url"))
    except InvalidUrl as e:
        return error_response(code="URL_INVALIDE", message=str(e), status=400)
    response = JsonResponse(to_json(link=link), status=201)
    response["Location"] = f"/api/liens/{link.code}"
    return response


@require_http_methods(["GET", "DELETE"])
def link_detail(request, code):
    try:
        if request.method == "GET":
            return JsonResponse(to_json(link=store.find(code=code)))

        if request.headers.get("X-Admin-Token") != settings.MINILIEN_ADMIN_TOKEN:
            return error_response(
                code="ACCES_REFUSE",
                message="Jeton d'administration absent ou incorrect (en-tête X-Admin-Token).",
                status=401,
            )
        store.delete(code=code)
        return HttpResponse(status=204)
    except LinkNotFound as e:
        return error_response(code="LIEN_INTROUVABLE", message=str(e), status=404)


@require_GET
def redirect_to_url(request, code):
    try:
        link = store.visit(code=code)
    except LinkNotFound as e:
        return error_response(code="LIEN_INTROUVABLE", message=str(e), status=404)
    return HttpResponseRedirect(link.url)