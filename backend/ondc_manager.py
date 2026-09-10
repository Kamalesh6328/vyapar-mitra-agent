# -*- coding: utf-8 -*-
from typing import Dict, Any, List

def generate_ondc_store_schema(
    store_name: str,
    owner_name: str,
    location: str,
    phone: str,
    upi_id: str,
    specialities: str,
    operating_hours: str
) -> Dict[str, Any]:
    # Creates ONDC Retail Protocol Beckn compliant Provider Catalogue Schema
    items_list = []
    default_items = [
        {"name": "Fresh Banana (केळी)", "price": 50.0, "unit": "dozen", "category": "Fruits", "in_stock": True},
        {"name": "Crisp Royal Apple (सफरचंद)", "price": 160.0, "unit": "kg", "category": "Fruits", "in_stock": True},
        {"name": "Seasonal Alphonso Mango (हापूस आंबा)", "price": 650.0, "unit": "dozen", "category": "Seasonal Fruits", "in_stock": True},
        {"name": "Fresh Papaya (पपई)", "price": 40.0, "unit": "kg", "category": "Fruits", "in_stock": True},
        {"name": "Ruby Pomegranate (डाळिंब)", "price": 180.0, "unit": "kg", "category": "Fruits", "in_stock": True},
        {"name": "Sweet Orange (मोसंबी / संत्री)", "price": 70.0, "unit": "kg", "category": "Fruits", "in_stock": True}
    ]
    
    for idx, itm in enumerate(default_items):
        items_list.append({
            "id": f"ITEM_VM_{idx+1:03d}",
            "descriptor": {
                "name": itm["name"],
                "symbol": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=150",
                "short_desc": f"Freshly sourced produce at {store_name}",
                "long_desc": f"Handpicked daily stock available at {location}."
            },
            "category_id": itm["category"],
            "price": {
                "currency": "INR",
                "value": f"{itm['price']:.2f}",
                "unit": itm["unit"]
            },
            "quantity": {
                "available": {"count": 25},
                "maximum": {"count": 10}
            },
            "fulfillment_id": "FULFILLMENT_HYPERLOCAL_PICKUP_DELIVERY"
        })

    return {
        "context": {
            "domain": "nic2004:52110",
            "country": "IND",
            "city": "std:020", # Pune STD code
            "action": "on_search",
            "core_version": "1.2.0",
            "bap_id": "buyer-app.ondc.org",
            "bpp_id": "seller-app.vyaparmitra.org",
            "bpp_uri": "https://seller.vyaparmitra.org/ondc"
        },
        "message": {
            "catalog": {
                "bpp/fulfillments": [
                    {"id": "1", "type": "Hyperlocal Delivery (1-3 km)"},
                    {"id": "2", "type": "Storefront Self-Pickup"}
                ],
                "bpp/descriptor": {
                    "name": store_name,
                    "symbol": "https://cdn-icons-png.flaticon.com/512/3081/3081986.png",
                    "short_desc": f"{store_name} - Hyperlocal Street Vendor",
                    "long_desc": f"Operated by {owner_name}. Located at {location}. Operating Hours: {operating_hours}."
                },
                "bpp/categories": [
                    {"id": "Fruits", "description": "Fresh Seasonal Produce"},
                    {"id": "Seasonal Fruits", "description": "Limited Seasonal Specials"}
                ],
                "bpp/providers": [
                    {
                        "id": f"PROVIDER_VM_{store_name.replace(' ', '_').upper()}",
                        "descriptor": {
                            "name": store_name,
                            "phone": phone
                        },
                        "locations": [
                            {
                                "id": "LOC_STALL_MAIN",
                                "gps": "18.5167,73.8800", # Pune Camp approx GPS
                                "address": {
                                    "street": location,
                                    "city": "Pune",
                                    "state": "Maharashtra",
                                    "area_code": "411001"
                                }
                            }
                        ],
                        "payments": [
                            {"type": "ON-ORDER", "collected_by": "BPP", "settlement_upi": upi_id}
                        ],
                        "items": items_list
                    }
                ]
            }
        }
    }