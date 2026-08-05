import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone
from auth import get_password_hash

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url, tls=True, tlsAllowInvalidCertificates=True)
db = client[os.environ['DB_NAME']]

def svc(title, slug, category, division, subcategory, desc, features, steps, docs, timeline, price, pricing_tiers=None, is_recurring=False, billing_cycle=None, base_price_per_cycle=None):
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
        "pricing_tiers": pricing_tiers or [],
        "is_active": True,
        "is_recurring": is_recurring,
        "billing_cycle": billing_cycle,
        "base_price_per_cycle": base_price_per_cycle,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def build_services():
    s = []
    # ═══════════════════════════════════════════
    # DIVISION 1: TAX SERVICES
    # ═══════════════════════════════════════════
    # ── Subcategory: Tax Compliance ──
    s.append(svc(
        "Tax Registration (State or Federal)", "tax-registration", "tax",
        "Tax Services", "Tax Compliance",
        "Complete tax registration with FIRS or State IRS for businesses and individuals.",
        ["Federal tax registration (FIRS)", "State tax registration", "TIN issuance", "Tax profile setup"],
        ["Gather required documents", "Complete registration forms", "Submit to relevant tax authority", "Receive TIN and certificates"],
        ["CAC certificate (companies)", "Valid ID (individuals)", "Utility bill", "Business address proof", "Passport photograph"],
        "5-10 business days", "₦30,000 - ₦80,000"
    ))
    s.append(svc(
        "Company Income Tax (CIT) Filing", "cit-filing", "tax",
        "Tax Services", "Tax Compliance",
        "Annual CIT returns filing for registered companies in Nigeria, including computation and optimization.",
        ["CIT computation and filing", "Tax optimization strategies", "FIRS portal submission", "Payment evidence documentation"],
        ["Review financial statements", "Compute assessable profit", "Prepare tax returns", "Submit to FIRS"],
        ["Audited financial statements", "Previous year's returns", "Bank statements", "Tax clearance certificate", "Fixed asset schedule"],
        "7-14 business days", "₦80,000 - ₦300,000",
        [{"name": "Company Income Tax (CIT)", "price": 150000, "description": "Complete CIT filing and compliance"}]
    ))
    s.append(svc(
        "Value Added Tax (VAT) Filing", "vat-filing", "tax",
        "Tax Services", "Tax Compliance",
        "Monthly VAT returns filing and remittance for VAT-registered businesses.",
        ["Monthly VAT computation", "Input/Output VAT reconciliation", "FIRS portal filing", "VAT payment advice"],
        ["Compile VAT transactions", "Reconcile input and output VAT", "Prepare monthly returns", "Submit and remit VAT"],
        ["Sales invoices", "Purchase invoices", "VAT registration certificate", "Bank statements", "Previous VAT returns"],
        "3-5 business days", "₦25,000 - ₦100,000/month",
        [{"name": "VAT Filing", "price": 20000, "description": "Monthly/quarterly VAT return filing"}]
    ))
    s.append(svc(
        "Withholding Tax (WHT) Filing", "wht-filing", "tax",
        "Tax Services", "Tax Compliance",
        "WHT returns filing and remittance compliance including vendor certificate issuance.",
        ["WHT computation", "Monthly/Quarterly returns", "Vendor WHT certificate issuance", "Compliance tracking"],
        ["Compile withholding transactions", "Compute WHT by category", "Prepare returns", "Submit to tax authority"],
        ["Payment vouchers", "Vendor invoices", "Bank statements", "TIN of vendors", "Previous WHT returns"],
        "3-5 business days", "₦30,000 - ₦120,000",
        [{"name": "Withholding Tax Filing", "price": 20000, "description": "WHT deduction and filing"}]
    ))
    s.append(svc(
        "PAYE Administration", "paye-administration", "tax",
        "Tax Services", "Tax Compliance",
        "Monthly PAYE deduction, filing and remittance to State IRS.",
        ["Monthly PAYE computation", "Employee tax schedule", "State portal filing", "Annual reconciliation"],
        ["Compute monthly deductions", "Prepare PAYE schedule", "File with State IRS", "Remit tax and obtain receipts"],
        ["Employee payroll records", "Staff TINs", "Previous PAYE returns", "Bank payment evidence", "Employee register"],
        "2-5 business days", "₦20,000 - ₦100,000/month",
        [{"name": "PAYE Filing", "price": 50000, "description": "PAYE tax filing and remittance"}]
    ))
    s.append(svc(
        "Education Tax Computation", "education-tax", "tax",
        "Tax Services", "Tax Compliance",
        "Computation and filing of Education Tax (TETFund) for applicable companies.",
        ["Education tax computation", "TETFund filing", "Payment processing", "Compliance certificate"],
        ["Determine assessable profit", "Compute 2.5% education tax", "File return", "Obtain receipt"],
        ["Audited accounts", "Tax returns", "CIT computations", "Previous education tax receipts"],
        "5-7 business days", "₦30,000 - ₦80,000"
    ))
    s.append(svc(
        "Capital Gains Tax Filing", "capital-gains-tax", "tax",
        "Tax Services", "Tax Compliance",
        "Capital Gains Tax computation and filing for asset disposals and business sales.",
        ["CGT computation", "Exemption analysis", "FIRS filing", "Payment processing"],
        ["Review transaction details", "Compute chargeable gain", "Apply exemptions", "File and remit"],
        ["Asset sale agreements", "Valuation reports", "Acquisition cost evidence", "Legal documents"],
        "7-14 business days", "₦50,000 - ₦200,000",
        [{"name": "Capital Gains Tax", "price": 50000, "description": "CGT computation and filing"}]
    ))
    s.append(svc(
        "Stamp Duties Compliance", "stamp-duties", "tax",
        "Tax Services", "Tax Compliance",
        "Stamp duties assessment, payment and filing for agreements, instruments and documents.",
        ["Stamp duty assessment", "Payment processing", "Stamp certificate issuance", "Compliance advisory"],
        ["Classify instrument", "Prepare assessment", "Pay duty", "Obtain stamp certificate"],
        ["Original agreement/instrument", "Value declaration", "Supporting documents"],
        "3-7 business days", "₦20,000 - ₦80,000",
        [{"name": "Stamp Duty", "price": 20000, "description": "Stamp duty compliance and filing"}]
    ))
    s.append(svc(
        "Transfer Pricing Documentation", "transfer-pricing", "tax",
        "Tax Services", "Tax Compliance",
        "Transfer pricing documentation including master file, local file and country-by-country reporting.",
        ["TP policy review", "Master file preparation", "Local file preparation", "CbC reporting", "Benchmarking analysis"],
        ["Review related-party transactions", "Perform functional analysis", "Prepare benchmarking study", "Compile documentation file"],
        ["Group structure chart", "Related-party agreements", "Financial statements", "Functional analysis questionnaires"],
        "14-30 business days", "₦300,000 - ₦1,000,000"
    ))
    s.append(svc(
        "Tax Clearance Certificate (TCC)", "tax-clearance-certificate", "tax",
        "Tax Services", "Tax Compliance",
        "TCC application and renewal for individuals and companies. Required for contracts, tenders and travel.",
        ["TCC application (new/renewal)", "For individuals and companies", "Fast-track available", "3-year validity"],
        ["Verify compliance status", "Prepare application", "Submit to tax authority", "Obtain certificate"],
        ["Tax returns (3 years)", "Evidence of tax payment", "Audited accounts (companies)", "Valid ID"],
        "10-21 business days", "₦50,000 - ₦200,000",
        [{"name": "Tax Clearance Certificate", "price": 80000, "description": "TCC processing and issuance"}]
    ))
    s.append(svc(
        "Annual Tax Returns Preparation", "annual-tax-returns", "tax",
        "Tax Services", "Tax Compliance",
        "Preparation and filing of annual tax returns for individuals, SMEs and corporations.",
        ["Returns preparation", "Tax computation", "Filing with tax authority", "Acknowledgment receipt"],
        ["Gather income/expense records", "Compute taxable income", "Prepare returns", "File and obtain acknowledgment"],
        ["Income statements", "Expense records", "Capital allowance schedule", "Prior year returns"],
        "5-10 business days", "₦40,000 - ₦150,000"
    ))
    s.append(svc(
        "Tax Remittance Management", "tax-remittance", "tax",
        "Tax Services", "Tax Compliance",
        "End-to-end management of all tax remittances — CIT, VAT, WHT, PAYE — ensuring timely payment.",
        ["Remittance scheduling", "Payment processing", "Receipt tracking", "Compliance calendar"],
        ["Set up compliance calendar", "Process payments", "Track receipts", "Monthly reconciliation"],
        ["Tax assessments", "Bank statements", "Previous remittance records"],
        "Ongoing/monthly", "₦30,000 - ₦100,000/month"
    ))
    s.append(svc(
        "PAYE Registration", "paye-registration", "tax",
        "Tax Services", "Tax Compliance",
        "Registration of your organization with the State Internal Revenue Service for PAYE tax compliance.",
        ["State IRS registration", "TIN issuance", "PAYE code allocation", "Compliance setup"],
        ["Gather required documents", "Complete registration forms", "Submit to state IRS", "Receive PAYE registration certificate"],
        ["CAC certificate", "Employee list", "Business address proof", "Valid ID of directors", "Utility bill"],
        "5-10 business days", "₦30,000",
        [{"name": "Standard", "price": 30000, "description": "PAYE registration with state IRS"}]
    ))
    s.append(svc(
        "Tax Health Check", "tax-health-check", "tax",
        "Tax Services", "Tax Compliance",
        "Comprehensive review of your tax position, filings and obligations to identify risks and opportunities.",
        ["Full tax position review", "Risk identification", "Optimization opportunities", "Compliance gap analysis", "Action plan"],
        ["Review all tax filings", "Analyze compliance gaps", "Identify savings opportunities", "Prepare health check report"],
        ["All tax returns (3 years)", "Tax payment evidence", "Financial statements", "Previous assessments"],
        "7-14 business days", "₦100,000 - ₦300,000",
        [{"name": "Annual Tax Health Check", "price": 100000, "description": "Comprehensive annual tax review"}]
    ))
    # ── Subcategory: Tax Advisory & Consulting ──
    s.append(svc(
        "Tax Planning & Optimization", "tax-planning", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Strategic tax planning to minimize liabilities and align with business objectives.",
        ["Tax efficiency review", "Structure optimization", "Scenario modeling", "Implementation roadmap"],
        ["Review current structure", "Identify optimization areas", "Model scenarios", "Present recommendations"],
        ["Financial statements", "Tax returns", "Business plan", "Group structure details"],
        "10-20 business days", "₦150,000 - ₦500,000"
    ))
    s.append(svc(
        "Tax Risk Assessment", "tax-risk-assessment", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Identify, assess and mitigate tax risks across your business operations.",
        ["Risk identification", "Probability analysis", "Impact assessment", "Mitigation plan"],
        ["Map tax processes", "Identify risk areas", "Assess impact and likelihood", "Develop mitigation plan"],
        ["Tax returns (3 years)", "Business processes documentation", "Previous audit reports"],
        "7-14 business days", "₦100,000 - ₦350,000"
    ))
    s.append(svc(
        "Tax-Efficient Business Structuring", "tax-efficient-structuring", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Advice on optimal business structures for tax efficiency, including holding companies and group structures.",
        ["Structure analysis", "Holding company advisory", "Group restructuring", "Implementation support"],
        ["Review current structure", "Analyze tax implications", "Design optimal structure", "Implementation plan"],
        ["Company documents", "Group structure", "Financial projections", "Shareholder agreements"],
        "14-30 business days", "₦200,000 - ₦600,000"
    ))
    s.append(svc(
        "Cross-Border Tax Advisory", "cross-border-tax", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Tax advisory for cross-border transactions, non-resident entities and foreign investments.",
        ["Double tax treaty analysis", "Non-resident tax advisory", "Repatriation planning", "Permanent establishment risk"],
        ["Analyze cross-border flows", "Apply relevant treaties", "Structure transactions", "Prepare advisory report"],
        ["Cross-border agreements", "Group structure", "Transaction documents", "Tax treaties analysis"],
        "14-30 business days", "₦300,000 - ₦1,000,000"
    ))
    s.append(svc(
        "Expatriate Tax Advisory", "expatriate-tax", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Tax compliance and planning for expatriate employees working in Nigeria.",
        ["Expatriate tax compliance", "Relief and allowance advisory", "Equalization planning", "Exit clearance support"],
        ["Review employment terms", "Compute Nigerian tax exposure", "Advise on reliefs", "Ensure compliance"],
        ["Employment contract", "Expatriate quota (if applicable)", "Passport and visa", "Home country tax details"],
        "5-10 business days", "₦80,000 - ₦250,000"
    ))
    s.append(svc(
        "Investment Tax Advisory", "investment-tax", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Tax advisory for investment vehicles, funds and capital market transactions.",
        ["Investment structure review", "Fund tax advisory", "Capital market transactions", "REIT/infrastructure advisory"],
        ["Analyze investment structure", "Identify tax implications", "Optimize for efficiency", "Prepare advisory"],
        ["Investment agreements", "Fund documents", "Financial projections", "Regulatory filings"],
        "14-21 business days", "₦200,000 - ₦750,000"
    ))
    s.append(svc(
        "Mergers & Acquisition Tax Advisory", "ma-tax-advisory", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Tax due diligence, structuring and integration support for M&A transactions.",
        ["Tax due diligence", "Deal structuring", "Post-acquisition integration", "Regulatory clearance"],
        ["Conduct tax due diligence", "Structure the transaction", "Obtain necessary clearances", "Post-deal integration support"],
        ["Target company tax records", "Financial statements", "Share purchase agreement", "Due diligence reports"],
        "4-8 weeks", "₦500,000 - ₦2,000,000"
    ))
    s.append(svc(
        "Startup Tax Advisory", "startup-tax", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Tax guidance for startups from formation through growth stages, including incentive identification.",
        ["Startup tax structuring", "Pioneer status advisory", "Tax incentive identification", "Compliance setup"],
        ["Review business model", "Identify applicable incentives", "Set up compliance framework", "Ongoing advisory"],
        ["Business plan", "Incorporation documents", "Revenue model details", "Shareholder information"],
        "5-10 business days", "₦50,000 - ₦200,000"
    ))
    s.append(svc(
        "Real Estate Tax Advisory", "real-estate-tax", "tax",
        "Tax Services", "Tax Advisory & Consulting",
        "Tax advisory for real estate development, property investment and REIT structures.",
        ["Property tax analysis", "REIT structuring", "Development advisory", "Capital gains planning"],
        ["Review property portfolio", "Analyze tax exposures", "Structure transactions", "Advisory report"],
        ["Property titles", "Sale/purchase agreements", "Development plans", "Financing documents"],
        "10-20 business days", "₦150,000 - ₦500,000"
    ))
    # ── Subcategory: Tax Audit & Investigation ──
    s.append(svc(
        "FIRS Tax Audit Support", "firs-audit-support", "tax",
        "Tax Services", "Tax Audit & Investigation",
        "Professional support during FIRS tax audit exercises to ensure fair assessment.",
        ["Audit preparation", "Documentation review", "Representation during audit", "Response to queries"],
        ["Prepare audit file", "Review tax positions in advance", "Represent during audit", "Respond to queries"],
        ["Tax returns (3+ years)", "Financial statements", "Audit queries", "Supporting schedules"],
        "Throughout audit period", "₦100,000 - ₦500,000"
    ))
    s.append(svc(
        "State IRS Audit Support", "state-irs-audit", "tax",
        "Tax Services", "Tax Audit & Investigation",
        "Support for audits by State Internal Revenue Services including PAYE and direct assessment audits.",
        ["PAYE audit support", "Direct assessment audit", "Documentation preparation", "Representation"],
        ["Review audit notice", "Prepare documentation", "Attend audit meetings", "Resolve findings"],
        ["PAYE records", "Employee register", "Bank statements", "Previous assessments"],
        "Throughout audit period", "₦80,000 - ₦300,000"
    ))
    s.append(svc(
        "Tax Investigation Defense", "tax-investigation-defense", "tax",
        "Tax Services", "Tax Audit & Investigation",
        "Legal and technical defense against tax investigations including back-duty audits.",
        ["Investigation defense strategy", "Documentation support", "Representation", "Negotiation support"],
        ["Assess investigation scope", "Develop defense strategy", "Prepare representations", "Negotiate settlement"],
        ["All tax records (6+ years)", "Financial statements", "Bank statements", "Board resolutions"],
        "4-12 weeks", "₦200,000 - ₦1,000,000"
    ))
    s.append(svc(
        "Tax Dispute Resolution", "tax-dispute-resolution", "tax",
        "Tax Services", "Tax Audit & Investigation",
        "Resolution of tax disputes through objection, appeal and alternative dispute resolution.",
        ["Objection preparation", "Appeal support", "ADR representation", "Settlement negotiation"],
        ["Review disputed assessment", "Prepare notice of objection", "File appeal if needed", "Represent at hearings"],
        ["Tax assessment notice", "Objection grounds", "Supporting evidence", "Legal precedents"],
        "4-12 weeks", "₦150,000 - ₦800,000"
    ))
    s.append(svc(
        "Tax Reconciliation Services", "tax-reconciliation", "tax",
        "Tax Services", "Tax Audit & Investigation",
        "Reconciliation of tax payments, returns and assessments to resolve discrepancies.",
        ["Payment vs assessment reconciliation", "Ledger review", "Discrepancy resolution", "Adjusted returns preparation"],
        ["Obtain tax payment history", "Compare with returns", "Identify discrepancies", "Prepare reconciliation report"],
        ["Tax receipts", "Bank statements", "Filed returns", "Tax assessment notices"],
        "5-10 business days", "₦50,000 - ₦200,000"
    ))
    # ── Subcategory: Specialized Tax Services ──
    s.append(svc(
        "Deferred Tax Computation", "deferred-tax", "tax",
        "Tax Services", "Specialized Tax Services",
        "Deferred tax computation in accordance with IAS 12 for financial reporting purposes.",
        ["Temporary difference analysis", "Deferred tax asset/liability computation", "IFRS compliance", "Disclosure support"],
        ["Identify timing differences", "Compute deferred tax", "Prepare schedule", "Support audit review"],
        ["Financial statements", "Fixed asset register", "Tax computations", "Prior year deferred tax schedules"],
        "5-10 business days", "₦80,000 - ₦300,000"
    ))
    s.append(svc(
        "Tax Due Diligence", "tax-due-diligence", "tax",
        "Tax Services", "Specialized Tax Services",
        "Comprehensive tax due diligence for transactions, investments or compliance purposes.",
        ["Full tax records review", "Risk identification", "Exposure quantification", "Due diligence report"],
        ["Review all tax records", "Identify risks and exposures", "Quantify potential liabilities", "Prepare DD report"],
        ["Tax returns (5+ years)", "Financial statements", "Audit reports", "Correspondence with tax authorities"],
        "10-20 business days", "₦200,000 - ₦800,000"
    ))
    s.append(svc(
        "VAT Refund Processing", "vat-refund", "tax",
        "Tax Services", "Specialized Tax Services",
        "VAT refund application processing including documentation and follow-up with FIRS.",
        ["Refund eligibility assessment", "Documentation preparation", "Application filing", "FIRS follow-up"],
        ["Assess refund eligibility", "Compile supporting documents", "Submit application", "Follow up with FIRS"],
        ["VAT returns (period)", "Purchase invoices", "Proof of exports (if applicable)", "Bank statements"],
        "4-12 weeks", "₦80,000 - ₦300,000"
    ))
    s.append(svc(
        "Pioneer Status Incentive Application", "pioneer-status", "tax",
        "Tax Services", "Specialized Tax Services",
        "Application for pioneer status incentive granting tax holiday for qualifying industries.",
        ["Eligibility assessment", "Application preparation", "FIRS/NIPC liaison", "Pioneer certificate follow-up"],
        ["Assess product eligibility", "Prepare application", "Submit to NIPC/FIRS", "Follow up for approval"],
        ["Business plan", "Feasibility study", "Incorporation documents", "Product/service details"],
        "3-6 months", "₦300,000 - ₦1,000,000"
    ))
    s.append(svc(
        "Free Trade Zone Tax Advisory", "free-trade-zone", "tax",
        "Tax Services", "Specialized Tax Services",
        "Tax advisory for companies operating in or establishing in Nigerian free trade zones.",
        ["FTZ incentive analysis", "Compliance advisory", "Customs duty advisory", "Operational structuring"],
        ["Review FTZ regulations", "Analyze applicable incentives", "Advise on compliance", "Prepare advisory report"],
        ["FTZ license", "Operational plan", "Import/export documentation", "Financial projections"],
        "10-20 business days", "₦200,000 - ₦600,000"
    ))

    # ═══════════════════════════════════════════
    # DIVISION 2: BUSINESS SERVICES
    # ═══════════════════════════════════════════
    # ── Subcategory: Business Formation & Structuring ──
    s.append(svc(
        "Company Registration (CAC)", "cac-registration", "business",
        "Business Services", "Business Formation & Structuring",
        "Complete CAC registration for Business Name, Limited Liability Company or Incorporated Trustees.",
        ["Name search/reservation", "CAC registration", "TIN registration", "Certificate of incorporation", "Company seal"],
        ["Name availability search", "Document preparation", "CAC portal submission", "Fee payment", "Certificate collection"],
        ["Valid ID", "Passport photographs", "Utility bill", "Memorandum & Articles", "Shareholder/Director information"],
        "5-7 business days", "₦50,000 - ₦150,000",
        [{"name": "Company Registration", "price": 150000, "description": "Full CAC company registration"}]
    ))
    s.append(svc(
        "Business Name Registration", "business-name-registration", "business",
        "Business Services", "Business Formation & Structuring",
        "Registration of business name with CAC for sole proprietorships and partnerships.",
        ["Name search", "Registration filing", "Certificate issuance", "TIN registration"],
        ["Search business name", "Prepare forms", "File with CAC", "Obtain certificate"],
        ["Valid ID", "Passport photograph", "Business address proof"],
        "3-5 business days", "₦25,000 - ₦60,000",
        [{"name": "Business Name Registration", "price": 75000, "description": "CAC business name registration"}]
    ))
    s.append(svc(
        "NGO/Incorporated Trustee Registration", "ngo-registration", "business",
        "Business Services", "Business Formation & Structuring",
        "Registration of NGOs, trusts and non-profit organizations with CAC and related bodies.",
        ["Name reservation", "Trust deed preparation", "CAC registration", "SCUML registration"],
        ["Reserve name", "Prepare trust deed", "Submit to CAC", "Obtain certificate"],
        ["Trust deed", "Trustee details and IDs", "Registered address proof", "Mission/objectives document"],
        "10-20 business days", "₦80,000 - ₦200,000"
    ))
    s.append(svc(
        "Foreign Company Registration", "foreign-company-registration", "business",
        "Business Services", "Business Formation & Structuring",
        "Registration of foreign companies establishing presence in Nigeria through branches or subsidiaries.",
        ["Branch registration", "Subsidiary incorporation", "Business permit", "Registration with authorities"],
        ["Determine entry strategy", "Prepare registration documents", "File with CAC", "Obtain business permit"],
        ["Parent company documents", "Board resolution", "Business plan", "Registered office address"],
        "14-30 business days", "₦200,000 - ₦500,000"
    ))
    s.append(svc(
        "Corporate Restructuring", "corporate-restructuring", "business",
        "Business Services", "Business Formation & Structuring",
        "Corporate restructuring including change of name, share capital changes and director changes.",
        ["Name change", "Share capital alteration", "Director changes", "CAC filings"],
        ["Board resolution", "Prepare special resolution", "File with CAC", "Obtain amended certificates"],
        ["Current CAC certificate", "Board/shareholder resolutions", "Updated director details", "Share allotment forms"],
        "7-21 business days", "₦80,000 - ₦350,000"
    ))
    s.append(svc(
        "Corporate Secretarial Services", "corporate-secretarial", "business",
        "Business Services", "Business Formation & Structuring",
        "Company secretarial services including board meeting minutes, register maintenance and statutory filings.",
        ["Register maintenance", "Board resolution drafting", "Meeting minutes", "Annual returns filing"],
        ["Maintain statutory registers", "Draft resolutions", "Minutes of meetings", "Annual filings"],
        ["Certificate of incorporation", "Shareholder register", "Director register", "Previous minutes"],
        "Ongoing/monthly", "₦30,000 - ₦100,000/month"
    ))
    # ── Subcategory: Financial & Accounting Services ──
    s.append(svc(
        "Bookkeeping Services", "bookkeeping", "business",
        "Business Services", "Financial & Accounting Services",
        "Professional bookkeeping for SMEs including transaction recording and account reconciliation.",
        ["Transaction recording", "Account reconciliation", "Ledger maintenance", "Monthly financial reports"],
        ["Set up chart of accounts", "Record transactions", "Reconcile accounts", "Prepare monthly reports"],
        ["Bank statements", "Sales/purchase invoices", "Receipts and payment records", "Previous accounting records"],
        "Ongoing/monthly", "₦30,000 - ₦100,000/month",
        [
            {"name": "Small", "price": 50000, "description": "Small business bookkeeping"},
            {"name": "Medium", "price": 80000, "description": "Medium business bookkeeping"},
            {"name": "Large (301–700 transactions)", "price": 100000, "description": "High-volume bookkeeping (301–700 transactions)"},
        ],
        is_recurring=True, billing_cycle="monthly", base_price_per_cycle=50000,
    ))
    s.append(svc(
        "Bank Reconciliation", "bank-reconciliation", "business",
        "Business Services", "Financial & Accounting Services",
        "Reconcile bank statements with internal financial records to ensure accuracy and identify discrepancies.",
        ["Bank statement matching", "Discrepancy identification", "Reconciliation reporting", "Exception tracking"],
        ["Collect bank statements", "Match transactions", "Identify discrepancies", "Prepare reconciliation report"],
        ["Bank statements", "Cash book / ledger", "Previous reconciliation reports"],
        "3-5 business days", "₦50,000 per bank account",
        [{"name": "Per Bank Account", "price": 50000, "description": "₦50,000 per bank account"}]
    ))
    s.append(svc(
        "Accounts Payable Management", "accounts-payable", "business",
        "Business Services", "Financial & Accounting Services",
        "Complete management of accounts payable including invoice processing, vendor payments, and aging analysis.",
        ["Invoice processing", "Payment scheduling", "Vendor management", "Aging analysis", "Payment reporting"],
        ["Receive invoices", "Verify and approve", "Schedule payments", "Process payments", "Generate aging report"],
        ["Purchase orders", "Invoices", "Vendor bank details", "Payment authorization"],
        "Ongoing/monthly", "₦100,000",
        [{"name": "Standard", "price": 100000, "description": "Full accounts payable management"}]
    ))
    s.append(svc(
        "Accounts Receivable Management", "accounts-receivable", "business",
        "Business Services", "Financial & Accounting Services",
        "Management of accounts receivable including invoicing, collections, credit control, and aging analysis.",
        ["Invoice generation", "Collections management", "Credit control", "Aging analysis", "Bad debt provisioning"],
        ["Generate invoices", "Send reminders", "Track collections", "Update aging report", "Provision for bad debts"],
        ["Sales records", "Customer details", "Payment terms", "Previous receivable records"],
        "Ongoing/monthly", "₦100,000",
        [{"name": "Standard", "price": 100000, "description": "Full accounts receivable management"}]
    ))
    s.append(svc(
        "Inventory Reconciliation", "inventory-reconciliation", "business",
        "Business Services", "Financial & Accounting Services",
        "Physical inventory count reconciliation with book records to identify and account for discrepancies.",
        ["Physical count coordination", "Book-to-physical reconciliation", "Variance analysis", "Adjustment entries"],
        ["Plan physical count", "Conduct count", "Compare with books", "Investigate variances", "Post adjustments"],
        ["Inventory register", "Warehouse location list", "Previous count sheets", "Stock movement records"],
        "5-10 business days", "₦100,000",
        [{"name": "Standard", "price": 100000, "description": "Complete inventory reconciliation"}]
    ))
    s.append(svc(
        "General Ledger Review", "general-ledger-review", "business",
        "Business Services", "Financial & Accounting Services",
        "Thorough review of the general ledger to ensure accuracy, completeness, and compliance with accounting standards.",
        ["Account analysis", "Transaction verification", "Error identification", "Reclassification entries"],
        ["Extract GL report", "Analyze account balances", "Verify transactions", "Identify errors", "Prepare findings report"],
        ["General ledger extract", "Chart of accounts", "Supporting documentation", "Prior period GL"],
        "5-10 business days", "₦150,000",
        [{"name": "Standard", "price": 150000, "description": "Comprehensive general ledger review"}]
    ))
    s.append(svc(
        "Trial Balance Preparation", "trial-balance", "business",
        "Business Services", "Financial & Accounting Services",
        "Preparation of trial balance from general ledger to verify debits equal credits and identify posting errors.",
        ["Account balance extraction", "Debit/credit verification", "Error identification", "Adjustment recommendations"],
        ["Extract account balances", "Verify arithmetic accuracy", "Identify imbalances", "Recommend adjustments"],
        ["General ledger", "Chart of accounts", "Adjustment entries", "Prior period trial balance"],
        "3-5 business days", "₦200,000",
        [{"name": "Standard", "price": 200000, "description": "Complete trial balance preparation"}]
    ))
    s.append(svc(
        "Outsourced Accounting", "outsourced-accounting", "business",
        "Business Services", "Financial & Accounting Services",
        "Full outsourced accounting function including payable/receivable management and financial reporting.",
        ["Accounts payable management", "Accounts receivable management", "Bank reconciliation", "Monthly management accounts"],
        ["Receive source documents", "Process transactions", "Reconcile accounts", "Produce management accounts"],
        ["All accounting source documents", "Bank statements", "Vendor/customer details", "Prior period accounts"],
        "Ongoing/monthly", "₦80,000 - ₦300,000/month",
        is_recurring=True, billing_cycle="monthly", base_price_per_cycle=80000,
    ))
    s.append(svc(
        "Financial Statement Preparation", "financial-statement", "business",
        "Business Services", "Financial & Accounting Services",
        "Preparation of financial statements in compliance with IFRS or local GAAP.",
        ["Trial balance review", "Adjusting entries", "Financial statement preparation", "IFRS compliance", "Director's report"],
        ["Review trial balance", "Make adjusting entries", "Prepare financial statements", "Prepare notes and disclosures"],
        ["Trial balance", "General ledger", "Fixed asset register", "Bank confirmations", "Debtor/creditor schedules"],
        "10-20 business days", "₦100,000 - ₦400,000",
        [
            {"name": "Annual Financial Statements", "price": 200000, "description": "Full annual financial statements preparation"},
            {"name": "Management Accounts", "price": 100000, "description": "Monthly/quarterly management accounts"},
            {"name": "Financial Statement Review", "price": 100000, "description": "Review and assurance of financial statements"},
        ]
    ))
    s.append(svc(
        "Management Accounts Preparation", "management-accounts", "business",
        "Business Services", "Financial & Accounting Services",
        "Monthly/quarterly management accounts for informed business decision-making.",
        ["Profit & loss statement", "Balance sheet", "Cash flow statement", "Budget vs actual analysis", "KPI dashboard"],
        ["Extract trial balance", "Prepare management accounts", "Variance analysis", "Management report"],
        ["Accounting records", "Budget/forecast", "Previous management accounts", "Operational data"],
        "5-10 business days", "₦50,000 - ₦200,000/month"
    ))
    s.append(svc(
        "Payroll Management", "payroll-management", "business",
        "Business Services", "Financial & Accounting Services",
        "End-to-end payroll processing including PAYE computation, pension and statutory deductions.",
        ["Payroll computation", "PAYE deductions", "Pension remittance", "Payroll reports", "Payslip generation"],
        ["Gather employee data", "Compute payroll", "Deduct statutory contributions", "Process payments", "Generate payslips"],
        ["Employee register", "Salary structure", "Attendance records", "Previous payroll data"],
        "Ongoing/monthly", "₦20,000 - ₦80,000/month",
        [
            {"name": "Up to 20 Staff", "price": 2500, "description": "₦2,500 per staff (up to 20 staff)"},
            {"name": "21–50 Staff", "price": 2200, "description": "₦2,200 per staff (21–50 staff)"},
            {"name": "51–100 Staff", "price": 2000, "description": "₦2,000 per staff (51–100 staff)"},
            {"name": "Pension Schedule", "price": 50000, "description": "Pension contribution schedule preparation"},
            {"name": "PAYE Schedule", "price": 50000, "description": "PAYE tax schedule preparation"},
            {"name": "NHF Schedule", "price": 30000, "description": "NHF contribution schedule preparation"},
            {"name": "NSITF Schedule", "price": 30000, "description": "NSITF contribution schedule preparation"},
            {"name": "Payroll Reports", "price": 40000, "description": "Comprehensive payroll reporting"},
        ],
        is_recurring=True, billing_cycle="monthly", base_price_per_cycle=50000,
    ))
    # ── Subcategory: Business Advisory Services ──
    s.append(svc(
        "Business Plan Preparation", "business-plan", "business",
        "Business Services", "Business Advisory Services",
        "Professional business plan preparation for startups, funding applications and strategic planning.",
        ["Executive summary", "Market analysis", "Financial projections", "Operational plan", "Funding strategy"],
        ["Understand business model", "Market research", "Financial modeling", "Draft business plan"],
        ["Business idea details", "Market research data", "Financial assumptions", "Management bios"],
        "10-20 business days", "₦100,000 - ₦350,000"
    ))
    s.append(svc(
        "Feasibility Studies", "feasibility-study", "business",
        "Business Services", "Business Advisory Services",
        "Comprehensive feasibility studies for new ventures, projects or expansions.",
        ["Market feasibility", "Technical feasibility", "Financial analysis", "Risk assessment", "Recommendations"],
        ["Market research", "Technical analysis", "Financial modeling", "Risk evaluation", "Report preparation"],
        ["Project concept", "Market data", "Cost estimates", "Technical specifications"],
        "14-30 business days", "₦150,000 - ₦500,000"
    ))
    s.append(svc(
        "Financial Modeling", "financial-modeling", "business",
        "Business Services", "Business Advisory Services",
        "Custom financial models for valuation, fundraising, budgeting and scenario analysis.",
        ["3-statement model", "DCF valuation", "Scenario analysis", "Sensitivity tables", "Dashboard outputs"],
        ["Define model structure", "Input assumptions", "Build calculations", "Test scenarios", "Final model delivery"],
        ["Historical financials", "Business assumptions", "Market data", "Model requirements brief"],
        "10-20 business days", "₦150,000 - ₦500,000"
    ))
    s.append(svc(
        "Business Valuation", "business-valuation", "business",
        "Business Services", "Business Advisory Services",
        "Business valuation for investment, sale, tax or strategic purposes using multiple methodologies.",
        ["DCF valuation", "Market comparable analysis", "Asset-based valuation", "Valuation report"],
        ["Review financials and projections", "Select methodology", "Perform valuation", "Prepare report"],
        ["Financial statements (3-5 years)", "Financial projections", "Market data", "Industry reports"],
        "10-20 business days", "₦200,000 - ₦800,000"
    ))
    # ── Subcategory: Transaction & Investment Support ──
    s.append(svc(
        "Due Diligence Services", "due-diligence", "business",
        "Business Services", "Transaction & Investment Support",
        "Financial, tax and operational due diligence for transactions and investments.",
        ["Financial due diligence", "Tax due diligence", "Operational review", "Risk identification", "Due diligence report"],
        ["Scope determination", "Data room review", "Management meetings", "Report preparation"],
        ["Target company records", "Financial statements (3+ years)", "Contracts and agreements", "Regulatory filings"],
        "2-6 weeks", "₦300,000 - ₦1,500,000"
    ))
    s.append(svc(
        "Investor Readiness Support", "investor-readiness", "business",
        "Business Services", "Transaction & Investment Support",
        "Preparation services to make your business investor-ready including documentation and materials.",
        ["Pitch deck preparation", "Data room setup", "Financial restructuring", "Valuation support", "Investor targeting"],
        ["Business review", "Pitch deck development", "Data room compilation", "Investor introduction"],
        ["Business plan", "Financial statements", "Market analysis", "Team information"],
        "14-30 business days", "₦150,000 - ₦500,000"
    ))
    # ── Subcategory: Human Capital & Outsourcing ──
    s.append(svc(
        "HR Compliance Support", "hr-compliance", "business",
        "Business Services", "Human Capital & Outsourcing",
        "HR compliance advisory including employment contracts, policies and statutory compliance.",
        ["Employment contract review", "HR policy development", "Statutory compliance check", "Employee handbook"],
        ["Review current HR practices", "Identify gaps", "Develop policies", "Implement compliance framework"],
        ["Current employment contracts", "HR policies (if any)", "Staff records", "Company policies"],
        "10-20 business days", "₦80,000 - ₦300,000"
    ))

    # ═══════════════════════════════════════════
    # DIVISION 3: REGULATORY SERVICES
    # ═══════════════════════════════════════════
    # ── Subcategory: Corporate Regulatory Compliance ──
    s.append(svc(
        "CAC Annual Returns Filing", "cac-annual-returns", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "Annual returns filing with CAC to maintain good standing and avoid penalties.",
        ["Returns preparation", "Financial summary", "CAC portal filing", "Compliance certificate"],
        ["Update company information", "Prepare financial summary", "File with CAC", "Download certificate"],
        ["Certificate of incorporation", "Previous annual returns", "Financial statements", "Director/shareholder updates"],
        "3-5 business days", "₦30,000 - ₦80,000",
        [{"name": "Annual Returns", "price": 50000, "description": "Annual returns filing with CAC"}]
    ))
    s.append(svc(
        "Beneficial Ownership Compliance", "beneficial-ownership", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "Beneficial ownership register maintenance and filing with CAC as required by law.",
        ["BO register preparation", "Ownership analysis", "CAC filing", "Annual updates"],
        ["Identify beneficial owners", "Prepare ownership register", "File with CAC", "Annual review"],
        ["Shareholder register", "Director information", "Ownership structure chart", "Identification documents"],
        "5-10 business days", "₦40,000 - ₦100,000"
    ))
    s.append(svc(
        "SCUML Registration", "scuml-registration", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "Registration with Special Control Unit against Money Laundering for designated non-financial businesses.",
        ["SCUML registration", "Annual compliance filing", "AML policy development", "Training support"],
        ["Determine applicability", "Prepare registration documents", "Submit to SCUML", "Obtain certificate"],
        ["CAC certificate", "Business description", "Director/owner details", "AML policy document"],
        "7-14 business days", "₦40,000 - ₦120,000",
        [{"name": "SCUML Registration", "price": 50000, "description": "SCUML compliance registration"}]
    ))
    s.append(svc(
        "NSITF Compliance", "nsitf-compliance", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "Nigeria Social Insurance Trust Fund registration, contributions and returns filing.",
        ["NSITF registration", "Monthly contributions", "Annual returns", "Compliance certificate"],
        ["Register with NSITF", "Compute monthly contributions", "Remit contributions", "File annual returns"],
        ["Employee register", "Payroll records", "CAC certificate", "Previous NSITF records"],
        "Ongoing/monthly", "₦15,000 - ₦50,000/month"
    ))
    s.append(svc(
        "ITF Compliance", "itf-compliance", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "Industrial Training Fund registration, levy payment and training plan filing.",
        ["ITF registration", "Annual levy computation", "Training plan submission", "Reimbursement claims"],
        ["Register with ITF", "Compute 1% levy", "Submit training plan", "File annual returns"],
        ["Employee register", "Payroll data", "CAC certificate", "Training records"],
        "5-10 business days / annual", "₦20,000 - ₦80,000/year"
    ))
    s.append(svc(
        "PENCOM Compliance", "pencom-compliance", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "Pension commission compliance including RSA registration and contribution remittance.",
        ["RSA registration", "Monthly contribution management", "Annual returns", "Compliance certificate"],
        ["Register employees for RSA", "Compute and remit contributions", "File returns", "Obtain compliance certificate"],
        ["Employee register", "Payroll data", "RSA numbers", "Previous remittance records"],
        "Ongoing/monthly", "₦20,000 - ₦60,000/month"
    ))
    s.append(svc(
        "Data Protection Compliance (NDPC)", "data-protection", "regulatory",
        "Regulatory Services", "Corporate Regulatory Compliance",
        "NDPC registration, data protection framework implementation and compliance filing.",
        ["DPC registration", "Data audit", "Policy development", "Compliance filing", "DPA training"],
        ["Register with NDPC", "Conduct data audit", "Develop privacy policy", "Implement controls", "File compliance returns"],
        ["Company information", "Data processing register", "Current privacy policies", "Consent mechanisms"],
        "14-30 business days", "₦100,000 - ₦400,000"
    ))
    # ── Subcategory: Industry-Specific Regulatory Support ──
    s.append(svc(
        "NAFDAC Registration", "nafdac-registration", "regulatory",
        "Regulatory Services", "Industry-Specific Regulatory Support",
        "NAFDAC product registration for food, drugs, cosmetics, chemicals and medical devices.",
        ["Product registration", "Label review", "GMP certification support", "Renewal processing"],
        ["Product analysis", "Document preparation", "NAFDAC submission", "Follow-up and certification"],
        ["Product formulation", "Lab analysis report", "Factory GMP documents", "Label/package details"],
        "3-12 months", "₦200,000 - ₦1,000,000"
    ))
    s.append(svc(
        "SON Certification", "son-certification", "regulatory",
        "Regulatory Services", "Industry-Specific Regulatory Support",
        "Standards Organization of Nigeria certification including SONCAP and product standards.",
        ["SONCAP certification", "Product standards compliance", "Quality management", "Import clearance support"],
        ["Product assessment", "Testing coordination", "SONCAP application", "Certificate issuance"],
        ["Product specification", "Test reports", "Factory license", "Import/export documents"],
        "2-8 weeks", "₦100,000 - ₦500,000"
    ))
    # ── Subcategory: Government Licensing & Permits ──
    s.append(svc(
        "Expatriate Quota Processing", "expatriate-quota", "regulatory",
        "Regulatory Services", "Government Licensing & Permits",
        "Expatriate quota application, renewal and administration with Ministry of Interior.",
        ["Quota application", "Renewal processing", "CERPAC support", "Compliance advisory"],
        ["Determine eligibility", "Prepare application", "Submit to Ministry", "Follow up for approval"],
        ["Company CAC documents", "Business justification", "Expatriate details", "Local employee training plan"],
        "2-6 months", "₦300,000 - ₦1,000,000"
    ))
    s.append(svc(
        "Business Permits Processing", "business-permit", "regulatory",
        "Regulatory Services", "Government Licensing & Permits",
        "Business permit application and renewal for foreign-owned companies operating in Nigeria.",
        ["Permit application", "Renewal processing", "Regulatory liaison", "Compliance support"],
        ["Determine applicable permit", "Prepare application", "Submit to authority", "Follow up"],
        ["CAC documents", "Business plan", "Shareholder details", "Tax clearance certificate"],
        "4-12 weeks", "₦150,000 - ₦500,000"
    ))

    # ═══════════════════════════════════════════
    # DIVISION 4: MODERN SERVICES
    # ═══════════════════════════════════════════
    # ── Subcategory: Digital & Technology Compliance ──
    s.append(svc(
        "E-Invoicing Implementation", "e-invoicing", "digital",
        "Modern Services", "Digital & Technology Compliance",
        "E-invoicing system implementation for tax compliance including FIRS e-invoice integration.",
        ["E-invoice system setup", "FIRS integration", "Invoice generation", "Compliance reporting"],
        ["Assess current invoicing", "Select e-invoicing platform", "Configure and integrate", "Go-live and training"],
        ["Current invoice templates", "ERP/system details", "Tax registration info", "Customer/supplier data"],
        "2-6 weeks", "₦200,000 - ₦800,000"
    ))
    s.append(svc(
        "ERP Tax Configuration", "erp-tax-configuration", "digital",
        "Modern Services", "Digital & Technology Compliance",
        "Tax configuration and optimization within ERP systems for automated tax compliance.",
        ["Tax code setup", "Withholding tax configuration", "VAT configuration", "Automated return generation"],
        ["Review ERP tax setup", "Configure tax codes", "Test configuration", "Document and train"],
        ["ERP system details", "Tax registration info", "Current chart of accounts", "Transaction data samples"],
        "2-4 weeks", "₦150,000 - ₦600,000"
    ))
    s.append(svc(
        "Automation of Tax Reporting", "tax-reporting-automation", "digital",
        "Modern Services", "Digital & Technology Compliance",
        "Automate tax data extraction, computation and report generation to eliminate manual processes.",
        ["Tax data extraction automation", "Computation automation", "Report generation", "Dashboard setup"],
        ["Map data sources", "Build automation scripts", "Test outputs", "Deploy and train"],
        ["Tax computation methodology", "Data source details", "Report templates", "IT infrastructure details"],
        "3-8 weeks", "₦250,000 - ₦1,000,000"
    ))
    # ── Subcategory: Risk & Governance Services ──
    s.append(svc(
        "Enterprise Risk Management", "erm", "risk",
        "Modern Services", "Risk & Governance Services",
        "Enterprise risk management framework development including risk identification and mitigation.",
        ["Risk assessment", "Risk register development", "Mitigation planning", "Monitoring framework", "Board reporting"],
        ["Risk identification workshops", "Risk analysis", "Control design", "Report preparation"],
        ["Business processes documentation", "Strategic plan", "Previous risk reports", "Industry risk data"],
        "4-8 weeks", "₦300,000 - ₦1,000,000"
    ))
    s.append(svc(
        "Internal Audit Outsourcing", "internal-audit", "risk",
        "Modern Services", "Risk & Governance Services",
        "Outsourced internal audit function including risk-based audit planning and execution.",
        ["Audit planning", "Fieldwork execution", "Finding reporting", "Recommendation tracking"],
        ["Develop audit plan", "Execute audit procedures", "Document findings", "Report to management"],
        ["Financial records", "Process documentation", "Previous audit reports", "Policies and procedures"],
        "Ongoing/quarterly", "₦200,000 - ₦500,000/quarter"
    ))
    return s

