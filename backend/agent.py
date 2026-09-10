# -*- coding: utf-8 -*-
import re
from typing import Dict, Any, List, Optional
from .rag_engine import RAGKnowledgeRetriever
from .ledger import MicroLedger
from .qr_generator import generate_upi_qr_base64
from .poster_generator import generate_stall_poster_svg
from .ondc_manager import generate_ondc_store_schema
from .schemes_application import generate_pmsvanidhi_application_kit

class VyaparMitraAgent:
    def __init__(self):
        self.rag = RAGKnowledgeRetriever()
        self.ledgers: Dict[str, MicroLedger] = {}
        self.vendor_profiles: Dict[str, Dict[str, Any]] = {}

    def _normalize_lang(self, lang: Optional[str]) -> str:
        if not lang:
            return "marathi"
        l = lang.lower().strip()
        if l in ["mr", "marathi", "mr-in"]:
            return "marathi"
        elif l in ["hi", "hindi", "hi-in"]:
            return "hindi"
        else:
            return "english"

    def get_or_create_ledger(self, session_id: str = "default") -> MicroLedger:
        if session_id not in self.ledgers:
            self.ledgers[session_id] = MicroLedger()
        return self.ledgers[session_id]

    def get_vendor_profile(self, session_id: str = "default") -> Dict[str, Any]:
        if session_id not in self.vendor_profiles:
            self.vendor_profiles[session_id] = {
                "store_name": "Camp Fresh Fruits",
                "owner_name": "Ramesh Patil",
                "category": "Fresh Fruits & Seasonal Specials",
                "specialities": "Bananas, Apples, Seasonal Alphonso Mangoes, Papayas, Pomegranates",
                "location": "Near Main Market Road & MG Road, Camp, Pune",
                "operating_hours": "7:00 AM - 8:00 PM",
                "upi_id": "campfruits@upi",
                "phone": "+91 98765 43210",
                "agent_name": "Vyapar Mitra (व्यापार मित्र)",
                "agent_tone": "warm",
                "custom_discount_rule": "10% off on ripe fruits after 6:30 PM",
                "daily_profit_goal": 1000.0
            }
        return self.vendor_profiles[session_id]

    def update_vendor_profile(self, session_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        curr = self.get_vendor_profile(session_id)
        curr.update({k: v for k, v in profile_data.items() if v is not None and v != ""})
        self.vendor_profiles[session_id] = curr
        return curr

    def classify_intent(self, text: str) -> str:
        t = text.lower()
        # Normalize Devanagari digits if present
        devanagari_digits = str.maketrans("०१२३४५६७८९", "0123456789")
        t = t.translate(devanagari_digits)

        loan_words = [
            "pm svanidhi", "loan", "apply for loan", "15000", "subsidy", "svanidhi", "scheme application", "loan application",
            "स्वनिधी", "कर्ज", "कर्ज अर्ज", "अनुदान", "योजना", "स्वनिधि", "ऋण", "ऋण आवेदन", "सब्सिडी", "लोन", "pmsvanidhi"
        ]
        ondc_words = [
            "ondc", "catalogue", "catalog", "online store", "open commerce", "beckn",
            "ओएनडीसी", "कॅटलॉग", "कैटलॉग", "ऑनलाइन दुकान", "ई-कॉमर्स", "उत्पादने सूची", "दुकान सूची", "उत्पाद सूची"
        ]
        report_words = [
            "sales report", "weekly report", "monthly report", "yearly report", "financial report", "p&l report", "report", "ledger summary",
            "विक्री अहवाल", "हिशोब", "अहवाल", "आठवड्याचा अहवाल", "महिन्याचा अहवाल", "नफा तोटा", "नफा अहवाल",
            "बिक्री रिपोर्ट", "हिसाब", "रिपोर्ट", "साप्ताहिक रिपोर्ट", "मासिक रिपोर्ट", "मुनाफा रिपोर्ट", "बिक्री विवरण"
        ]
        maps_words = [
            "google maps", "maps", "location", "local seo", "directions", "stall pin", "where is",
            "गुगल मॅप्स", "मॅप्स", "पत्ता", "स्थान", "लोकेशन", "गाडी पिन", "गूगल मैप्स", "दिशा", "दुकान का पता"
        ]
        poster_words = [
            "qr code", "poster", "banner", "stall poster", "standee", "qr", "print",
            "क्यूआर", "क्यूआर कोड", "पोस्टर", "बॅनर", "स्टॅन्डी", "फलक", "प्रिंट", "बैनर", "स्टैंडी"
        ]
        score_words = [
            "how am i doing", "my score", "digital score", "readiness score", "score", "credit score", "credit", "readiness",
            "माझा स्कोअर", "डिजिटल स्कोअर", "स्कोअर", "गुण", "प्रगती", "क्रेडिट स्कोअर", "क्रेडिट",
            "मेरा स्कोर", "डिजिटल स्कोर", "स्कोर", "अंक", "प्रगति", "क्रेडिट स्कोर"
        ]
        ledger_words = [
            "sold", "spent", "bought", "kharch", "diye", "bika", "kamaya", "rupees of", "transaction",
            "विकले", "विकली", "विकला", "खर्च", "दिले", "मिळाले", "कमावले", "रुपयांची", "रुपये", "घेतले", "आणले",
            "बेचे", "बेचा", "बेची", "दिए", "मिले", "कमाए", "रुपए", "खरीदा", "खरीदे", "लाए"
        ]
        mandi_words = [
            "mandi", "wholesale", "competitor", "market price", "selling time", "footfall", "demand", "price", "apmc",
            "मंडी", "घाऊक", "बाजार भाव", "दर", "भाव", "गुलटेकडी", "विक्री वेळ", "थोक भाव", "दाम", "बिक्री समय"
        ]
        whatsapp_words = [
            "whatsapp", "wa format", "send to whatsapp", "wa message", "broadcast",
            "व्हॉट्सॲप", "व्हॉट्सअॅप", "संदेश", "प्रचार संदेश", "व्हाट्सएप", "व्हाट्सऐप", "प्रचार"
        ]
        profile_words = [
            "store profile", "my profile", "settings", "store details", "personalise", "customize",
            "माझे दुकान", "प्रोफाइल", "माहिती", "सेटिंग्ज", "मेरी दुकान", "सेटिंग्स"
        ]

        if any(w in t for w in loan_words):
            return "mode_loan"
        elif any(w in t for w in ondc_words):
            return "mode_ondc"
        elif any(w in t for w in report_words):
            return "mode_reports"
        elif any(w in t for w in maps_words):
            return "mode_maps"
        elif any(w in t for w in poster_words):
            return "mode_poster"
        elif any(w in t for w in score_words):
            return "mode_2_score"
        elif any(w in t for w in ledger_words):
            return "mode_3_ledger"
        elif any(w in t for w in mandi_words):
            return "mode_4_market"
        elif any(w in t for w in whatsapp_words):
            return "mode_5_whatsapp"
        elif any(w in t for w in profile_words):
            return "mode_profile"
        else:
            return "mode_1_onboarding"

    def mode_1_onboarding_kit(self, business_desc: str, lang: str = "marathi", session_id: str = "default") -> Dict[str, Any]:
        lang = self._normalize_lang(lang)
        profile = self.get_vendor_profile(session_id)
        stall_name = profile.get("store_name", "Camp Fresh Fruits")
        location = profile.get("location", "Near Main Market Road & MG Road, Camp, Pune")
        hours = profile.get("operating_hours", "7:00 AM - 8:00 PM")
        upi_id = profile.get("upi_id", "campfruits@upi")
        owner = profile.get("owner_name", "Ramesh Patil")
        specialities = profile.get("specialities", "Bananas, Apples, Mangoes, Papayas")
        custom_offer = profile.get("custom_discount_rule", "10% off on ripe fruits after 6:30 PM")

        business_profile = {
            "suggested_name": stall_name,
            "owner_name": owner,
            "tagline": f"100% Farm-Fresh Produce Daily • Managed by {owner}",
            "category": profile.get("category", "Fresh Fruit Stall / Micro-Vendor"),
            "description": f"Located at {location}, {stall_name} offers premium fresh, handpicked produce ({specialities}) daily from {hours}. Serving local residents and commuters with trusted quality for over 5 years."
        }

        pricing_tips = [
            "Morning Commuter Combos: Bundle 2 bananas + 1 apple for a flat round figure (e.g. ₹40) for swift cash-free UPI checkout.",
            f"Store Custom Offer: {custom_offer} to clear perishable inventory before closing.",
            "Dynamic Seasonal Margins: Keep everyday staple fruits at steady competitive rates while adjusting peak seasonal items (like mangoes) to morning APMC wholesale rates."
        ]

        fintech = self.rag.get_fintech_info()
        upi_setup = {
            "recommended_apps": [a["name"] for a in fintech.get("upi_apps", [])],
            "required_documents": [
                "Aadhaar Card",
                "Bank Account details & IFSC code (or Bank Passbook)",
                "Mobile number linked to Bank Account"
            ],
            "steps": fintech.get("qr_setup_steps", []),
            "kyc_note": "Please note: In-app digital KYC is securely completed directly by the vendor inside the chosen merchant app."
        }

        platforms = self.rag.get_platforms()
        schemes = self.rag.get_all_schemes()
        disclaimer = "Please verify current scheme details on pmsvanidhi.mohua.gov.in before applying."

        marathi_caption = f"🍎 {stall_name} ({location}) येथे रोज ताजी व उत्तम दर्जाची फळे! {specialities} उपलब्ध. 📍 {location} | ⏰ {hours} | 💳 UPI ID: {upi_id} आणि रोख स्वीकारले जाते! ({custom_offer})"
        hindi_caption = f"🍎 {stall_name} ({location}) में रोज़ाना ताज़ा और शुद्ध फल! {specialities}। 📍 {location} | ⏰ {hours} | 💳 UPI ID: {upi_id} और कैश स्वीकार्य! ({custom_offer})"
        english_caption = f"🍎 Fresh Seasonal Fruits at {stall_name}! {specialities} daily. 📍 {location} | ⏰ {hours} | 💳 UPI: {upi_id} & Cash Accepted! Special Offer: {custom_offer}"
        
        poster_text = f"{stall_name.upper()}\n ताजी आणि दर्जेदार फळे \n🍎 {specialities}\n📍 {location}\n⏰ Open Daily: {hours}\n[ SCAN QR CODE TO PAY VIA UPI: {upi_id} ]"

        qr_base64 = generate_upi_qr_base64(upi_id, stall_name)
        poster_svg = generate_stall_poster_svg(stall_name, business_profile["tagline"], location, hours, upi_id, qr_base64, lang)

        return {
            "mode": 1,
            "mode_name": "Digital Onboarding Kit",
            "business_profile": business_profile,
            "pricing_tips": pricing_tips,
            "upi_setup": upi_setup,
            "online_platforms": platforms,
            "msme_schemes": schemes,
            "scheme_disclaimer": disclaimer,
            "promotional_material": {
                "english_caption": english_caption,
                "local_translation": marathi_caption if lang == "marathi" else (hindi_caption if lang == "hindi" else english_caption),
                "language": lang,
                "poster_text": poster_text,
                "qr_base64": qr_base64,
                "poster_svg": poster_svg,
                "upi_id": upi_id
            }
        }

    def mode_2_digital_score(self, signals: Optional[Dict[str, bool]] = None, session_id: str = "default", lang: str = "marathi") -> Dict[str, Any]:
        lang = self._normalize_lang(lang)
        profile = self.get_vendor_profile(session_id)
        if signals is None:
            signals = {"upi_set_up": bool(profile.get("upi_id")), "google_maps_listed": True, "ondc_listed": True, "scheme_registered": False}
        
        score = 0
        breakdown = []
        if signals.get("upi_set_up"):
            score += 25
            breakdown.append({"item": f"UPI Payment Setup ({profile.get('upi_id', 'Active')})", "points": 25, "status": "Completed"})
        else:
            breakdown.append({"item": "UPI & QR Code Payment Setup", "points": 0, "status": "Pending"})

        if signals.get("google_maps_listed"):
            score += 25
            breakdown.append({"item": f"Google Maps & Business Profile ({profile.get('store_name', 'Listed')})", "points": 25, "status": "Completed"})
        else:
            breakdown.append({"item": "Google Maps & Business Profile", "points": 0, "status": "Pending"})

        if signals.get("ondc_listed"):
            score += 25
            breakdown.append({"item": "ONDC / Online Delivery Catalogue", "points": 25, "status": "Completed"})
        else:
            breakdown.append({"item": "ONDC / Online Delivery Listing", "points": 0, "status": "Pending"})

        if signals.get("scheme_registered"):
            score += 25
            breakdown.append({"item": "PM SVANidhi / Udyam Assist Formalization", "points": 25, "status": "Completed"})
        else:
            breakdown.append({"item": "PM SVANidhi / Udyam Assist Formalization", "points": 0, "status": "Pending"})

        if lang == "marathi":
            badge = "डिजिटल एक्सप्लोरर" if score < 25 else ("डिजिटल स्टार्टर" if score <= 50 else ("डिजिटल ग्रोथ लीडर" if score <= 75 else "डिजिटल चॅम्पियन"))
        elif lang == "hindi":
            badge = "डिजिटल एक्सप्लोरर" if score < 25 else ("डिजिटल स्टार्टर" if score <= 50 else ("डिजिटल ग्रोथ लीडर" if score <= 75 else "डिजिटल चैंपियन"))
        else:
            badge = "Digital Explorer" if score < 25 else ("Digital Starter" if score <= 50 else ("Digital Growth Leader" if score <= 75 else "Digital Champion"))

        ranked_actions = []
        if not signals.get("scheme_registered"):
            if lang == "marathi":
                ranked_actions.append("१. पीएम स्वनिधी योजनेअंतर्गत ₹१५,००० च्या पहिल्या हप्त्यासाठी तात्काळ अर्ज करा (+२५ गुण).")
            elif lang == "hindi":
                ranked_actions.append("1. पीएम स्वनिधि योजना के तहत ₹15,000 की पहली किश्त के लिए तुरंत आवेदन करें (+25 अंक)।")
            else:
                ranked_actions.append("1. Apply for PM SVANidhi 1st tranche loan (up to ₹15,000) for full formalization (+25 pts).")
        if not signals.get("ondc_listed"):
            if lang == "marathi":
                ranked_actions.append("२. ओएनडीसी (ONDC) डिजिटल कॅटलॉग सक्रिय करा (+२५ गुण).")
            elif lang == "hindi":
                ranked_actions.append("2. ओएनडीसी (ONDC) डिजिटल कैटलॉग सक्रिय करें (+25 अंक)।")
            else:
                ranked_actions.append("2. List your fruit prices on an ONDC seller partner app (+25 pts).")
        if not signals.get("google_maps_listed"):
            if lang == "marathi":
                ranked_actions.append(f"३. गुगल मॅप्सवर {profile.get('store_name')} चे स्थान जोडा (+२५ गुण).")
            elif lang == "hindi":
                ranked_actions.append(f"3. गूगल मैप्स पर {profile.get('store_name')} का स्थान जोड़ें (+25 अंक)।")
            else:
                ranked_actions.append(f"3. Add {profile.get('store_name')} to Google Maps with opening hours (+25 pts).")
        if not signals.get("upi_set_up"):
            if lang == "marathi":
                ranked_actions.append("४. UPI QR कोड पेमेंट सक्रिय करा (+२५ गुण).")
            elif lang == "hindi":
                ranked_actions.append("4. UPI QR कोड पेमेंट सक्रिय करें (+25 अंक)।")
            else:
                ranked_actions.append("4. Set up UPI QR code payment for digital transactions (+25 pts).")

        return {
            "mode": 2,
            "mode_name": "Digital Readiness Score",
            "score": score,
            "max_score": 100,
            "badge": badge,
            "breakdown": breakdown,
            "next_actions": ranked_actions[:3] if ranked_actions else (["डिजिटल व्यवहार कायम ठेवा!" if lang == "marathi" else ("डिजिटल लेन-देन जारी रखें!" if lang == "hindi" else "Maintain 100% digital transactions!")]),
            "store_name": profile.get("store_name", "Camp Fresh Fruits")
        }

    def mode_3_ledger_log(self, text: str, session_id: str = "default", lang: str = "marathi") -> Dict[str, Any]:
        lang = self._normalize_lang(lang)
        profile = self.get_vendor_profile(session_id)
        ledger = self.get_or_create_ledger(session_id)
        added = ledger.parse_natural_language(text)
        summary = ledger.get_summary()

        daily_goal = profile.get("daily_profit_goal", 1000.0)
        goal_progress_pct = round((summary['net_profit'] / daily_goal) * 100, 1) if daily_goal > 0 else 0.0

        if lang == "marathi":
            if added:
                confirmation = f"✅ **{profile.get('store_name')}** साठी {len(added)} व्यवहार यशस्वीरीत्या नोंदवले. आजची एकूण विक्री: ₹{summary['total_income']}, खर्च: ₹{summary['total_expense']}, निव्वळ नफा: ₹{summary['net_profit']} (दैनंदिन ध्येयाच्या {goal_progress_pct}% पूर्ण)."
            else:
                confirmation = f"📊 **{profile.get('store_name')}** चे हिशोब: एकूण विक्री: ₹{summary['total_income']}, खर्च: ₹{summary['total_expense']}, निव्वळ नफा: ₹{summary['net_profit']}."
        elif lang == "hindi":
            if added:
                confirmation = f"✅ **{profile.get('store_name')}** के लिए {len(added)} लेन-देन सफलतापूर्वक दर्ज किए गए। आज की कुल बिक्री: ₹{summary['total_income']}, खर्च: ₹{summary['total_expense']}, शुद्ध लाभ: ₹{summary['net_profit']} (दैनिक लक्ष्य का {goal_progress_pct}% पूर्ण)।"
            else:
                confirmation = f"📊 **{profile.get('store_name')}** का हिसाब: कुल बिक्री: ₹{summary['total_income']}, खर्च: ₹{summary['total_expense']}, शुद्ध लाभ: ₹{summary['net_profit']}."
        else:
            if added:
                confirmation = f"✅ Logged {len(added)} transaction(s) for **{profile.get('store_name')}**. Today's Sales: ₹{summary['total_income']}, Expenses: ₹{summary['total_expense']}, Net Profit: ₹{summary['net_profit']} ({goal_progress_pct}% of daily goal)."
            else:
                confirmation = f"📊 Current Ledger for **{profile.get('store_name')}**: Total Sales: ₹{summary['total_income']}, Expenses: ₹{summary['total_expense']}, Net Profit: ₹{summary['net_profit']}."

        credit_statement = ledger.generate_loan_statement(f"{profile.get('store_name')} (Owner: {profile.get('owner_name')})")

        return {
            "mode": 3,
            "mode_name": "Micro-Accounting Ledger",
            "confirmation": confirmation,
            "added_entries": added,
            "summary": summary,
            "daily_goal": daily_goal,
            "goal_progress_pct": goal_progress_pct,
            "credit_statement": credit_statement,
            "csv_export": ledger.export_csv()
        }

    def mode_4_market_insights(self, city: str = "pune", product: str = "fruits", session_id: str = "default", lang: str = "marathi") -> Dict[str, Any]:
        lang = self._normalize_lang(lang)
        profile = self.get_vendor_profile(session_id)
        mandi_data = self.rag.get_mandi_data(city)
        footfall = self.rag.get_footfall_insights(city, "camp_mg_road")
        
        if lang == "marathi":
            advice = f"**{profile.get('store_name')}** साठी सल्ला: कृषी उत्पन्न बाजार समिती (APMC गुलटेकडी) येथून पहाटे ताजी फळे घाऊक भावात खरेदी करा. सकाळी ७:३०-१०:३० व संध्याकाळी ५:३०-८:३० या गर्दीच्या वेळेत जलद UPI पेमेंट वापरा."
        elif lang == "hindi":
            advice = f"**{profile.get('store_name')}** के लिए सुझाव: एपीएमसी गुलटेकड़ी मंडी से सुबह ताज़ा फल थोक भाव पर खरीदें। सुबह 7:30-10:30 और शाम 5:30-8:30 बिक्री के पीक समय पर UPI पेमेंट का उपयोग करें।"
        else:
            advice = f"Tailored for **{profile.get('store_name')}**: Buy fresh produce ({profile.get('specialities', 'fruits')}) in early morning batches at APMC Gultekdi. Adjust pricing during morning and evening rush hours."

        return {
            "mode": 4,
            "mode_name": "Hyperlocal Demand & Mandi Intelligence",
            "city": city.title(),
            "store_name": profile.get("store_name", "Camp Fresh Fruits"),
            "wholesale_mandi": mandi_data.get("wholesale_mandi", "APMC Mandi"),
            "commodities": mandi_data.get("commodities", {}),
            "peak_footfall": footfall,
            "advice": advice
        }

    def mode_5_whatsapp_format(self, data: Any, session_id: str = "default", lang: str = "marathi") -> str:
        lang = self._normalize_lang(lang)
        profile = self.get_vendor_profile(session_id)
        name = profile.get("store_name", "Camp Fresh Fruits")
        owner = profile.get("owner_name", "Ramesh Patil")
        phone = profile.get("phone", "+91 98765 43210")
        upi = profile.get("upi_id", "campfruits@upi")
        offer = profile.get("custom_discount_rule", "Fresh quality fruits at best prices")

        if lang == "marathi":
            return (
                f"🌟 *{name}* (मालक: {owner}) 🌟\n"
                f"📍 स्थान: {profile.get('location')}\n"
                f"⏰ वेळ: {profile.get('operating_hours')}\n\n"
                f"🍎 *खास ऑफर:* {offer}\n\n"
                f"💳 *UPI द्वारे पैसे द्या:* `{upi}`\n"
                f"📞 *ऑर्डर / संपर्क:* {phone}\n\n"
                f"🏛️ *सरकारी योजना लाभ (PM SVANidhi):*\n"
                f"७% व्याज अनुदानासह ₹१५,००० पर्यंत विनातारण कर्ज उपलब्ध.\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"👉 *१ दाबा:* किंमत आणि नफा टिप्स\n"
                f"👉 *२ दाबा:* UPI QR कोड व स्टँडी\n"
                f"👉 *३ दाबा:* पीएम स्वनिधी कर्ज अर्ज\n"
                f"👉 *४ दाबा:* पुणे मंडी आजचे भाव"
            )
        elif lang == "hindi":
            return (
                f"🌟 *{name}* (मालिक: {owner}) 🌟\n"
                f"📍 स्थान: {profile.get('location')}\n"
                f"⏰ समय: {profile.get('operating_hours')}\n\n"
                f"🍎 *विशेष ऑफर:* {offer}\n\n"
                f"💳 *UPI द्वारा भुगतान करें:* `{upi}`\n"
                f"📞 *ऑर्डर / संपर्क:* {phone}\n\n"
                f"🏛️ *सरकारी योजना लाभ (PM SVANidhi):*\n"
                f"7% ब्याज सब्सिडी के साथ ₹15,000 तक बिना गारंटी ऋण उपलब्ध।\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"👉 *1 दबाएं:* मूल्य और लाभ टिप्स\n"
                f"👉 *2 दबाएं:* UPI QR कोड और स्टैंडी\n"
                f"👉 *3 दबाएं:* पीएम स्वनिधि ऋण आवेदन\n"
                f"👉 *4 दबाएं:* पुणे मंडी आज के भाव"
            )
        else:
            return (
                f"🌟 *{name}* (Owner: {owner}) 🌟\n"
                f"📍 {profile.get('location')}\n"
                f"⏰ {profile.get('operating_hours')}\n\n"
                f"🍎 *Special Offer:* {offer}\n\n"
                f"💳 *Pay via UPI:* `{upi}`\n"
                f"📞 *Order / Enquiry:* {phone}\n\n"
                f"1️⃣ *Government Scheme Matched (PM SVANidhi):*\n"
                f"Up to ₹15,000 collateral-free credit with 7% interest subsidy.\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"👉 *Reply 1 for Pricing Tips*\n"
                f"👉 *Reply 2 for UPI QR Setup*\n"
                f"👉 *Reply 3 for Loan Schemes*\n"
                f"👉 *Reply 4 for Mandi Rates*"
            )

    def process_message(self, message: str, session_id: str = "default", lang: str = "marathi", signals: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        lang = self._normalize_lang(lang)
        intent = self.classify_intent(message)
        profile = self.get_vendor_profile(session_id)
        
        if intent == "mode_loan":
            app_kit = generate_pmsvanidhi_application_kit(
                vendor_name=profile.get("owner_name", "Ramesh Patil"),
                mobile=profile.get("phone", "+91 98765 43210"),
                aadhaar_masked="XXXX-XXXX-9876",
                store_name=profile.get("store_name", "Camp Fresh Fruits"),
                location=profile.get("location", "Camp, Pune"),
                bank_account="1234567890",
                ifsc="SBIN0001234",
                loan_tranche=1
            )
            if lang == "marathi":
                reply = f"🏛️ **{profile.get('owner_name')}** यांच्यासाठी **पीएम स्वनिधी १ला हप्ता कर्ज अर्ज किट (₹१५,००० - ७% व्याज अनुदानासह)** तयार केले आहे. खालील कागदपत्रे तपासा व अधिकृत पोर्टलवर सबमिट करा."
            elif lang == "hindi":
                reply = f"🏛️ **{profile.get('owner_name')}** के लिए **पीएम स्वनिधि पहली किश्त ऋण आवेदन किट (₹15,000 - 7% ब्याज सब्सिडी)** तैयार की गई है। आवश्यक दस्तावेज जांचें और आधिकारिक पोर्टल पर जमा करें।"
            else:
                reply = f"🏛️ Generated official **PM SVANidhi 1st Tranche Loan Application Kit (₹15,000 with 7% interest subsidy)** for **{profile.get('owner_name')}**."

            return {
                "intent": intent,
                "mode": "loan",
                "mode_name": "PM SVANidhi Loan Application",
                "application_kit": app_kit,
                "reply_text": reply
            }
        elif intent == "mode_ondc":
            schema = generate_ondc_store_schema(
                store_name=profile.get("store_name", "Camp Fresh Fruits"),
                owner_name=profile.get("owner_name", "Ramesh Patil"),
                location=profile.get("location", "Camp, Pune"),
                phone=profile.get("phone", "+91 98765 43210"),
                upi_id=profile.get("upi_id", "campfruits@upi"),
                specialities=profile.get("specialities", "Fresh seasonal fruits"),
                operating_hours=profile.get("operating_hours", "7:00 AM - 8:00 PM")
            )
            if lang == "marathi":
                reply = f"🌐 **{profile.get('store_name')}** साठी बेकन प्रोटोकॉल अनुरूप **ONDC डिजिटल कॅटलॉग** तयार केला आहे. सर्व उत्पादनांचे थेट UPI पेमेंट जोडले आहे."
            elif lang == "hindi":
                reply = f"🌐 **{profile.get('store_name')}** के लिए बेकन प्रोटोकॉल आधारित **ONDC डिजिटल स्टोर कैटलॉग** तैयार है। उत्पाद सूची और UPI पेमेंट सक्रिय है।"
            else:
                reply = f"🌐 Created Beckn-compliant **ONDC Retail Catalogue** for **{profile.get('store_name')}** with active products and UPI payment routing."

            return {
                "intent": intent,
                "mode": "ondc",
                "mode_name": "ONDC Digital Store Catalogue",
                "ondc_schema": schema,
                "reply_text": reply
            }
        elif intent == "mode_reports":
            ledger = self.get_or_create_ledger(session_id)
            period = "weekly" if any(w in message.lower() for w in ["week", "आठवडा", "साप्ताहिक", "hafta"]) else ("monthly" if any(w in message.lower() for w in ["month", "महिना", "मासिक"]) else ("yearly" if any(w in message.lower() for w in ["year", "वर्ष", "वार्षिक"]) else "daily"))
            rep = ledger.get_periodic_report(period)

            if lang == "marathi":
                period_mr = "दैनंदिन" if period == "daily" else ("साप्ताहिक" if period == "weekly" else ("मासिक" if period == "monthly" else "वार्षिक"))
                reply = f"📊 **{profile.get('store_name')}** चा **{period_mr} विक्री व नफा अहवाल**:\n• एकूण महसूल: **₹{rep['total_income']}**\n• एकूण खर्च: **₹{rep['total_expense']}**\n• निव्वळ नफा: **₹{rep['net_profit']}** (नफा दर: **{rep['profit_margin_pct']}%**)."
            elif lang == "hindi":
                period_hi = "दैनिक" if period == "daily" else ("साप्ताहिक" if period == "weekly" else ("मासिक" if period == "monthly" else "वार्षिक"))
                reply = f"📊 **{profile.get('store_name')}** की **{period_hi} वित्तीय रिपोर्ट**:\n• कुल बिक्री: **₹{rep['total_income']}**\n• कुल खर्च: **₹{rep['total_expense']}**\n• शुद्ध मुनाफा: **₹{rep['net_profit']}** (मार्जिन: **{rep['profit_margin_pct']}%**)."
            else:
                reply = f"📊 Here is the **{period.capitalize()} Financial & Sales Report** for **{profile.get('store_name')}**:\n• Total Revenue: **₹{rep['total_income']}**\n• Expenses: **₹{rep['total_expense']}**\n• Net Profit: **₹{rep['net_profit']}** ({rep['profit_margin_pct']}% margin)."

            return {
                "intent": intent,
                "mode": "reports",
                "mode_name": f"{period.capitalize()} Sales Report",
                "report_data": rep,
                "reply_text": reply
            }
        elif intent == "mode_maps":
            if lang == "marathi":
                reply = f"📍 **गुगल मॅप्स व स्थानिक स्थान**: **{profile.get('store_name')}** हे **{profile.get('location')}** येथे नोंदणीकृत आहे. वेळ: **{profile.get('operating_hours')}**."
            elif lang == "hindi":
                reply = f"📍 **गूगल मैप्स और स्थानीय स्थान**: **{profile.get('store_name')}** **{profile.get('location')}** पर स्थित है। समय: **{profile.get('operating_hours')}**."
            else:
                reply = f"📍 **Google Maps Stall Listing**: Located at **{profile.get('location')}**. Open daily from {profile.get('operating_hours')}."

            return {
                "intent": intent,
                "mode": "maps",
                "mode_name": "Google Maps & Local SEO",
                "store_name": profile.get("store_name", "Camp Fresh Fruits"),
                "location": profile.get("location", "Near Main Market Road & MG Road, Camp, Pune"),
                "gmaps_link": f"https://www.google.com/maps/search/?api=1&query={profile.get('location', 'Camp+Pune').replace(' ', '+')}",
                "reply_text": reply
            }
        elif intent == "mode_poster":
            qr_b64 = generate_upi_qr_base64(profile.get("upi_id", "campfruits@upi"), profile.get("store_name", "Camp Fresh Fruits"))
            svg = generate_stall_poster_svg(
                stall_name=profile.get("store_name", "Camp Fresh Fruits"),
                tagline=f"100% Farm-Fresh Daily • {profile.get('owner_name')}",
                location=profile.get("location", "Camp, Pune"),
                operating_hours=profile.get("operating_hours", "7:00 AM - 8:00 PM"),
                upi_id=profile.get("upi_id", "campfruits@upi"),
                qr_base64=qr_b64,
                language=lang
            )
            if lang == "marathi":
                reply = f"🎨 **{profile.get('store_name')}** साठी छापील स्टॉल मार्केटिंग बॅनर आणि UPI QR स्टँडी तयार करण्यात आले आहे (UPI ID: `{profile.get('upi_id')}`). 'Print Standee' वर क्लिक करून प्रिंट करा."
            elif lang == "hindi":
                reply = f"🎨 **{profile.get('store_name')}** के लिए प्रिंटेबल स्टॉल मार्केटिंग बैनर और UPI QR स्टैंडी तैयार की गई है (UPI ID: `{profile.get('upi_id')}`). 'Print Standee' पर क्लिक करके प्रिंट करें।"
            else:
                reply = f"🎨 Generated printable stall marketing banner and UPI QR standee for **{profile.get('store_name')}** (UPI: `{profile.get('upi_id')}`)."

            return {
                "intent": intent,
                "mode": "poster",
                "mode_name": "Printable Stall Banner & QR Code",
                "poster_svg": svg,
                "qr_base64": qr_b64,
                "reply_text": reply
            }
        elif intent == "mode_2_score":
            res = self.mode_2_digital_score(signals, session_id, lang)
            res["intent"] = intent
            if lang == "marathi":
                res["reply_text"] = f"📈 **{res['store_name']}** चा सध्याचा डिजिटल सज्जता स्कोअर: **{res['score']}/१००** ({res['badge']}). पुढील पायरी: {res['next_actions'][0]}"
            elif lang == "hindi":
                res["reply_text"] = f"📈 **{res['store_name']}** का वर्तमान डिजिटल स्कोर: **{res['score']}/100** ({res['badge']}). अगला कदम: {res['next_actions'][0]}"
            else:
                res["reply_text"] = f"📈 Your Digital Readiness Score for **{res['store_name']}** is **{res['score']}/100** ({res['badge']}). Next Step: {res['next_actions'][0]}"
            return res
        elif intent == "mode_3_ledger":
            res = self.mode_3_ledger_log(message, session_id, lang)
            res["intent"] = intent
            res["reply_text"] = res["confirmation"]
            return res
        elif intent == "mode_4_market":
            res = self.mode_4_market_insights("pune", "fruits", session_id, lang)
            res["intent"] = intent
            if lang == "marathi":
                res["reply_text"] = f"🍉 **पुणे APMC गुलटेकडी मंडी भाव विश्लेषण**:\n• केळी: घाऊक दर ₹२०-₹३५/डझन (किरकोळ ₹५०)\n• सफरचंद: घाऊक दर ₹११०-₹१२५/किलो (किरकोळ ₹१६०)\n• हापूस आंबे: घाऊक दर ₹४५०-₹५२०/डझन (किरकोळ ₹६५०)\n⏰ **ग्राहक गर्दीची वेळ:** सकाळी ७:३०-१०:३० व संध्याकाळी ५:३०-८:३०."
            elif lang == "hindi":
                res["reply_text"] = f"🍉 **पुणे APMC मंडी भाव विश्लेषण**:\n• केला: थोक भाव ₹20-₹35/दर्जन (खुदरा ₹50)\n• सेब: थोक भाव ₹110-₹125/किलो (खुदरा ₹160)\n• आम: थोक भाव ₹450-₹520/दर्जन (खुदरा ₹650)\n⏰ **बिक्री का सर्वोत्तम समय:** सुबह 7:30-10:30 और शाम 5:30-8:30."
            else:
                res["reply_text"] = f"🍉 **Pune APMC Mandi Intelligence**:\n• Bananas: Wholesale ₹20-₹35/doz (Retail ₹50)\n• Apples: Wholesale ₹110-₹125/kg (Retail ₹160)\n• Mangoes: Wholesale ₹450-₹520/doz (Retail ₹650)\n⏰ **Peak Selling Window:** 7:30-10:30 AM & 5:30-8:30 PM."
            return res
        elif intent == "mode_5_whatsapp":
            kit = self.mode_1_onboarding_kit(message, lang, session_id)
            wa_text = self.mode_5_whatsapp_format(kit, session_id, lang)
            return {
                "intent": intent,
                "mode": 5,
                "mode_name": "WhatsApp-Ready Format",
                "whatsapp_text": wa_text,
                "reply_text": wa_text
            }
        elif intent == "mode_profile":
            if lang == "marathi":
                reply = f"🏪 आपले दुकान **{profile.get('store_name')}** (मालक: {profile.get('owner_name')}) सक्रिय आहे. AI सहाय्यक: **{profile.get('agent_name')}**."
            elif lang == "hindi":
                reply = f"🏪 आपकी दुकान **{profile.get('store_name')}** (मालिक: {profile.get('owner_name')}) सक्रिय है। AI सहायक: **{profile.get('agent_name')}**."
            else:
                reply = f"🏪 Your store **{profile.get('store_name')}** (Owner: {profile.get('owner_name')}) is configured. AI Agent Name: **{profile.get('agent_name')}**."

            return {
                "intent": intent,
                "mode": 6,
                "mode_name": "Store & AI Agent Personalization",
                "profile": profile,
                "reply_text": reply
            }
        else:
            res = self.mode_1_onboarding_kit(message, lang, session_id)
            res["intent"] = intent
            if lang == "marathi":
                res["reply_text"] = f"🚀 **{res['business_profile']['suggested_name']}** साठी संपूर्ण डिजिटल ऑनबोर्डिंग किट तयार आहे! यात गुगल बिझनेस प्रोफाइल, UPI सेटअप (\`{profile.get('upi_id')}\`), पीएम स्वनिधी योजना जुळणी आणि मराठी प्रचार साहित्य समाविष्ट आहे."
            elif lang == "hindi":
                res["reply_text"] = f"🚀 **{res['business_profile']['suggested_name']}** के लिए संपूर्ण डिजिटल ऑनबोर्डिंग किट तैयार है! इसमें गूगल बिजनेस प्रोफाइल, UPI सेटअप (\`{profile.get('upi_id')}\`), पीएम स्वनिधि ऋण मिलान और हिंदी प्रचार सामग्री शामिल है।"
            else:
                res["reply_text"] = f"🚀 Here is your complete Digital Onboarding Kit for **{res['business_profile']['suggested_name']}**! Includes Google Business profile, UPI setup for `{profile.get('upi_id')}`, PM SVANidhi scheme matching, and bilingual marketing material."
            return res