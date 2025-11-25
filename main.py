from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime

app = FastAPI()

API_KEY = "DEIN_API_KEY"  # <<-- später ersetzen


class FinancialPlanRequest(BaseModel):
    monatlicheMiete: float
    personalKosten: float
    produktEinkauf: float
    erwarteterUmsatz: float
    sonstigeAusgaben: float
    monat: Optional[str] = None


class FinancialPlanResponse(BaseModel):
    planId: str
    status: str
    gesamtKosten: float
    gewinn: float
    gewinnMargeProzent: float
    istProfitabel: bool
    erstelltAm: str


def check_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail={"fehlerCode": "UNAUTHORIZED", "nachricht": "Ungültiger API-Key"}
        )


@app.post("/financial-plan", response_model=FinancialPlanResponse)
def create_financial_plan(
    body: FinancialPlanRequest,
    x_api_key: Optional[str] = Header(None)
):
    check_key(x_api_key)

    gesamt = (
        body.monatlicheMiete
        + body.personalKosten
        + body.produktEinkauf
        + body.sonstigeAusgaben
    )

    gewinn = body.erwarteterUmsatz - gesamt
    marge = (gewinn / body.erwarteterUmsatz * 100) if body.erwarteterUmsatz > 0 else 0

    return FinancialPlanResponse(
        planId=str(uuid4()),
        status="erstellt",
        gesamtKosten=gesamt,
        gewinn=gewinn,
        gewinnMargeProzent=round(marge, 2),
        istProfitabel=gewinn > 0,
        erstelltAm=datetime.utcnow().isoformat() + "Z"
    )
