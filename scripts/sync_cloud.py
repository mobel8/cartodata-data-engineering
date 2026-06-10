"""Sync de la couche GOLD vers un bucket objet S3-compatible (Cloudflare R2 / S3).

Couche "cloud" honnête et minimale : on synchronise les Parquet GOLD vers un
stockage objet pour que l'artefact consommé par les autres modules du portfolio
soit aussi disponible dans le cloud. AUCUN cluster managé.

Activé uniquement si les credentials sont présents (variables d'environnement) :
  S3_BUCKET, S3_ENDPOINT_URL (R2), AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
Sinon : no-op tracé (le pipeline ne dépend jamais du cloud pour tourner).

Usage : py scripts/sync_cloud.py
"""

from __future__ import annotations

import os

from cartodata_de import config


def sync(bucket: str | None = None, prefix: str = "gold/") -> int:
    bucket = bucket or os.environ.get("S3_BUCKET")
    if not bucket:
        print("[sync_cloud] S3_BUCKET absent -> no-op (couche cloud désactivée).")
        return 0
    try:
        import boto3  # import paresseux : extra 'cloud'
    except ImportError:
        print("[sync_cloud] boto3 non installé (pip install -e '.[cloud]') -> no-op.")
        return 0

    files = sorted(config.GOLD.glob("*.parquet"))
    if not files:
        print("[sync_cloud] Aucun Parquet GOLD à synchroniser (lancez d'abord le pipeline).")
        return 0

    s3 = boto3.client("s3", endpoint_url=os.environ.get("S3_ENDPOINT_URL"))
    for f in files:
        s3.upload_file(str(f), bucket, f"{prefix}{f.name}")
    print(f"[sync_cloud] {len(files)} fichiers GOLD -> s3://{bucket}/{prefix}")
    return len(files)


if __name__ == "__main__":
    raise SystemExit(0 if sync() >= 0 else 1)
