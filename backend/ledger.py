# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class MicroLedger:
    def __init__(self):
        self.transactions: List[Dict[str, Any]] = []
        self._seed_sample_history()

    def _seed_sample_history(self):
        # Seed realistic recent transaction history for multi-period (Daily, Weekly, Monthly, Yearly) demo
        now = datetime.now()
        samples = [
            (now - timedelta(days=0), "income", 550.0, "Sold 12 kg bananas and 6 kg apples", "Fruit Sales"),
            (now - timedelta(days=0), "expense", 80.0, "Ice blocks for fruit cooling", "Cooling/Ice"),
            (now - timedelta(days=1), "income", 680.0, "Sold seasonal Alphonso mangoes", "Fruit Sales"),
            (now - timedelta(days=1), "expense", 120.0, "Tempo transport from Gultekdi Mandi", "Logistics"),
            (now - timedelta(days=2), "income", 740.0, "Daily office commuter fruit packs", "Fruit Sales"),
            (now - timedelta(days=3), "income", 620.0, "Sold papayas and pomegranates", "Fruit Sales"),
            (now - timedelta(days=4), "expense", 150.0, "Cart wheel maintenance", "Maintenance"),
            (now - timedelta(days=5), "income", 890.0, "Weekend residential bulk orders", "Fruit Sales"),
            (now - timedelta(days=8), "income", 780.0, "Weekly office fruit supply", "Fruit Sales"),
            (now - timedelta(days=12), "income", 810.0, "Evening family fruit sales", "Fruit Sales"),
            (now - timedelta(days=15), "expense", 200.0, "Crate storage charges", "Operating Expense"),
            (now - timedelta(days=20), "income", 920.0, "Festival seasonal fruit orders", "Fruit Sales"),
            (now - timedelta(days=28), "income", 850.0, "End-of-month fruit clearance", "Fruit Sales"),
            (now - timedelta(days=45), "income", 940.0, "Mango peak season sales", "Fruit Sales"),
            (now - timedelta(days=60), "income", 760.0, "Apples and oranges morning sales", "Fruit Sales"),
            (now - timedelta(days=90), "income", 820.0, "Quarterly corporate fruit snacks", "Fruit Sales"),
            (now - timedelta(days=120), "income", 750.0, "Daily market road sales", "Fruit Sales"),
            (now - timedelta(days=180), "income", 890.0, "Mid-year fruit hampers", "Fruit Sales"),
            (now - timedelta(days=250), "income", 910.0, "Winter special oranges & apples", "Fruit Sales"),
            (now - timedelta(days=320), "income", 870.0, "Early season fruit sales", "Fruit Sales")
        ]
        for dt, tx_type, amount, desc, cat in samples:
            self.transactions.append({
                "id": len(self.transactions) + 1,
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "date": dt.strftime("%Y-%m-%d"),
                "type": tx_type,
                "amount": amount,
                "description": desc,
                "category": cat
            })

    def add_entry(self, tx_type: str, amount: float, description: str, category: str = "General") -> Dict[str, Any]:
        now = datetime.now()
        entry = {
            "id": len(self.transactions) + 1,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "type": tx_type.lower(),
            "amount": round(float(amount), 2),
            "description": description.strip(),
            "category": category
        }
        self.transactions.append(entry)
        return entry

    def parse_natural_language(self, text: str) -> List[Dict[str, Any]]:
        # Normalize Devanagari numerals (०-९) to ASCII digits (0-9)
        devanagari_digits = str.maketrans("०१२३४५६७८९", "0123456789")
        normalized_text = text.translate(devanagari_digits)

        added = []
        # Split on commas, semicolons, newlines, and conjunctions in English, Marathi, Hindi
        parts = re.split(r'[,;.\n]|\band\b|आणि|व|तसेच|और|तथा|एवं', normalized_text, flags=re.IGNORECASE)
        for part in parts:
            p = part.strip()
            if not p:
                continue
            nums = re.findall(r'(\d+(?:\.\d+)?)', p)
            if not nums:
                continue
            amount_val = float(nums[0])
            p_lower = p.lower()
            
            # Expense keywords in English, Marathi, Hindi, Hinglish
            expense_keywords = [
                'spent', 'bought', 'buy', 'expense', 'paid', 'cost', 'ice', 'transport', 'repair',
                'kharch', 'diye', 'khareeda', 'kharid', 'bhada', 'kiraya',
                'खर्च', 'दिले', 'खरेदी', 'घेतले', 'आणले', 'भरले', 'बर्फ', 'भाडे', 'वाहतूक', 'दुरुस्ती',
                'दिए', 'खरीदा', 'खरीदे', 'लिए', 'लाए', 'भाड़ा', 'मरम्मत'
            ]
            is_expense = any(k in p_lower for k in expense_keywords)
            
            if is_expense:
                if any(x in p_lower for x in ['ice', 'बर्फ', 'barf']):
                    cat = "Cooling/Ice"
                elif any(x in p_lower for x in ['transport', 'भाडे', 'वाहतूक', 'भाड़ा', 'kiraya', 'tempo']):
                    cat = "Logistics"
                else:
                    cat = "Operating Expense"
                clean_desc = re.sub(r'(\d+(?:\.\d+)?)', '', p).strip() or "Daily Operating Expense"
                entry = self.add_entry("expense", amount_val, clean_desc, cat)
                added.append(entry)
            else:
                cat = "Fruit Sales"
                clean_desc = re.sub(r'(\d+(?:\.\d+)?)', '', p).strip() or "Daily Fruit Sales"
                entry = self.add_entry("income", amount_val, clean_desc, cat)
                added.append(entry)
        return added

    def get_summary(self) -> Dict[str, Any]:
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in self.transactions if t["type"] == "expense")
        net = total_income - total_expense
        margin = round((net / total_income) * 100, 1) if total_income > 0 else 0.0
        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_profit": round(net, 2),
            "profit_margin_pct": margin,
            "transaction_count": len(self.transactions),
            "transactions": self.transactions
        }

    def get_periodic_report(self, period: str = "daily") -> Dict[str, Any]:
        now = datetime.now()
        period = period.lower()
        
        if period == "daily":
            # Filter today's transactions or last 7 days breakdown
            days_limit = 1
            labels = ["Today"]
        elif period == "weekly":
            days_limit = 7
            labels = [(now - timedelta(days=i)).strftime("%a (%d %b)") for i in range(6, -1, -1)]
        elif period == "monthly":
            days_limit = 30
            labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
        else: # yearly
            days_limit = 365
            labels = ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"]

        cutoff = now - timedelta(days=days_limit)
        filtered = [t for t in self.transactions if datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S") >= cutoff] if period != "yearly" else self.transactions

        income = sum(t["amount"] for t in filtered if t["type"] == "income")
        expense = sum(t["amount"] for t in filtered if t["type"] == "expense")
        profit = income - expense
        margin = round((profit / income) * 100, 1) if income > 0 else 0.0

        # Chart Series Generation
        if period == "weekly":
            chart_income = []
            chart_expense = []
            for i in range(6, -1, -1):
                day_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                d_inc = sum(t["amount"] for t in self.transactions if t.get("date") == day_str and t["type"] == "income")
                d_exp = sum(t["amount"] for t in self.transactions if t.get("date") == day_str and t["type"] == "expense")
                chart_income.append(round(d_inc, 2))
                chart_expense.append(round(d_exp, 2))
        elif period == "monthly":
            chart_income = [round(income * 0.22, 2), round(income * 0.28, 2), round(income * 0.24, 2), round(income * 0.26, 2)]
            chart_expense = [round(expense * 0.25, 2), round(expense * 0.22, 2), round(expense * 0.30, 2), round(expense * 0.23, 2)]
        elif period == "yearly":
            chart_income = [round(income * 0.24, 2), round(income * 0.32, 2), round(income * 0.22, 2), round(income * 0.22, 2)]
            chart_expense = [round(expense * 0.25, 2), round(expense * 0.25, 2), round(expense * 0.25, 2), round(expense * 0.25, 2)]
        else: # daily
            labels = ["Morning (7-11 AM)", "Afternoon (11-4 PM)", "Evening (4-8 PM)"]
            chart_income = [round(income * 0.45, 2), round(income * 0.15, 2), round(income * 0.40, 2)]
            chart_expense = [round(expense * 0.70, 2), round(expense * 0.10, 2), round(expense * 0.20, 2)]

        return {
            "period": period.capitalize(),
            "total_income": round(income, 2),
            "total_expense": round(expense, 2),
            "net_profit": round(profit, 2),
            "profit_margin_pct": margin,
            "transaction_count": len(filtered),
            "chart_labels": labels,
            "chart_income": chart_income,
            "chart_expense": chart_expense,
            "filtered_transactions": filtered
        }

    def generate_loan_statement(self, vendor_name: str = "Camp Fresh Fruits") -> Dict[str, Any]:
        summ = self.get_summary()
        return {
            "statement_title": f"Informal Micro-Enterprise Cash Flow Statement - {vendor_name}",
            "generated_at": datetime.now().strftime("%d-%b-%Y %H:%M"),
            "total_revenue": summ["total_income"],
            "total_operating_expenses": summ["total_expense"],
            "net_operating_profit": summ["net_profit"],
            "operating_margin": f"{summ['profit_margin_pct']}%",
            "record_count": summ["transaction_count"],
            "loan_readiness_indicator": "Positive Cash Flow - Suitable for PM SVANidhi Micro-Credit" if summ["net_profit"] >= 0 else "Caution: Operating Deficit",
            "recommended_first_tranche": "₹15,000 (PM SVANidhi Scheme)",
            "transactions": self.transactions
        }

    def export_csv(self, period: str = "all") -> str:
        lines = ["ID,Timestamp,Type,Amount (INR),Category,Description"]
        for t in self.transactions:
            desc = t["description"].replace(",", " ")
            lines.append(f"{t['id']},{t['timestamp']},{t['type']},{t['amount']},{t['category']},{desc}")
        return "\n".join(lines)

    def clear(self):
        self.transactions = []