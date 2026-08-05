"""
Migration: Add pricing tiers to existing services + create missing services.
Run once: python migrate_pricing.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url, tls=True, tlsAllowInvalidCertificates=True)
db = client[os.environ['DB_NAME']]

# ── Pricing tiers for existing services ──
PRICING_UPDATES = {
    "bookkeeping": [
        {"name": "Small", "price": 50000, "description": "Small business bookkeeping"},
        {"name": "Medium", "price": 80000, "description": "Medium business bookkeeping"},
        {"name": "Large (301–700 transactions)", "price": 100000, "description": "High-volume bookkeeping (301–700 transactions)"},
    ],
    "financial-statement": [
        {"name": "Annual Financial Statements", "price": 200000, "description": "Full annual financial statements preparation"},
        {"name": "Management Accounts", "price": 100000, "description": "Monthly/quarterly management accounts"},
        {"name": "Financial Statement Review", "price": 100000, "description": "Review and assurance of financial statements"},
    ],
    "payroll-management": [
        {"name": "Up to 20 Staff", "price": 2500, "description": "₦2,500 per staff (up to 20 staff)"},
        {"name": "21–50 Staff", "price": 2200, "description": "₦2,200 per staff (21–50 staff)"},
        {"name": "51–100 Staff", "price": 2000, "description": "₦2,000 per staff (51–100 staff)"},
        {"name": "Pension Schedule", "price": 50000, "description": "Pension contribution schedule preparation"},
        {"name": "PAYE Schedule", "price": 50000, "description": "PAYE tax schedule preparation"},
        {"name": "NHF Schedule", "price": 30000, "description": "NHF contribution schedule preparation"},
        {"name": "NSITF Schedule", "price": 30000, "description": "NSITF contribution schedule preparation"},
        {"name": "Payroll Reports", "price": 40000, "description": "Comprehensive payroll reporting"},
    ],
    "cit-filing": [
        {"name": "Company Income Tax (CIT)", "price": 150000, "description": "Complete CIT filing and compliance"},
    ],
    "vat-filing": [
        {"name": "VAT Filing", "price": 20000, "description": "Monthly/quarterly VAT return filing"},
    ],
    "wht-filing": [
        {"name": "Withholding Tax Filing", "price": 20000, "description": "WHT deduction and filing"},
    ],
    "paye-administration": [
        {"name": "PAYE Filing", "price": 50000, "description": "PAYE tax filing and remittance"},
    ],
    "capital-gains-tax": [
        {"name": "Capital Gains Tax", "price": 50000, "description": "CGT computation and filing"},
    ],
    "stamp-duties": [
        {"name": "Stamp Duty", "price": 20000, "description": "Stamp duty compliance and filing"},
    ],
    "tax-health-check": [
        {"name": "Annual Tax Health Check", "price": 100000, "description": "Comprehensive annual tax review"},
    ],
    "tax-clearance-certificate": [
        {"name": "Tax Clearance Certificate", "price": 80000, "description": "TCC processing and issuance"},
    ],
    "cac-registration": [
        {"name": "Company Registration", "price": 150000, "description": "Full CAC company registration"},
    ],
    "business-name-registration": [
        {"name": "Business Name Registration", "price": 75000, "description": "CAC business name registration"},
    ],
    "cac-annual-returns": [
        {"name": "Annual Returns", "price": 50000, "description": "Annual returns filing with CAC"},
    ],
    "scuml-registration": [
        {"name": "SCUML Registration", "price": 50000, "description": "SCUML compliance registration"},
    ],
}

# ── New services to create ──
def svc_doc(title, slug, category, division, subcategory, desc, features, steps, docs, timeline, price, tiers):
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "slug": slug,
        "category": category,
        "division": division,
        "subcategory": subcategory,
        "description": desc,
        "features": features,
        "process_steps": steps,
        "required_documents": docs,
        "estimated_timeline": timeline,
        "price_range": price,
        "pricing_tiers": tiers,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

NEW_SERVICES = [
    svc_doc(
        "Bank Reconciliation", "bank-reconciliation", "business",
        "Business Services", "Financial & Accounting Services",
        "Reconcile bank statements with internal financial records to ensure accuracy and identify discrepancies.",
        ["Bank statement matching", "Discrepancy identification", "Reconciliation reporting", "Exception tracking"],
        ["Collect bank statements", "Match transactions", "Identify discrepancies", "Prepare reconciliation report"],
        ["Bank statements", "Cash book / ledger", "Previous reconciliation reports"],
        "3-5 business days", "₦50,000 per bank account",
        [{"name": "Per Bank Account", "price": 50000, "description": "₦50,000 per bank account"}]
    ),
    svc_doc(
        "Accounts Payable Management", "accounts-payable", "business",
        "Business Services", "Financial & Accounting Services",
        "Complete management of accounts payable including invoice processing, vendor payments, and aging analysis.",
        ["Invoice processing", "Payment scheduling", "Vendor management", "Aging analysis", "Payment reporting"],
        ["Receive invoices", "Verify and approve", "Schedule payments", "Process payments", "Generate aging report"],
        ["Purchase orders", "Invoices", "Vendor bank details", "Payment authorization"],
        "Ongoing/monthly", "₦100,000",
        [{"name": "Standard", "price": 100000, "description": "Full accounts payable management"}]
    ),
    svc_doc(
        "Accounts Receivable Management", "accounts-receivable", "business",
        "Business Services", "Financial & Accounting Services",
        "Management of accounts receivable including invoicing, collections, credit control, and aging analysis.",
        ["Invoice generation", "Collections management", "Credit control", "Aging analysis", "Bad debt provisioning"],
        ["Generate invoices", "Send reminders", "Track collections", "Update aging report", "Provision for bad debts"],
        ["Sales records", "Customer details", "Payment terms", "Previous receivable records"],
        "Ongoing/monthly", "₦100,000",
        [{"name": "Standard", "price": 100000, "description": "Full accounts receivable management"}]
    ),
    svc_doc(
        "Inventory Reconciliation", "inventory-reconciliation", "business",
        "Business Services", "Financial & Accounting Services",
        "Physical inventory count reconciliation with book records to identify and account for discrepancies.",
        ["Physical count coordination", "Book-to-physical reconciliation", "Variance analysis", "Adjustment entries"],
        ["Plan physical count", "Conduct count", "Compare with books", "Investigate variances", "Post adjustments"],
        ["Inventory register", "Warehouse location list", "Previous count sheets", "Stock movement records"],
        "5-10 business days", "₦100,000",
        [{"name": "Standard", "price": 100000, "description": "Complete inventory reconciliation"}]
    ),
    svc_doc(
        "General Ledger Review", "general-ledger-review", "business",
        "Business Services", "Financial & Accounting Services",
        "Thorough review of the general ledger to ensure accuracy, completeness, and compliance with accounting standards.",
        ["Account analysis", "Transaction verification", "Error identification", "Reclassification entries"],
        ["Extract GL report", "Analyze account balances", "Verify transactions", "Identify errors", "Prepare findings report"],
        ["General ledger extract", "Chart of accounts", "Supporting documentation", "Prior period GL"],
        "5-10 business days", "₦150,000",
        [{"name": "Standard", "price": 150000, "description": "Comprehensive general ledger review"}]
    ),
    svc_doc(
        "Trial Balance Preparation", "trial-balance", "business",
        "Business Services", "Financial & Accounting Services",
        "Preparation of trial balance from general ledger to verify debits equal credits and identify posting errors.",
        ["Account balance extraction", "Debit/credit verification", "Error identification", "Adjustment recommendations"],
        ["Extract account balances", "Verify arithmetic accuracy", "Identify imbalances", "Recommend adjustments"],
        ["General ledger", "Chart of accounts", "Adjustment entries", "Prior period trial balance"],
        "3-5 business days", "₦200,000",
        [{"name": "Standard", "price": 200000, "description": "Complete trial balance preparation"}]
    ),
    svc_doc(
        "PAYE Registration", "paye-registration", "tax",
        "Tax Services", "Tax Compliance",
        "Registration of your organization with the State Internal Revenue Service for PAYE tax compliance.",
        ["State IRS registration", "TIN issuance", "PAYE code allocation", "Compliance setup"],
        ["Gather required documents", "Complete registration forms", "Submit to state IRS", "Receive PAYE registration certificate"],
        ["CAC certificate", "Employee list", "Business address proof", "Valid ID of directors", "Utility bill"],
        "5-10 business days", "₦30,000",
        [{"name": "Standard", "price": 30000, "description": "PAYE registration with state IRS"}]
    ),
]


async def migrate():
    # 1. Update pricing tiers on existing services
    print("=== Updating pricing tiers ===")
    updated = 0
    for slug, tiers in PRICING_UPDATES.items():
        result = await db.services.update_one(
            {"slug": slug},
            {"$set": {"pricing_tiers": tiers}}
        )
        if result.modified_count > 0:
            print(f"  [OK] {slug} — {len(tiers)} tiers")
            updated += 1
        elif result.matched_count > 0:
            print(f"  [SKIP] {slug} — already set")
        else:
            print(f"  [MISS] {slug}")
    print(f"  Updated: {updated}\n")

    # 2. Create missing services
    print("=== Creating missing services ===")
    created = 0
    for svc in NEW_SERVICES:
        exists = await db.services.find_one({"slug": svc["slug"]})
        if exists:
            # Update pricing tiers if missing
            if not exists.get("pricing_tiers"):
                await db.services.update_one(
                    {"slug": svc["slug"]},
                    {"$set": {"pricing_tiers": svc["pricing_tiers"]}}
                )
                print(f"  [UPDATED TIERS] {svc['slug']}")
                created += 1
            else:
                print(f"  [EXISTS] {svc['slug']}")
        else:
            await db.services.insert_one(svc)
            print(f"  [CREATED] {svc['slug']} — {svc['title']}")
            created += 1
    print(f"  Created/Updated: {created}")
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(migrate())
