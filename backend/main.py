# -*- coding: utf-8 -*-
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from .agent import VyaparMitraAgent
from .qr_generator import generate_upi_qr_base64
from .poster_generator import generate_stall_poster_svg
from .ondc_manager import generate_ondc_store_schema
from .schemes_application import generate_pmsvanidhi_application_kit

app = FastAPI(
    title="Vyapar Mitra AI Agent",
    description="Street Vendor Digitalization & Financial Inclusion Agent (Problem Statement 29)",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = VyaparMitraAgent()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    language: Optional[str] = None
    lang: Optional[str] = None
    signals: Optional[Dict[str, bool]] = None

class VendorProfileRequest(BaseModel):
    session_id: Optional[str] = "default"
    store_name: Optional[str] = None
    owner_name: Optional[str] = None
    category: Optional[str] = None
    specialities: Optional[str] = None
    location: Optional[str] = None
    operating_hours: Optional[str] = None
    upi_id: Optional[str] = None
    phone: Optional[str] = None
    agent_name: Optional[str] = None
    agent_tone: Optional[str] = None
    custom_discount_rule: Optional[str] = None
    daily_profit_goal: Optional[float] = None

class PMSVANidhiAppRequest(BaseModel):
    session_id: Optional[str] = "default"
    vendor_name: Optional[str] = "Ramesh Patil"
    mobile: Optional[str] = "+91 98765 43210"
    aadhaar_masked: Optional[str] = "XXXX-XXXX-9876"
    store_name: Optional[str] = "Camp Fresh Fruits"
    location: Optional[str] = "Camp, Pune"
    bank_account: Optional[str] = "1234567890"
    ifsc: Optional[str] = "SBIN0001234"
    vending_category: Optional[str] = "Fruit & Vegetable Vendor"
    tvc_recommendation_status: Optional[str] = "Certificate of Vending (CoV) Available"
    loan_tranche: Optional[int] = 1

class QRRequest(BaseModel):
    upi_id: str
    payee_name: str
    amount: Optional[float] = None
    note: Optional[str] = None

class PosterRequest(BaseModel):
    stall_name: str
    tagline: Optional[str] = ""
    location: str
    operating_hours: Optional[str] = "7:00 AM - 8:00 PM"
    upi_id: str
    language: Optional[str] = "marathi"

@app.get("/api/health")
async def health_check():
    return {"status": "online", "service": "Vyapar Mitra AI Agent", "version": "1.1.0"}

@app.get("/api/vendor/profile")
async def get_profile(session_id: str = "default"):
    return agent.get_vendor_profile(session_id)

@app.post("/api/vendor/profile")
async def update_profile(req: VendorProfileRequest):
    data = req.model_dump(exclude_unset=True)
    sid = data.pop("session_id", "default")
    updated = agent.update_vendor_profile(sid, data)
    return {"status": "success", "profile": updated}

@app.get("/api/reports/sales")
async def get_sales_report(period: str = "daily", session_id: str = "default"):
    ledger = agent.get_or_create_ledger(session_id)
    return ledger.get_periodic_report(period)

@app.get("/api/reports/export")
async def export_sales_report_csv(period: str = "all", session_id: str = "default"):
    ledger = agent.get_or_create_ledger(session_id)
    csv_data = ledger.export_csv(period)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=vyapar_mitra_{period}_sales_report.csv"}
    )

@app.post("/api/schemes/apply-pmsvanidhi")
async def apply_pmsvanidhi(req: PMSVANidhiAppRequest):
    prof = agent.get_vendor_profile(req.session_id or "default")
    app_kit = generate_pmsvanidhi_application_kit(
        vendor_name=req.vendor_name or prof.get("owner_name", "Ramesh Patil"),
        mobile=req.mobile or prof.get("phone", "+91 98765 43210"),
        aadhaar_masked=req.aadhaar_masked or "XXXX-XXXX-9876",
        store_name=req.store_name or prof.get("store_name", "Camp Fresh Fruits"),
        location=req.location or prof.get("location", "Camp, Pune"),
        bank_account=req.bank_account or "1234567890",
        ifsc=req.ifsc or "SBIN0001234",
        vending_category=req.vending_category or "Fruit & Vegetable Vendor",
        tvc_recommendation_status=req.tvc_recommendation_status or "Certificate of Vending (CoV) Available",
        loan_tranche=req.loan_tranche or 1
    )
    return app_kit

@app.get("/api/ondc/catalogue")
async def get_ondc_catalogue(session_id: str = "default"):
    prof = agent.get_vendor_profile(session_id)
    return generate_ondc_store_schema(
        store_name=prof.get("store_name", "Camp Fresh Fruits"),
        owner_name=prof.get("owner_name", "Ramesh Patil"),
        location=prof.get("location", "Camp, Pune"),
        phone=prof.get("phone", "+91 98765 43210"),
        upi_id=prof.get("upi_id", "campfruits@upi"),
        specialities=prof.get("specialities", "Fresh seasonal fruits"),
        operating_hours=prof.get("operating_hours", "7:00 AM - 8:00 PM")
    )

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        response = agent.process_message(
            message=req.message,
            session_id=req.session_id or "default",
            lang=req.lang or req.language or "marathi",
            signals=req.signals
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/onboard")
async def onboard_endpoint(req: ChatRequest):
    return agent.mode_1_onboarding_kit(req.message, req.lang or req.language or "marathi", req.session_id or "default")

@app.post("/api/score")
async def score_endpoint(req: ChatRequest):
    return agent.mode_2_digital_score(req.signals, req.session_id or "default", req.lang or req.language or "marathi")

@app.post("/api/ledger/transaction")
async def ledger_tx_endpoint(req: ChatRequest):
    return agent.mode_3_ledger_log(req.message, req.session_id or "default", req.lang or req.language or "marathi")

@app.get("/api/ledger/summary")
async def ledger_summary_endpoint(session_id: str = "default"):
    ledger = agent.get_or_create_ledger(session_id)
    return ledger.get_summary()

@app.get("/api/ledger/statement")
async def ledger_statement_endpoint(session_id: str = "default", vendor_name: str = "Camp Fresh Fruits"):
    ledger = agent.get_or_create_ledger(session_id)
    return ledger.generate_loan_statement(vendor_name)

@app.get("/api/schemes")
async def schemes_endpoint():
    return agent.rag.get_all_schemes()

@app.get("/api/market-insights")
async def market_insights_endpoint(city: str = "pune", product: str = "fruits", session_id: str = "default"):
    return agent.mode_4_market_insights(city, product, session_id)

@app.post("/api/qr/generate")
async def qr_generate_endpoint(req: QRRequest):
    qr_b64 = generate_upi_qr_base64(req.upi_id, req.payee_name, req.amount, req.note)
    return {"upi_id": req.upi_id, "qr_base64": qr_b64}

@app.post("/api/poster/generate")
async def poster_generate_endpoint(req: PosterRequest):
    qr_b64 = generate_upi_qr_base64(req.upi_id, req.stall_name)
    svg_data = generate_stall_poster_svg(
        stall_name=req.stall_name,
        tagline=req.tagline or "",
        location=req.location,
        operating_hours=req.operating_hours or "7:00 AM - 8:00 PM",
        upi_id=req.upi_id,
        qr_base64=qr_b64,
        language=req.language or "marathi"
    )
    return {"svg": svg_data, "qr_base64": qr_b64}

# Static file mount
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))