async def seed_database():
    print("Seeding database...")
    
    users_added = 0
    if not await db.users.find_one({"email": "admin@tbrsolutions.ng"}):
        await db.users.insert_one({
            "id": str(uuid.uuid4()), "email": "admin@tbrsolutions.ng",
            "full_name": "TBR Admin", "phone": "+234 800 000 0000",
            "company_name": "TBR Solutions", "role": "super_admin",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True, "created_at": datetime.now(timezone.utc).isoformat()
        })
        users_added += 1
        print("[OK] Admin user created: admin@tbrsolutions.ng / admin123")
    
    if not await db.users.find_one({"email": "client@test.com"}):
        await db.users.insert_one({
            "id": str(uuid.uuid4()), "email": "client@test.com",
            "full_name": "Test Client", "phone": "+234 800 111 2222",
            "company_name": "Test Company Ltd", "role": "client",
            "hashed_password": get_password_hash("client123"),
            "is_active": True, "created_at": datetime.now(timezone.utc).isoformat()
        })
        users_added += 1
        print("[OK] Test client created: client@test.com / client123")
    
    if users_added == 0:
        print("[SKIP] Users already exist")
    
    old_count = await db.services.count_documents({"division": {"$exists": False}})
    if old_count > 0:
        await db.services.delete_many({})
        print(f"[CLEAN] Removed {old_count} old-format services")

    svc_count = await db.services.count_documents({})
    if svc_count == 0:
        services = build_services()
        await db.services.insert_many(services)
        print(f"[OK] Seeded {len(services)} services across 4 divisions")
    else:
        print(f"[SKIP] {svc_count} services already exist")
    
    industry_count = await db.industries.count_documents({})
    if industry_count == 0:
        industries = [
            {"id": str(uuid.uuid4()), "title": "Financial Services", "slug": "financial-services",
             "description": "Regulatory and compliance solutions for banks, fintechs, insurance and investment firms.",
             "challenges": ["Complex CBN/SEC regulations", "AML/CFT compliance", "Licensing approvals", "Capital adequacy reporting"],
             "solutions": ["Regulatory compliance management", "License application/renewals", "Audit and risk advisory", "Policy development"],
             "icon": "landmark", "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "title": "Oil & Gas", "slug": "oil-gas",
             "description": "Advisory for upstream, midstream and downstream oil and gas operations.",
             "challenges": ["NUPRC compliance", "Environmental regulations", "Joint venture agreements", "Host community obligations"],
             "solutions": ["Regulatory compliance", "Contract review", "Tax optimization", "Stakeholder management"],
             "icon": "fuel", "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "title": "Technology & Startups", "slug": "technology-startups",
             "description": "Agile compliance and growth advisory for tech companies and startups.",
             "challenges": ["Fast regulatory changes", "Data protection (NDPC)", "IP protection", "Investor readiness"],
             "solutions": ["Company structuring", "IP registration", "NDPC compliance", "Due diligence support"],
             "icon": "code", "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "title": "Manufacturing & FMCG", "slug": "manufacturing-fmcg",
             "description": "Regulatory support for manufacturing, product registration and distribution.",
             "challenges": ["NAFDAC registration", "SON certification", "Import/export compliance", "Environmental permits"],
             "solutions": ["Product registration", "Quality certification", "Trade license management", "Supply chain compliance"],
             "icon": "factory", "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "title": "SMEs & Startups", "slug": "smes-startups",
             "description": "Affordable compliance, tax and business advisory packages for small businesses.",
             "challenges": ["Limited budget for compliance", "Lack of in-house expertise", "Regulatory complexity", "Growth support"],
             "solutions": ["Affordable compliance packages", "Outsourced accounting", "Business advisory", "Tax planning"],
             "icon": "building2", "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        await db.industries.insert_many(industries)
        print(f"[OK] Seeded {len(industries)} industries")
    else:
        print(f"[SKIP] {industry_count} industries already exist")
    
    if await db.resources.count_documents({}) == 0:
        await db.resources.insert_many([
            {"id": str(uuid.uuid4()), "title": "2026 Tax Compliance Guide for Nigerian Businesses",
             "slug": "2026-tax-compliance-guide", "category": "Tax Updates",
             "excerpt": "Essential tax compliance requirements and deadlines for businesses operating in Nigeria in 2026.",
             "content": "Full article content here...", "author": "TBR Tax Advisory Team",
             "tags": ["tax", "compliance", "2026"],
             "featured_image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",
             "views": 0, "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "title": "Understanding CAC's New Digital Filing System",
             "slug": "cac-digital-filing-system", "category": "Regulatory Updates",
             "excerpt": "A guide to navigating the CAC's updated digital filing platform.",
             "content": "Full article content here...", "author": "TBR Compliance Team",
             "tags": ["CAC", "filing", "digital"],
             "featured_image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85",
             "views": 0, "created_at": datetime.now(timezone.utc).isoformat()},
        ])
        print("[OK] Seeded 2 resources")
    else:
        print("[SKIP] Resources already exist")
    
    print("\n[DONE] Database seeding completed!")
    print("Admin: admin@tbrsolutions.ng / admin123")
    print("Client: client@test.com / client123")

if __name__ == "__main__":
    asyncio.run(seed_database())
