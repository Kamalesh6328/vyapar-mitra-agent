# -*- coding: utf-8 -*-
from typing import Optional

def generate_stall_poster_svg(
    stall_name: str,
    tagline: str,
    location: str,
    operating_hours: str,
    upi_id: str,
    qr_base64: str,
    language: str = "marathi"
) -> str:
    slogans = {
        "marathi": {
            "title_sub": "ताजी आणि दर्जेदार फळे",
            "scan_pay": "UPI द्वारे पैसे देण्यासाठी स्कॅन करा",
            "tagline_def": "रोज ताजी फळे | योग्य भाव",
            "open_txt": "वेळ",
            "location_txt": "पत्ता"
        },
        "hindi": {
            "title_sub": "ताज़ा और शुद्ध फल",
            "scan_pay": "UPI से भुगतान के लिए स्कैन करें",
            "tagline_def": "रोज़ाना ताज़ा फल | सही दाम",
            "open_txt": "समय",
            "location_txt": "स्थान"
        },
        "english": {
            "title_sub": "100% Farm-Fresh Seasonal Fruits",
            "scan_pay": "Scan Here to Pay via UPI",
            "tagline_def": "Fresh Produce Daily | Honest Pricing",
            "open_txt": "Hours",
            "location_txt": "Location"
        }
    }
    texts = slogans.get(language.lower(), slogans["marathi"])
    tag = tagline if tagline else texts["tagline_def"]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1100" width="800" height="1100" style="font-family: Arial, Helvetica, sans-serif; background: #ffffff;">
  <!-- Outer Frame -->
  <rect x="20" y="20" width="760" height="1060" rx="28" fill="#f8fafc" stroke="#2563eb" stroke-width="8" />
  
  <!-- Header Banner -->
  <rect x="40" y="40" width="720" height="170" rx="20" fill="#1e40af" />
  <text x="400" y="110" font-size="40" font-weight="bold" fill="#ffffff" text-anchor="middle">{stall_name}</text>
  <text x="400" y="160" font-size="22" fill="#bfdbfe" text-anchor="middle">{texts['title_sub']} • {tag}</text>
  
  <!-- Fruits Icons -->
  <text x="400" y="255" font-size="44" text-anchor="middle">🍎 🍌 🥭 🍊 🍇 🥝 🍈</text>
  
  <!-- Location & Hours Box -->
  <rect x="80" y="285" width="640" height="120" rx="16" fill="#eff6ff" stroke="#93c5fd" stroke-width="2" />
  <text x="400" y="330" font-size="22" font-weight="bold" fill="#1e3a8a" text-anchor="middle">📍 {texts['location_txt']}: {location}</text>
  <text x="400" y="375" font-size="20" font-weight="600" fill="#047857" text-anchor="middle">⏰ {texts['open_txt']}: {operating_hours}</text>
  
  <!-- QR Frame -->
  <rect x="150" y="435" width="500" height="500" rx="24" fill="#ffffff" stroke="#cbd5e1" stroke-width="3" />
  <text x="400" y="480" font-size="24" font-weight="bold" fill="#0f172a" text-anchor="middle">💳 {texts['scan_pay']}</text>
  
  <!-- QR Image -->
  <image href="{qr_base64}" x="220" y="505" width="360" height="360" />
  
  <!-- UPI ID Box -->
  <rect x="200" y="875" width="400" height="42" rx="10" fill="#f1f5f9" />
  <text x="400" y="904" font-size="19" font-weight="600" fill="#334155" text-anchor="middle">UPI ID: {upi_id}</text>
  <text x="400" y="965" font-size="18" font-weight="bold" fill="#475569" text-anchor="middle">Google Pay | PhonePe | Paytm | BHIM UPI</text>
  
  <!-- Footer -->
  <text x="400" y="1035" font-size="14" fill="#94a3b8" text-anchor="middle">Powered by Vyapar Mitra AI • Digital Street Vendor Platform</text>
</svg>"""
    return svg