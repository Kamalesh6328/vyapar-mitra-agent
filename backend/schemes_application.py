# -*- coding: utf-8 -*-
from typing import Dict, Any
from datetime import datetime

def generate_pmsvanidhi_application_kit(
    vendor_name: str,
    mobile: str,
    aadhaar_masked: str,
    store_name: str,
    location: str,
    bank_account: str,
    ifsc: str,
    vending_category: str = "Fruit & Vegetable Vendor",
    tvc_recommendation_status: str = "Certificate of Vending (CoV) Available",
    loan_tranche: int = 1
) -> Dict[str, Any]:
    tranche_info = {
        1: {"amount": "₹15,000", "tenure": "12 Months", "subsidy": "7% per annum interest subsidy"},
        2: {"amount": "₹25,000", "tenure": "18 Months", "subsidy": "7% per annum interest subsidy"},
        3: {"amount": "₹50,000", "tenure": "36 Months", "subsidy": "7% per annum interest subsidy"}
    }
    t_info = tranche_info.get(loan_tranche, tranche_info[1])

    return {
        "application_id": f"PMSV-PUNE-{datetime.now().strftime('%Y%m%d%H%M')}",
        "scheme_name": "PM SVANidhi (Pradhan Mantri Street Vendor's AtmaNirbhar Nidhi)",
        "official_portal": "https://pmsvanidhi.mohua.gov.in/",
        "loan_tranche": loan_tranche,
        "requested_amount": t_info["amount"],
        "tenure": t_info["tenure"],
        "interest_subsidy": t_info["subsidy"],
        "digital_cashback_benefit": "Monthly cashback up to ₹100 for eligible UPI transactions (₹1,200/year)",
        "applicant_profile": {
            "applicant_name": vendor_name,
            "business_name": store_name,
            "aadhaar_number": aadhaar_masked or "XXXX-XXXX-1234",
            "mobile_linked_aadhaar": mobile,
            "vending_activity": vending_category,
            "vending_location": location,
            "urban_local_body": "Pune Municipal Corporation (PMC)",
            "vending_status": tvc_recommendation_status,
            "disbursement_bank": {
                "account_number": bank_account or "XXXX-XXXX-5678",
                "ifsc_code": ifsc or "SBIN0001234"
            }
        },
        "required_documents_checklist": [
            {"doc": "Aadhaar Card with active mobile link", "status": "Ready"},
            {"doc": "Bank Passbook / Cancelled Cheque", "status": "Ready"},
            {"doc": "Certificate of Vending (CoV) / TVC Letter of Recommendation (LoR)", "status": tvc_recommendation_status},
            {"doc": "Self-Declaration of Street Vending", "status": "Ready"}
        ],
        "application_steps": [
            "1. Visit the official MoHUA PM SVANidhi portal: https://pmsvanidhi.mohua.gov.in/",
            "2. Click 'Apply for Loan (1st Tranche - ₹15,000)'.",
            "3. Enter your Aadhaar-linked mobile number and verify via OTP.",
            "4. Select Urban Local Body: 'Maharashtra -> Pune -> Pune Municipal Corporation (PMC)'.",
            "5. Select your Town Vending Committee (TVC) status or upload Letter of Recommendation (LoR).",
            "6. Provide Bank Account Number & IFSC code for direct DBT subsidy credits.",
            "7. Submit application online or visit your nearest Common Service Centre (CSC) with this printout for free biometric verification."
        ]
    }