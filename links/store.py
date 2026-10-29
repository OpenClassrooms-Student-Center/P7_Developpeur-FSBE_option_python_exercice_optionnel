"""Stockage en mémoire des liens courts (les données sont perdues au redémarrage)."""
import secrets
import string
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
MAX_URL_LENGTH = 2048


class InvalidUrl(Exception):
    pass


class LinkNotFound(Exception):
    def __init__(self, code):
        super().__init__(f"Aucun lien ne correspond au code « {code} ».")


@dataclass
class Link:
    code: str
    url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    visits: int = 0


class LinkStore:
    def __init__(self):
        self._links = {}
        self._lock = threading.Lock()

    def create(self, url):
        url = validate_url(url=url)
        with self._lock:
            while True:
                code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
                if code not in self._links:
                    link = Link(code=code, url=url)
                    self._links[code] = link
                    return link

    def list(self):
        return sorted(self._links.values(), key=lambda link: link.created_at, reverse=True)

    def find(self, code):
        try:
            return self._links[code]
        except KeyError:
            raise LinkNotFound(code=code) from None

    def visit(self, code):
        with self._lock:
            link = self.find(code=code)
            link.visits += 1
            return link

    def delete(self, code):
        with self._lock:
            if self._links.pop(code, None) is None:
                raise LinkNotFound(code=code)

    def clear(self):
        with self._lock:
            self._links.clear()


def validate_url(url):
    if not isinstance(url, str) or not url.strip():
        raise InvalidUrl("Le champ « url » est obligatoire.")
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        raise InvalidUrl(f"L'URL dépasse {MAX_URL_LENGTH} caractères.")
    parts = urlparse(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise InvalidUrl("L'URL doit commencer par http:// ou https:// et contenir un domaine.")
    return url


store = LinkStore()