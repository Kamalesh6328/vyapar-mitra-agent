# -*- coding: utf-8 -*-
import sys
import os
import uvicorn

if __name__ == "__main__":
    # Ensure project root is in sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print("=" * 60)
    print("🚀 Starting Vyapar Mitra AI Agent (व्यापार मित्र)")
    print("📍 Street Vendor Digitalization & Financial Inclusion Platform")
    print("🌐 Access Dashboard at: http://localhost:8000")
    print("=" * 60)

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)