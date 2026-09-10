# -*- coding: utf-8 -*-
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app
from backend.agent import VyaparMitraAgent
from backend.rag_engine import RAGKnowledgeRetriever
from backend.ledger import MicroLedger
from backend.qr_generator import generate_upi_uri, generate_upi_qr_base64
from backend.poster_generator import generate_stall_poster_svg
from backend.ondc_manager import generate_ondc_store_schema
from backend.schemes_application import generate_pmsvanidhi_application_kit

client = TestClient(app)

def test_rag_knowledge_base():
    rag = RAGKnowledgeRetriever()
    schemes = rag.get_all_schemes()
    assert len(schemes) >= 2
    svanidhi = rag.get_scheme_by_id("pm_svanidhi")
    assert svanidhi is not None
    assert "₹15,000" in svanidhi["tranches"][0]["amount"]
    assert "7%" in svanidhi["financial_benefits"]["interest_subsidy"]

def test_multi_period_reports():
    ledger = MicroLedger()
    # Test daily, weekly, monthly, yearly
    d = ledger.get_periodic_report("daily")
    assert d["period"] == "Daily"
    assert len(d["chart_labels"]) == 3

    w = ledger.get_periodic_report("weekly")
    assert w["period"] == "Weekly"
    assert len(w["chart_labels"]) == 7
    assert w["total_income"] > 0

    m = ledger.get_periodic_report("monthly")
    assert m["period"] == "Monthly"
    assert len(m["chart_labels"]) == 4

    y = ledger.get_periodic_report("yearly")
    assert y["period"] == "Yearly"
    assert len(y["chart_labels"]) == 4

def test_pmsvanidhi_application():
    app_kit = generate_pmsvanidhi_application_kit(
        vendor_name="Ramesh Patil",
        mobile="+91 98765 43210",
        aadhaar_masked="XXXX-XXXX-9876",
        store_name="Camp Fresh Fruits",
        location="Camp, Pune",
        bank_account="1234567890",
        ifsc="SBIN0001234",
        loan_tranche=1
    )
    assert app_kit["loan_tranche"] == 1
    assert app_kit["requested_amount"] == "₹15,000"
    assert "7%" in app_kit["interest_subsidy"]
    assert len(app_kit["required_documents_checklist"]) >= 4

def test_ondc_store_catalogue():
    schema = generate_ondc_store_schema(
        store_name="Camp Fresh Fruits",
        owner_name="Ramesh Patil",
        location="Camp, Pune",
        phone="+91 98765 43210",
        upi_id="campfruits@upi",
        specialities="Bananas, Apples, Mangoes",
        operating_hours="7AM-8PM"
    )
    catalog = schema["message"]["catalog"]
    assert catalog["bpp/descriptor"]["name"] == "Camp Fresh Fruits"
    providers = catalog["bpp/providers"]
    assert len(providers) > 0
    assert len(providers[0]["items"]) >= 6

def test_api_endpoints():
    # Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200

    # Sales report
    res_rep = client.get("/api/reports/sales?period=weekly")
    assert res_rep.status_code == 200
    assert res_rep.json()["period"] == "Weekly"

    # Export report CSV
    res_csv = client.get("/api/reports/export?period=weekly")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]

    # PM SVANidhi Application API
    res_loan = client.post("/api/schemes/apply-pmsvanidhi", json={
        "vendor_name": "Ramesh Patil",
        "mobile": "+91 98765 43210"
    })
    assert res_loan.status_code == 200
    assert res_loan.json()["requested_amount"] == "₹15,000"

    # ONDC Catalogue API
    res_ondc = client.get("/api/ondc/catalogue")
    assert res_ondc.status_code == 200
    assert "bpp/providers" in res_ondc.json()["message"]["catalog"]

def test_multilingual_marathi_hindi_support():
    ledger = MicroLedger()
    # Test Marathi natural language input with Devanagari numerals
    mr_text = "आज केळी विकली ₹५०० आणि चहा खर्च ₹८०"
    mr_parsed = ledger.parse_natural_language(mr_text)
    assert len(mr_parsed) == 2
    assert mr_parsed[0]["amount"] == 500.0
    assert mr_parsed[0]["type"] == "income"
    assert mr_parsed[1]["amount"] == 80.0
    assert mr_parsed[1]["type"] == "expense"

    # Test Hindi natural language input with Devanagari numerals
    hi_text = "आज सेब बेचे ₹७०० और किराया खर्च ₹१५०"
    hi_parsed = ledger.parse_natural_language(hi_text)
    assert len(hi_parsed) == 2
    assert hi_parsed[0]["amount"] == 700.0
    assert hi_parsed[0]["type"] == "income"
    assert hi_parsed[1]["amount"] == 150.0
    assert hi_parsed[1]["type"] == "expense"

    # Test Agent Multilingual responses
    agent = VyaparMitraAgent()
    
    # Marathi Loan Query
    mr_loan_res = agent.process_message("मला पीएम स्वनिधी कर्ज हवे आहे", lang="mr")
    assert mr_loan_res["intent"] == "mode_loan"
    assert "पीएम स्वनिधी" in mr_loan_res["reply_text"]

    # Hindi Mandi Rate Query
    hi_mandi_res = agent.process_message("आज का मंडी भाव क्या है?", lang="hi")
    assert hi_mandi_res["intent"] == "mode_4_market"
    assert "मंडी" in hi_mandi_res["reply_text"] or "बाजार" in hi_mandi_res["reply_text"]

    # Marathi Ledger Recording
    mr_rec_res = agent.process_message("आज सफरचंद विकले ५००", lang="mr")
    assert mr_rec_res["intent"] == "mode_3_ledger"
    assert "नोंदवले" in mr_rec_res["reply_text"] or "हिशोब" in mr_rec_res["reply_text"]

def test_chat_multilingual_api():
    # Test /api/chat with Marathi
    res_mr = client.post("/api/chat", json={
        "message": "मला दुकान ओएनडीसी वर नोंदवायचे आहे",
        "lang": "mr"
    })
    assert res_mr.status_code == 200
    data_mr = res_mr.json()
    assert data_mr["intent"] == "mode_ondc"
    assert "ONDC" in data_mr["reply_text"] or "कॅटलॉग" in data_mr["reply_text"]

    # Test /api/chat with Hindi
    res_hi = client.post("/api/chat", json={
        "message": "मेरा क्रेडिट स्कोर चेक करो",
        "lang": "hi"
    })
    assert res_hi.status_code == 200
    data_hi = res_hi.json()
    assert data_hi["intent"] == "mode_2_score"
    assert "स्कोर" in data_hi["reply_text"]