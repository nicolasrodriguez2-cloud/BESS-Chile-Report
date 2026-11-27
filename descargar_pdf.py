#!/usr/bin/env python3
"""Baja un PDF a la carpeta de su fuente y calcula el hash.
Respeta robots.txt. Para ante 401/403/429. Sin reintentos. Headers normales."""
import argparse, datetime, hashlib, json, pathlib, re, sys
import urllib.error
import urllib.request
from urllib import robotparser
from urllib.parse import urlparse

import yaml

UA = "BESS-Chile-Report-bot/1.0"
MAX_BYTES = 60 * 1024 * 1024
OK, POLITICA, BLOQUEADO, TECNICO = 0, 3, 4, 5


def robots_ok(url):
    p = urlparse(url)
    rp = robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()  # 401/403 en robots.txt cuenta como "no"
    except Exception:
        return True  # robots.txt ilegible: seguir y dejarlo en el changelog
    return rp.can_fetch("*", url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--fuente", required=True)
    a = ap.parse_args()

    with open("fuentes.yml", encoding="utf-8") as fh:
        fuentes = yaml.safe_load(fh)
    f = next((x for x in fuentes if x.get("nombre") == a.fuente), None)
    if not f:
        print(f"FALLO_TECNICO: fuente desconocida {a.fuente}")
        return TECNICO

    if not robots_ok(a.url):
        print("BLOQUEADO_POLITICA: robots.txt")
        return POLITICA

    req = urllib.request.Request(a.url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            datos = r.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429):
            print(f"BLOQUEADO: HTTP {e.code}")
            return BLOQUEADO
        print(f"FALLO_TECNICO: HTTP {e.code}")
        return TECNICO
    except Exception as e:
        print(f"FALLO_TECNICO: {e}")
        return TECNICO

    if len(datos) > MAX_BYTES:
        print("FALLO_TECNICO: archivo demasiado grande")
        return TECNICO
    if not datos.startswith(b"%PDF"):
        print("FALLO_TECNICO: no es un PDF")
        return TECNICO

    nombre = pathlib.PurePosixPath(urlparse(a.url).path).name or "reporte.pdf"
    nombre = re.sub(r"[^\w.\- ]", "_", nombre)
    carpeta = pathlib.Path(f["carpeta"])
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / nombre
    if destino.exists():
        print(f"FALLO_TECNICO: ya existe {destino}. No se sobrescribe. Anotar en el changelog.")
        return TECNICO
    destino.write_bytes(datos)

    print(json.dumps({
        "metodo": "urllib",
        "fuente": a.fuente,
        "url": a.url,
        "archivo": str(destino),
        "sha256": hashlib.sha256(datos).hexdigest(),
        "bytes": len(datos),
        "fecha_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }, ensure_ascii=False))
    return OK


if __name__ == "__main__":
    sys.exit(main())
