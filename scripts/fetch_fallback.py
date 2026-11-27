#!/usr/bin/env python3
"""Fallback con Scrapling (solo HTTP). Respeta robots.txt. Sin modo sigiloso."""
import argparse, datetime, hashlib, json, pathlib, sys
from urllib import robotparser
from urllib.parse import urlparse

import yaml
from scrapling.fetchers import Fetcher

OK, POLITICA, BLOQUEADO, TECNICO = 0, 3, 4, 5


def robots_ok(url):
    p = urlparse(url)
    rp = robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return True  # robots.txt ilegible: seguir y dejarlo en el changelog
    return rp.can_fetch("*", url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--fuente")
    ap.add_argument("--out", default="datos_crudos")
    a = ap.parse_args()

    if a.fuente:
        with open("fuentes.yml", encoding="utf-8") as fh:
            fuentes = yaml.safe_load(fh)
        f = next((x for x in fuentes if x.get("nombre") == a.fuente), None)
        if not f or not f.get("fallback_scrapling"):
            print("BLOQUEADO_POLITICA: fuente sin fallback permitido")
            return POLITICA

    if not robots_ok(a.url):
        print("BLOQUEADO_POLITICA: robots.txt")
        return POLITICA

    try:
        page = Fetcher.get(a.url, timeout=30)
    except Exception as e:
        print(f"FALLO_TECNICO: {e}")
        return TECNICO

    status = getattr(page, "status", None)
    if status in (401, 403, 429):
        print(f"BLOQUEADO: HTTP {status}")
        return BLOQUEADO
    if status is None or status >= 400:
        print(f"FALLO_TECNICO: HTTP {status}")
        return TECNICO

    try:
        texto = page.markdown()
    except Exception:
        texto = ""
    if not texto or not texto.strip():
        print("FALLO_TECNICO: pagina vacia (posible JavaScript)")
        return TECNICO

    ahora = datetime.datetime.now(datetime.timezone.utc)
    h = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    carpeta = pathlib.Path(a.out) / ahora.strftime("%Y%m")
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{h[:8]}.md"
    ruta.write_text(texto, encoding="utf-8")

    print(json.dumps({
        "metodo": "scrapling",
        "url": a.url,
        "status": status,
        "sha256": h,
        "archivo": str(ruta),
        "fecha_utc": ahora.isoformat(),
    }, ensure_ascii=False))
    return OK


if __name__ == "__main__":
    sys.exit(main())
