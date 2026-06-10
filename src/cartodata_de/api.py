"""API FastAPI read-only sur la couche GOLD.

C'est l'interface par laquelle les AUTRES modules du portfolio (BI, ML, GenAI)
consomment le dataset GOLD : un seul producteur, plusieurs consommateurs.
Lecture seule -> aucun risque d'écriture concurrente sur le warehouse.

Lancer : uvicorn cartodata_de.api:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from cartodata_de import __version__, warehouse

app = FastAPI(
    title="CartoData IDF — GOLD API",
    version=__version__,
    description="Accès read-only au mart GOLD du marché de l'emploi Data/IA en Île-de-France.",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/kpis")
def kpis() -> dict:
    rows = warehouse.query("SELECT * FROM mart_kpis")
    if not rows:
        raise HTTPException(status_code=404, detail="mart_kpis vide — lancez le pipeline.")
    return rows[0]


@app.get("/marts")
def marts() -> dict:
    return {"marts": warehouse.list_marts()}


@app.get("/marts/{name}")
def mart(name: str) -> list[dict]:
    # Anti-injection : on n'autorise que les noms de marts réellement présents.
    if name not in warehouse.list_marts():
        raise HTTPException(status_code=404, detail=f"mart inconnu : {name}")
    return warehouse.query(f"SELECT * FROM {name}")


@app.get("/offres")
def offres(
    departement: str | None = Query(default=None),
    contract: str | None = Query(default=None),
    has_salary: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict]:
    clauses, params = [], []
    if departement:
        clauses.append("departement = ?")
        params.append(departement)
    if contract:
        clauses.append("contract = ?")
        params.append(contract)
    if has_salary is not None:
        clauses.append("has_salary = ?")
        params.append(has_salary)
    sql = (
        "SELECT source, title, company, city, departement, contract, remote, "
        "sal_min_eur, sal_max_eur, has_salary, url FROM fct_offres"
    )
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += f" LIMIT {int(limit)}"
    return warehouse.query(sql, params)
