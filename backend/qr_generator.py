# -*- coding: utf-8 -*-
import base64
import urllib.parse
from io import BytesIO
from typing import Optional
import qrcode

def generate_upi_uri(upi_id: str, payee_name: str, amount: Optional[float] = None, note: Optional[str] = None) -> str:
    params = {
        "pa": upi_id.strip(),
        "pn": payee_name.strip(),
        "cu": "INR"
    }
    if amount and amount > 0:
        params["am"] = f"{amount:.2f}"
    if note:
        params["tn"] = note.strip()
    return "upi://pay?" + urllib.parse.urlencode(params)

def generate_upi_qr_base64(upi_id: str, payee_name: str, amount: Optional[float] = None, note: Optional[str] = None) -> str:
    uri = generate_upi_uri(upi_id, payee_name, amount, note)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="#ffffff")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"