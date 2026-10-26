import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


C1 = """<p>Nigeria has introduced a fundamentally rewritten set of tax rules for multinational enterprises (MNEs), effective from 1 January 2026. The new framework departs significantly from the old regime: some provisions follow the standard OECD model, while others adopt incorporated models that depart from the norm. The OECD principle of limiting taxation to the level of economic activities within a country is now applied alongside aggressive nexus rules that capture income with only minimal connection to Nigeria.</p>
<p>The law defines an MNE as a company operating in more than one jurisdiction. As a result, provisions that previously applied only to foreign companies now also apply to local companies with an international footprint.</p>
<h2>1. Expanded exposure to Nigerian tax</h2>
<p>The Nigeria Tax Act (NTA) broadens the types of transactions and income streams that fall within Nigeria's tax net:</p>
<ul>
<li><strong>Expanded tax nexus.</strong> Taxation now extends beyond companies with a permanent establishment (PE) or significant economic presence (SEP). SEP captures companies deriving income from Nigeria through digital platforms with no physical presence in the country.</li>
<li><strong>Income from services.</strong> Foreign companies without any presence in Nigeria are taxable on payments received for services provided to residents of Nigeria (and to nonresidents with a Nigerian PE). Foreign insurers similarly pay tax on premiums received from Nigeria (NTA, ss. 17(3)(b), 17(3)(c)).</li>
<li><strong>Income from goods.</strong> Tax is assessed on profit from the direct supply of goods by foreign companies with a PE to residents of Nigeria, with profit attributed to the supplier's PE (NTA, s. 17(5)(c)).</li>
<li><strong>Share disposals.</strong> Residents pay tax on gains from the disposal of shares in foreign companies where more than 50% of the share value derives from underlying Nigerian assets or immovable chargeable assets (NTA, ss. 46(f), 46(g), 47). Change-of-control disposals triggering changes in Nigerian ownership are also caught.</li>
<li><strong>Disposal of a trade or business.</strong> Nonresidents pay tax on gains from disposing of any trade, business, profession or vocation carried on in Nigeria and assets located there (NTA, s. 17(2)).</li>
<li><strong>Place of management.</strong> The PE definition now includes foreign companies with a place of management in Nigeria, adopting standard double-tax-treaty conditions for creating a taxable presence (NTA, s. 17(9)).</li>
</ul>
<h2>2. Minimum profit margin</h2>
<p>Where a nonresident company operates through a PE or SEP in Nigeria, attributable profit is taxed at a margin not below that of the nonresident company itself, and the PE or SEP is deemed to have the same credit rating as the nonresident (NTA, ss. 17(5)(a), 17(6)-(7)). Only expenses incurred to produce attributable taxable profits are deductible (NTA, s. 17(5)(d)); expenses paid to connected parties for royalties, fees or similar items are not (NTA, s. 17(5)(e)).</p>
<h2>3. Minimum tax and BEPS Pillar Two</h2>
<p>The law incorporates the OECD/G20 BEPS Pillar Two framework for in-scope MNEs (NTA, ss. 6(3), 57(1)-(2)). For other nonresident companies, minimum tax is the higher of tax suffered at source or 4% of gross Nigerian-source revenue (NTA, s. 17(8)).</p>
<h2>4. Anti-avoidance, CFC rules and reliefs</h2>
<p>Controlled Foreign Company (CFC) rules allow the tax authority to attribute to a Nigerian company a proportion of the profits of a foreign company it controls, where attributing the profit does not impair the foreign company's operations (NTA, s. 6(2)).</p>
<p><strong>Double taxation relief.</strong> MNEs may claim double tax relief regardless of whether a double tax agreement exists with the host country (NTA, ss. 120, 121(2)), subject to an exception for MNEs complying with the global minimum tax rules (NTA, s. 120(8)).</p>
<p><strong>Recoverable input VAT.</strong> Taxpayers can now claim all input VAT against output VAT (NTA, s. 156(5)), and VAT refunds are due within 30 days in cash or as set-off against other tax liabilities (NTAA, s. 56).</p>
<h2>5. Repeal of major tax incentives</h2>
<p>Provisions granting tax holidays and the fiscal/monetary incentives for enterprises in free trade or export processing zones have been repealed (NTA, ss. 197(2)-(3)), a change that may affect foreign direct investment flows.</p>
<h2>6. Tightened compliance and the NRS</h2>
<ul>
<li>All taxpayers must obtain a Tax Identification Number (TIN), and banks must ensure the TIN is provided (NTAA, ss. 6(1), 8(2)).</li>
<li>The tax authority can appoint banks to recover assessed tax (NTAA, s. 60(1)).</li>
<li>The Nigeria Revenue Service (NRS) now administers all federally collectable revenues, including import duties, under the Nigeria Revenue Service (Establishment) Act 2025.</li>
</ul>
<h2>Takeaways</h2>
<p>The new law is a watershed for tax administration. It adopts different — and sometimes conflicting — tax principles in order to shore up revenue, even where equity of treatment is questionable. Subjecting a non-resident company to tax on services provided and consumed in Nigeria without any contact with the country stretches traditional nexus thinking. Expect some provisions to be challenged and amended over time; how implementation affects returns on foreign investment will be closely watched.</p>"""

C2 = """<p>Nigeria's fiscal pressures are pushing tax authorities to broaden a narrow revenue base, and freelancers, influencers and online vendors are now the government's new mobilisation frontier. With the fiscal deficit projected at N23.85 trillion in the 2026 budget and the Nigeria Revenue Service (NRS) targeting N40.71 trillion in 2026 collections, authorities are under pressure to raise revenue without significant rate increases — and to bring self-employed earners into the formal net.</p>
<blockquote>"The digital economy has grown rapidly while remaining largely untaxed; this reform closes that gap and captures a fast-expanding revenue base without raising rates on traditional sectors." — Onyinye Afolabi, principal consultant, Techpoint Finance</blockquote>
<p>Nigeria is one of Africa's most active freelance markets, driven by high youth unemployment and widespread mobile internet penetration. World Population Review ranks Nigeria seventh globally by freelance earnings at roughly $0.2 billion a year (against ~$1.2 billion in the US and ~$1.0 billion in India). An analysis of the same dataset estimates Nigeria accounts for more than 30% of Africa's online freelance revenue while housing less than one-fifth of the continent's population.</p>
<h2>What changes under the new regime</h2>
<p>Under the Nigeria Tax Act and the Nigeria Tax Administration Act — signed into law in June 2025 and effective January 2026 — digital creators and online sellers fall squarely within existing tax categories rather than a new, special tax:</p>
<ul>
<li><strong>Corporate creators:</strong> creators operating through limited liability companies are subject to Companies Income Tax.</li>
<li><strong>Individual creators:</strong> individuals are liable under Personal Income Tax administered by their state of residence.</li>
<li><strong>TIN registration:</strong> every taxable person must register and obtain a Tax Identification Number.</li>
<li><strong>VAT:</strong> creators supplying taxable goods and services must register for VAT, charge it where applicable and file monthly returns.</li>
<li><strong>Stamp duties</strong> may also apply to certain electronic instruments.</li>
</ul>
<p>The law defines a small company as one with turnover not exceeding N50 million (though interpretation varies across related statutes). Small companies may be exempt from companies' income tax, creating potential incentives for digital earners to formalise under corporate structures. Once turnover exceeds the threshold, profits become taxable at 30%.</p>
<h2>Enforcement realities</h2>
<p>Experts caution that enforcement capacity remains limited relative to the scale of Nigeria's online economy. One senior tax associate told BusinessDay the authorities "currently do not have the infrastructure to track and enforce compliance across millions of digital earners" and are likely to prioritise larger taxpayers. Non-compliance still carries meaningful risk, however: failure to file or remit can attract a 10% penalty on outstanding liabilities plus compound interest linked to the Central Bank's monetary policy rate.</p>
<h2>What this means for the economy</h2>
<p>The government stands to capture revenue from a rapidly expanding segment of the workforce, particularly as formal employment growth stays weak. Even modest compliance gains among digital earners could generate billions of naira in additional revenue, and states that rely heavily on PAYE from salaried workers could stabilise their internally generated revenue by taxing self-employed digital professionals.</p>
<p>The risks are equally real: aggressive enforcement without simplified filing systems may discourage entrepreneurship among young Nigerians who turned to freelancing amid high unemployment, and there is a danger of compliance fatigue if federal and state authorities impose overlapping demands on small-scale earners.</p>"""

C3 = """<p>West Africa's tax landscape is entering a decisive transformation phase. Nigeria's consolidated Nigeria Tax Act (NTA) and Ghana's incremental reforms will shape business outcomes in 2026 and beyond. The shift from legislation to implementation introduces short-term complexity alongside long-term structural opportunity. IMF research shows more than 60% of businesses globally experience operational disruption for at least a year after major tax reforms — disruption is a predictable phase of reform, not an indicator of policy failure. International assessments suggest 12 to 24 months is a realistic adjustment horizon.</p>
<p>Nigeria's reforms are consequential given a historically low tax-to-GDP ratio of roughly 10.8%. The NTA introduces minimum effective taxes, expanded residency and nexus rules, revised corporate and personal income tax structures, enhanced digital reporting obligations and recalibrated incentives — a clear direction toward broader coverage, reduced leakage and greater fiscal sustainability.</p>
<p>Ghana presents a more predictable, incremental environment — phased policy updates, targeted sector incentives and sustained investment in tax digitalisation — and offers a practical reference point for businesses navigating Nigeria's transition.</p>
<h2>Nigeria: a comprehensive legislative overhaul</h2>
<p>Passed by the National Assembly in 2025 and effective 1 January 2026, the NTA consolidates CITA, PITA, the VAT Act, Capital Gains Tax Act, Stamp Duties Act and Petroleum Profits Tax Act into a single modern regime. Discrepancies between the versions passed by the Assembly and those published in the gazette triggered re-gazetting and the release of Certified True Copies; officials maintain the reforms remain in force. The episode distinguishes procedural controversy from policy reversal — core objectives (broadening the base, strengthening administration, improving compliance) remain intact.</p>
<p><strong>Corporate changes.</strong> Companies with annual turnover up to NGN100m and fixed assets below NGN250m are fully exempt from CIT, CGT, VAT and the Development Levy. CGT for companies is aligned with the standard 30% corporate rate; indirect (offshore share) transfers linked to Nigerian assets are now taxable; and a 4% Development Levy replaces several sector-specific levies. A 15% Minimum Effective Tax (MET) applies to companies exceeding NGN50b turnover or multinational groups with global revenue over £750m, aligning with BEPS 2.0. The legacy Pioneer Status incentive is replaced by an Economic Development Tax Incentive (EDTI) — a 5% annual tax credit on qualifying capital expenditure for up to five years, with carryforward.</p>
<p><strong>Personal changes.</strong> Individuals earning NGN800,000 or less a year are below the exemption threshold; progressive rates rise to a maximum of 25%; taxable income expands to digital assets, prizes and honoraria; and residency rules now weigh physical presence, permanent home and economic/family ties.</p>
<p><strong>VAT and administration.</strong> VAT remains 7.5% but with mandatory e-invoicing, fiscalisation and real-time digital reporting; input VAT recovery applies broadly to services and capital expenditure; essential goods and non-oil exports are zero-rated; and the Nigeria Revenue Service (NRS) manages federal tax administration.</p>
<p><strong>Nonresidents.</strong> Nonresident companies are taxed on significant economic presence, linked activity or a permanent establishment; taxable turnkey projects are expanded; force-of-attraction rules aggregate Nigeria-related profits; minimum tax generally applies at 4% of Nigerian-source income (or withholding tax); and CFC rules tax undistributed profits of foreign subsidiaries controlled by Nigerian companies. Free-zone exemptions remain, but Nigerian territorial revenue becomes fully taxable from 2028, with minimum tax applying to qualifying export-only free-zone entities outside large MNE groups.</p>
<h2>Ghana: incremental modernisation</h2>
<ul>
<li><strong>CIT</strong> at 25%, with reduced rates and incentives for manufacturing and agriculture.</li>
<li><strong>Minimum tax</strong> on a chargeable income of 5% of turnover for qualifying companies (including those declaring losses for five years).</li>
<li><strong>PIT</strong> progressive up to 35%, with 183-day presence or significant economic/family ties determining residency.</li>
<li><strong>VAT</strong> at 15%, plus NHIL and GETFund levies at 2.5% each; the GRA mandates electronic filing and real-time VAT reporting.</li>
<li><strong>WHT</strong> applied widely on dividends, interest and services.</li>
<li><strong>Administration</strong> centred on e-tax platforms, electronic invoicing, automated risk-based audits and structured dispute resolution.</li>
</ul>
<h2>Nigeria vs Ghana: key themes</h2>
<ul>
<li><strong>Legislative approach:</strong> Nigeria consolidates into one Tax Act; Ghana modernises separate statutes incrementally.</li>
<li><strong>Corporate tax:</strong> Nigeria 30% CIT + 15% MET + 4% Development Levy; Ghana 25% CIT + sector incentives.</li>
<li><strong>Digital compliance:</strong> both mandate e-invoicing and real-time reporting; Nigeria's change is more structural.</li>
<li><strong>Investment incentives:</strong> Nigeria shifts from tax holidays to the investment-linked EDTI; Ghana keeps predictable sector exemptions.</li>
<li><strong>Nonresident rules:</strong> Nigeria is more aggressive (CFC, force of attraction, 4% minimum tax); Ghana relies on standard WHT and PE concepts.</li>
</ul>
<h2>Practical implications</h2>
<p>Global reform experience points to five disciplines: rely on authoritative legislative texts and official guidance (governance); run early internal assessments covering finance, tax, legal and operations; review corporate structures and supply chains for alignment; invest in digital filing, reporting and data reconciliation readiness; and stay engaged with authorities and industry groups as interpretation matures. For Nigeria, the primary risk is delayed engagement — clarity develops through implementation, so early adaptation is a competitive necessity.</p>
<p>The underlying trajectory — toward structured, digitally enabled, transparent tax systems — is clear. Reform uncertainty is a phase, not an endpoint.</p>"""

C4 = """<p>Nigeria's 2026 tax landscape is defined by a reform-driven fiscal strategy and landmark developments in the courts and the tax authority. This briefing summarises PwC's significant corporate developments for Nigerian companies and their advisers.</p>
<h2>2026 budget and fiscal strategy</h2>
<p>The 2026 federal budget of N58.18 trillion marks a shift from spending-led stimulus to reform-driven growth. It is framed against 2025 lessons: non-oil revenues outperformed expectations, but capital expenditure was under-implemented and debt servicing absorbed a large share of revenue. The budget rests on conservative oil-price assumptions, moderate production targets and an ambitious growth outlook, coordinated fiscal and monetary policy, and a Medium-Term Expenditure Framework prioritising revenue mobilisation, expenditure efficiency and debt sustainability.</p>
<p>Infrastructure, power, defence, agriculture, digital economy, health, education, solid minerals and creative industries are positioned for increased private-sector participation through PPPs, concessions and blended finance. Expanded input VAT claims, consolidated levies and revised income and capital gains tax thresholds are expected to lower the cost of doing business while reshaping revenue dynamics.</p>
<h2>Court ruling: CbCR Regulations declared invalid</h2>
<p>The Federal High Court (FHC) upheld the Tax Appeal Tribunal's decision in <em>Check Point Software Technologies B.V. Nigeria Limited v FIRS</em>, holding that the Income Tax (Country-by-Country Reporting) Regulations 2018 were not validly issued and are null and void. The FIRS had no Board in place when the Regulations were made. The Court also held that the country-by-country Multilateral Competent Authority Agreement is a treaty within Section 12 of the Constitution and must be enacted by the National Assembly to have force in Nigeria, and that the penalties in the CbCR Regulations (up to NGN10 million) exceeded the FIRS's statutory powers under FIRSEA (NGN10,000 - NGN25,000).</p>
<h2>FIRS circular on the WHT Regulations 2024</h2>
<p>On 24 February 2025, the FIRS issued a Circular guiding implementation of the WHT (Rates) Regulations 2024, effective for transactions from 1 January 2025:</p>
<ul>
<li><strong>Scope:</strong> applies to companies, partnerships, statutory and non-statutory bodies, unincorporated persons and non-resident persons involved in transactions requiring deduction at source.</li>
<li><strong>Small-company exemption:</strong> small companies are exempt from deducting WHT where the transaction value is NGN2 million or less and the supplier holds a valid TIN, with worked illustrations provided.</li>
<li><strong>Fake receipts:</strong> the Circular reiterates penalties for failure to deduct or remit, and sanctions for submitting fake or counterfeit receipts.</li>
<li><strong>Exemptions:</strong> interest or fees on bank direct debits, and broker commissions withheld per industry norms, are clarified as outside the requirements.</li>
</ul>
<h2>Proposed windfall tax on banks</h2>
<p>The government proposes a 70% 'windfall tax' on realised profits Nigerian banks made from exchange transactions in FY2023-FY2025. The proposal is contentious: it applies retrospectively to profits from FY2023 that banks had already filed and paid by June 2024, raising practical and legal concerns.</p>
<h2>Deposit requirements for appeals struck down</h2>
<p>The FHC struck down provisions requiring taxpayers to pay security deposits before filing appeals at the Tax Appeal Tribunal and courts, holding they infringe the constitutional right to fair hearing. Taxpayers can now appeal without paying deposits, though questions remain about deposit requirements that still exist in the FIRS Establishment Act and the constitutionality of Practice Directions.</p>
<h2>VAT on imported digital-platform goods postponed</h2>
<p>The FIRS postponed its planned automated collection of VAT on imported goods bought through digital platforms. Following the 2020 Finance Act's requirement that non-residents supplying taxable goods/services to Nigerian customers register and account for VAT, the Simplified Compliance Regime took effect 1 January 2022 for services and intangibles and was due 1 January 2024 for goods. The FIRS pushed that goods start back to allow more time to develop a seamless process and cooperate with the Nigerian Customs Service; the services/intangibles framework remains in force.</p>"""

C5 = """<p>Businesses across Nigeria face significant compliance adjustments ahead of the 2026 tax filing cycle. The changes affect filing timelines, documentation requirements, digital reporting standards, audit exposure and penalty enforcement, signalling a tighter compliance environment and increased regulatory oversight.</p>
<h2>1. Stricter filing timelines and enforcement</h2>
<p>Regulators have emphasised zero tolerance for late submissions, particularly for corporate income tax (CIT) and VAT returns. Companies must still file annual income tax returns within six months of financial year-end, but authorities are strengthening enforcement with automated penalty assessments and interest accruals. Per the FIRS, late-filing penalties are N25,000 for the first month of default and N5,000 for each subsequent month; in 2026 businesses risk faster penalty imposition through digital monitoring systems.</p>
<h2>2. Expanded digital reporting requirements</h2>
<p>Authorities are expanding mandatory electronic filing, e-invoicing frameworks and real-time transaction reporting, modernising administration through automation and data integration. Expect stricter validation protocols and data-matching across agencies. Implications include greater scrutiny of transaction records, alignment between VAT filings and audited financial statements, and improved internal accounting controls. Companies relying on manual reconciliation may face bottlenecks — CFOs should prioritise ERP integration and tax-technology upgrades.</p>
<h2>3. Increased audit and data cross-verification</h2>
<p>Tax authorities are intensifying cross-checking between corporate filings, bank records and third-party disclosures, consistent with OECD-promoted global compliance trends. Automated risk-assessment systems can now flag inconsistencies in declared revenue, VAT remittances and withholding tax records. Businesses operating across multiple states or sectors face higher audit probability where discrepancies arise — a shift from reactive audits to proactive, risk-based monitoring.</p>
<h2>4. Revised documentation and disclosure standards</h2>
<p>Companies must maintain more detailed supporting records for related-party transactions, capital allowances and asset declarations, transfer pricing documentation and withholding tax deductions. Transfer pricing compliance is especially critical for multinationals: Nigeria's TP regulations, administered by the FIRS, require contemporaneous documentation justifying intercompany pricing. An inability to produce adequate records at audit can result in reassessments and additional liabilities.</p>
<h2>5. Stronger penalty framework and interest accrual</h2>
<p>Automated systems reduce delays in penalty issuance, delivering immediate consequences for infractions. Interest on unpaid tax liabilities accrues at prevailing commercial rates, increasing financial exposure for companies that defer compliance. For listed companies, the risks extend beyond penalties to reputational damage and investor confidence.</p>
<h2>Strategic implications for business leaders</h2>
<ul>
<li>Conduct internal compliance audits before the 2026 filing cycle.</li>
<li>Invest in digital tax-reporting infrastructure.</li>
<li>Review and update transfer pricing documentation.</li>
<li>Train finance teams on updated regulatory expectations.</li>
</ul>
<p>The 2026 filing cycle is a decisive shift toward stricter enforcement, digital oversight and enhanced documentation. Treat tax compliance as a strategic governance priority, not an administrative obligation. Businesses that adapt early mitigate risk and position themselves competitively in an increasingly regulated environment.</p>"""

C6 = """<p>Revenue is the pulse of every business — the ability to generate, record and protect it determines whether an organisation can meet its obligations to shareholders, employees and partners. The revenue cycle, from product development to invoicing and collection, is central to value creation. As business environments grow more complex, that cycle becomes vulnerable to revenue leakage — through missed billing, contract mismanagement or errors in revenue recognition — which silently erodes profitability and, in severe cases, threatens future viability.</p>
<p>Waiting for month-end reconciliations or quarterly audits to find discrepancies is no longer viable. Organisations must adopt a proactive, real-time approach to leakage, or risk losing significant value over time.</p>
<h2>The evolution of revenue assurance</h2>
<p>Traditionally, revenue assurance was reactive — periodic audits and manual, sample-based reviews. By the time discrepancies were identified, the financial impact had already hit the bottom line, and sample testing overlooked hidden issues in high-volume businesses. In sectors with diverse revenue streams — telecommunications, retail, media — multiple pricing structures, discount arrangements and partner agreements create complex revenue paths demanding data accuracy and process integrity.</p>
<p>Modern data analytics and artificial intelligence have transformed the discipline. AI monitors transactions at speed and volume, flagging unusual patterns and pinpointing anomalies at source and in real time — proactive insights that let organisations address leakage immediately rather than after the fact.</p>
<h2>Leakage is a cross-industry threat</h2>
<p>Leakage manifests differently by sector. In financial services it can arise from inaccuracies in bank and card fee calculations or errors in partner commissions; payment partners are critical, but any discrepancy may mean lost revenue or unearned fees. Stringent regulatory requirements add a compliance layer that makes transaction-by-transaction tracking essential.</p>
<h2>Key questions for an effective framework</h2>
<ul>
<li>Is your organisation experiencing revenue leakage?</li>
<li>Where are the potential leakage points in your revenue cycle?</li>
<li>Can you quantify potential revenue losses?</li>
<li>How accurate are your reported revenue figures?</li>
<li>Do you have advanced systems and controls in place to prevent and monitor leakage?</li>
</ul>
<h2>Data analytics and AI: the future of revenue assurance</h2>
<p>Machine-learning models detect anomalies, predict risk areas and surface actionable insights from historical data — identifying subtle indicators such as unusual billing-cycle patterns or inconsistencies in partner commission structures. Coupled with real-time data, these insights enable fast response and minimal financial impact. Sentiment is positive: in PwC's 27th Annual CEO Survey, 63% of Middle East CEOs expected GenAI to increase their organisations' revenue and 62% expected it to increase profitability.</p>
<h2>Building a revenue assurance culture</h2>
<p>Technology alone is not enough. A resilient framework requires a cultural shift that treats revenue integrity as everybody's responsibility — collaboration across finance, operations, sales and IT — plus training on revenue management processes, clear policies and performance metrics aligned with revenue protection goals.</p>
<h2>Looking ahead</h2>
<p>Revenue assurance is now a proactive, strategic pillar of organisational resilience: systematically analyse the revenue cycle to identify leakage risks; build a culture of accountability; implement comprehensive policies and clear metrics; invest in AI and data-analytics tools for real-time monitoring; and keep a data-driven focus so discrepancies are addressed swiftly.</p>"""

C7 = """<p>Telecom executives face an uncomfortable reality: traditional revenue streams are eroding while operational complexity multiplies. As ARPU declines and competition intensifies, the question shifts from what revenue assurance is to how quickly operators can turn billing infrastructure into a strategic protection engine. Gartner estimates operators lose 2-5% of annual revenue through billing discrepancies, fraud and reconciliation failures.</p>
<p>Modern operators need more than periodic audits — they need AI-driven systems that detect anomalies in real time, machine-learning models that predict billing irregularities before cash flow suffers, and comprehensive reconciliation frameworks that ensure every transaction is monetised.</p>
<h2>Why revenue assurance matters now</h2>
<p>Revenue leakage costs the telecom industry billions each year. PwC research shows many operators lose 3-8% of total revenue to billing errors, fraud and reconciliation gaps — direct EBITDA erosion at a time when 5G and evolving technology investments strain margins. Regulators have intensified scrutiny of billing practices across expanding service portfolios, from legacy voice to IoT. A single billing mistake can trigger churn in markets where subscribers have abundant alternatives.</p>
<p>Documented benefits of a comprehensive telecom revenue-assurance system include:</p>
<ul>
<li>EBITDA improvement of 2-5% through reduced revenue leakage.</li>
<li>Customer churn reduction of 15-30% via accurate billing.</li>
<li>Regulatory-compliance savings of USD 0.5-2 million annually.</li>
<li>Shorter service-launch cycles with built-in billing validation.</li>
</ul>
<h2>Core components of a revenue-assurance framework</h2>
<ol>
<li><strong>Data acquisition and collection</strong> — captures event and call detail records (CDRs) from network elements, billing platforms and external interfaces.</li>
<li><strong>Rating verification</strong> — checks that every record is priced correctly against tariff tables, exposing discrepancies before they reach customers.</li>
<li><strong>Usage reconciliation</strong> — matches records across network domains and systems, flagging missing or duplicate transactions.</li>
<li><strong>Reporting and analytics</strong> — converts validated data into automated alerts and trend analysis for assurance teams.</li>
</ol>
<h2>Typical leakage scenarios</h2>
<ul>
<li><strong>SIM-box fraud (international bypass):</strong> 3-8% of revenue, high detection complexity.</li>
<li><strong>IRSF schemes (premium-rate exploitation):</strong> 2-5%, very high complexity.</li>
<li><strong>Billing engine errors (configuration drift):</strong> 1-3%, medium.</li>
<li><strong>Interconnect disputes (CDR reconciliation gaps):</strong> 0.5-2%, low.</li>
<li><strong>PBX intrusions (endpoint compromise):</strong> 1-4%, medium.</li>
</ul>
<h2>Step-by-step revenue-assurance process</h2>
<ol>
<li><strong>Data ingestion</strong> — collect comprehensive CDRs, billing and network usage data across voice, data and value-added services.</li>
<li><strong>Validation and cleansing</strong> — verify integrity, identify gaps and standardise formats.</li>
<li><strong>Rating reconciliation</strong> — compare billed charges against expected tariffs in near real time.</li>
<li><strong>Exception management</strong> — flag anomalies through intelligent threshold monitoring.</li>
<li><strong>Fraud analytics</strong> — apply algorithms that detect schemes traditional controls miss.</li>
<li><strong>KPI reporting</strong> — dashboards tracking billing accuracy, revenue recovery and operational efficiency.</li>
</ol>
<p>Operators adopting automated workflows typically uncover discrepancies worth 2-5% of total revenue — losses manual methods rarely capture.</p>
<h2>Advanced technologies reshaping assurance</h2>
<p>AI and machine learning with big-data frameworks enable real-time analysis of massive datasets, examining billing data, CDRs and signalling simultaneously to predict and prevent losses. Blockchain-based threat intelligence supplies near real-time insight on emerging fraud vectors, and patented Protocol Signature technology analyses signalling patterns to detect fraud before a call even happens. Forward-looking platforms embrace fintech data, IoT traffic and 5G network-slicing metrics.</p>
<h2>Definitions</h2>
<p><strong>Revenue assurance</strong> is a discipline that guarantees accurate billing and complete revenue capture across telecom operations, continuously monitoring BSS and OSS processes and applying systematic controls to prevent leakage. It differs from revenue management (optimising pricing and product strategies) and fraud management (combating malicious activity) — business assurance unites all three for holistic financial protection.</p>"""

C8 = """<p>Revenue assurance is the use of data quality and process improvement methods that improve profits, revenues and cash flows without influencing demand. The definition was developed by a TM Forum working group and documented in its Revenue Assurance Technical Overview.</p>
<h2>Origins and expansion</h2>
<p>Revenue assurance emerged in the telecommunications industry, where high transaction volumes, complex rating and billing structures, and multiple network and IT systems create constant risk of revenue leakage. Over time the discipline expanded well beyond telecom to any industry where revenue flows through many systems and touchpoints — utilities, financial services, media, retail and subscription platforms.</p>
<h2>Core techniques</h2>
<ul>
<li><strong>Automated reconciliation</strong> — matching records between systems (e.g., network usage vs. billing) to identify missing, duplicate or mis-rated transactions.</li>
<li><strong>Data quality management</strong> — cleansing, standardising and deduplicating data so downstream processes run on trustworthy inputs.</li>
<li><strong>Continuous monitoring and analytics</strong> — detecting anomalies, leakage and process breakdowns in near real time rather than at audit time.</li>
<li><strong>Process improvement</strong> — fixing the root causes of leakage so that revenue is captured correctly at source.</li>
</ul>
<h2>Why it matters for tax and financial reporting</h2>
<p>The same principles are directly applicable outside telecom. Nigerian businesses managing VAT collections, withholding tax deductions, e-invoice reconciliation and payroll under the new Nigeria Tax Act face the same underlying problem: revenue (and tax) must be accurately captured, recorded and remitted across multiple systems. A revenue-assurance mindset ensures that money due — whether to the business or to the tax authority — is never lost to process failure. With mandatory e-invoicing and real-time digital reporting on the horizon, data quality and reconciliation have become compliance requirements as much as commercial priorities.</p>
<p>In summary, revenue assurance protects a company's numbers where they are earned, using data quality and process controls to maximise profit, revenue and cash flow without needing to change demand or pricing.</p>"""

C9 = """<p>Nigeria's foreign investor participation surged 107.74% month-on-month in March 2026, reaching N288.82 billion on the Nigerian Exchange — a robust indicator of international confidence in Africa's largest economy, with a N542.3 trillion GDP and a population exceeding 200 million consumers.</p>
<ul>
<li><strong>Diversification:</strong> Nigeria offers relatively non-correlated returns.</li>
<li><strong>Yield advantage:</strong> the NGX delivered a 45.9% equity return in 2025, far ahead of the S&amp;P 500's 12.4%.</li>
<li><strong>First-mover benefits</strong> in renewable energy, digital banking, health tech and other emerging sectors.</li>
</ul>
<h2>What is driving the surge</h2>
<p>Three reform milestones underpin renewed confidence:</p>
<ul>
<li><strong>May 2023 — fuel subsidy removal</strong>, freeing up an estimated N4 trillion annually for infrastructure and social services.</li>
<li><strong>June 2023 — FX liberalisation</strong>, unifying the NAFEX window and making repatriation transparent and predictable.</li>
<li><strong>Q1 2026 results</strong> — a 78% year-on-year rise in foreign inflows to the NGX, totalling N393.68 billion.</li>
</ul>
<p>The Dangote Refinery's more-than-US$5 billion investment post-reforms is a real-world signal of the impact of guaranteed FX repatriation. Demographically, roughly 63% of Nigerians are under 25, 46% of adults are now banked, and the informal sector is estimated at N25 trillion — a vast formalisation opportunity. High-growth sectors include fintech (32% CAGR), agriculture (18%) and renewable energy (29%), while the NGX's dedicated Tech Board has drawn over N120 billion in foreign venture-capital funding since 2025.</p>
<h2>Four ways to participate</h2>
<p><strong>1. Foreign Direct Investment (FDI).</strong> Best for manufacturers, infrastructure developers and service providers seeking control. Key steps: register with the CAC (about N50,000, ~2 weeks); obtain the NIPC certificate (about N100,000); open a foreign-currency domiciliary account; and complete an Environmental Impact Assessment where applicable (N2-5 million).</p>
<p><strong>2. Foreign Portfolio Investment (FPI).</strong> Best for funds and institutions seeking liquid exposure. Register with the SEC (about N250,000), open a CSCS account (about N25,000), and fund investments through the Investors' &amp; Exporters' window using CBN Form A. 2026 year-to-date: FGN bonds yielding 15.2% pulled N189 billion; NGX stocks (45.9%) N288.82 billion; commercial paper (18.5%) N65 billion.</p>
<p><strong>3. Private Equity / Venture Capital.</strong> 312 Nigerian startups raised US$1.2 billion in 2025 across fintech, healthtech, agritech and e-commerce. The Paystack exit (acquired by Stripe for over US$200 million) shows the exit potential for early-stage investors.</p>
<p><strong>4. Public-Private Partnerships.</strong> The Lagos-Calabar Coastal Highway (~US$11 billion), Abuja Light Rail Phase 2 (~N800 billion) and power-sector reforms open long-term infrastructure opportunities, often with CBN facilitation or guarantees.</p>
<h2>Regulatory framework to know</h2>
<ul>
<li><strong>CBN:</strong> FX approvals and the Certificate of Capital Importation (CCI); report inward capital within 30 days and obtain a CCI — without it, repatriation is extremely difficult.</li>
<li><strong>FIRS:</strong> CIT (30% for large companies), VAT (7.5%) and WHT; annual CIT filing, monthly VAT and WHT filing.</li>
<li><strong>NIPC:</strong> business permits and investment incentives (registration ~N100,000, 14 days).</li>
<li><strong>CAC:</strong> company registration (~N50,000, ~2 weeks).</li>
<li><strong>SEC:</strong> capital market regulation and foreign-investor registration.</li>
<li><strong>NAFDAC and SON:</strong> product, food and standards regulation.</li>
</ul>
<p>Watch 5% withholding tax on dividends (deducted at source), local-content requirements in oil &amp; gas and ICT, and the expatriate quota from the Ministry of Interior.</p>
<h2>Incentives worth using</h2>
<ul>
<li>5-year tax holiday for pioneer industries (CIT-exempt).</li>
<li>100% capital allowance on qualifying infrastructure projects.</li>
<li>Investment tax credit of up to 20% on qualifying R&amp;D expenditure.</li>
<li>Rural investment allowance of 10-100% of qualifying capital expenditure.</li>
<li>Free Trade Zones — Lekki, Calabar, Kano and Onne offer 0% VAT/corporate tax, duty-free imports, 100% foreign ownership and unrestricted repatriation.</li>
</ul>
<h2>Challenges and mitigation</h2>
<p>FX liquidity and naira volatility (hedge via CBN forwards — commonly 25% of anticipated FX needs); sudden regulatory change (retain experienced local counsel and monitor official guidance); infrastructure deficits (budget for alternative power and use FTZs); security concerns in some regions (conduct site due diligence); bureaucracy (use digital government services); and skilled-labour gaps (invest in local talent).</p>
<h2>2026 outlook: where the smart money is going</h2>
<p>Five fast-growing areas stand out: electric vehicles (e.g., Nord Motors raised N12 billion), healthtech (Helium Health raised US$30 million Series B), climate tech (a carbon-credit market estimated at N150 billion), digital education, and logistics and supply-chain technology. Hybrid plays — AgriTech and PropTech — are emerging frontiers with high disruption potential.</p>"""

C10 = """<p>Using 2026 macroeconomic data — including the Central Bank of Nigeria's Macroeconomic Outlook and the World Bank's Global Economic Projection — this analysis identifies the most sustainable, high-yielding investment opportunities in Nigeria, a market now defined by what MOHAC Africa calls 'Consolidated Stability': domestic growth projected at 4.49% (the fastest pace in over a decade) with inflation moderating toward 12.94%, making real yields among the most competitive in Sub-Saharan Africa.</p>
<h2>1. Banking and capital markets</h2>
<p>For capital preservation, 2026 fixed income is a powerhouse after 2025's monetary tightening. Money market funds offer 22-26% yields; 364-day treasury bills carry stop rates between 18% and 22% and are tax-free. On equities, the NGX anticipates a landmark year with the expected listing of the Dangote Refinery and NNPC; blue-chip banking stocks dominate income lists — Zenith Bank at a 10.5% dividend yield and GTCO at 8.6%.</p>
<h2>2. Agribusiness: the N2.3 trillion opportunity</h2>
<p>Agriculture has shifted from subsistence to industrial-scale production. The 2026 budget earmarks N2.3 trillion for agriculture and technology, with N1.45 trillion to the Ministry of Agriculture and N126 billion for Special Agro-Industrial Processing Zones (SAPZ). The real profit lies in value-added processing — soybeans, cassava and fruit juices — where local processing opens the African Continental Free Trade Area (AfCFTA) market of 1.3 billion people while qualifying for 5-year pioneer tax holidays.</p>
<h2>3. Real estate: infrastructure-driven growth</h2>
<p>The Epe-Ibeju-Lekki corridor has entered a golden growth phase: land appreciating 20-25% annually in 2026, driven by the Lekki Deep Sea Port and the Coastal Road Project. Prime short-let luxury apartments in Lekki Phase 1 and Victoria Island deliver 25-35% annual returns. REITs and off-plan projects in smart estates offer hands-off diaspora exposure, with 'green building' — solar and water-recycling estates — now driving tenant demand as energy costs rise.</p>
<h2>4. Fintech and iDICE: the digital youth engine</h2>
<p>Nigeria's tech movement is backed by the US$617 million iDICE (Investment in Digital and Creative Enterprises) program, which in 2026 adds a creative-sector fund and a fund-of-funds. Fintech remains the sector leader, with HealthTech and EdTech the breakout stars. The Nigeria Youth Investment Fund received a N110 billion boost. Seed-stage investors can take equity in the next African unicorn through SEC-licensed digital wealth apps starting from as little as N50,000.</p>
<h2>5. Off-Grid Solar: the clean-energy shift</h2>
<p>With the 2021 Petroleum Industry Act matured, attention turns to the gas-to-power transition and off-grid solar. The 2026 budget allocates N257.8 billion to the Energy Commission of Nigeria for renewable research and infrastructure. Mini-grids and local assembly of solar components address a massive SME and rural power deficit, offer stable long-term cash flows, and are often eligible for international green bonds — a dual layer of security for institutional investors.</p>
<h2>Protecting your capital</h2>
<ul>
<li>Verify that platforms and brokers are licensed by the SEC.</li>
<li>Register with NIPC for legal protection and capital repatriation facilitation.</li>
<li>Consult the 2025 Finance Act for new tax incentives for small businesses and export ventures.</li>
</ul>
<p>Entry is accessible: from N5,000 via digital wealth apps for mutual funds, or N1.5-5 million for land banking in developing areas. The 2026 landscape offers a rare window where high yields meet structural stability — whether for tech startups, agro-processing businesses or diaspora investors.</p>"""

C11 = """<p>The United Kingdom has committed to working side-by-side with Nigeria to strengthen implementation, reduce bottlenecks and create a more predictable business environment that unlocks investment opportunities, creates jobs and supports long-term growth.</p>
<p>Alice Clarke, the UK's Head of Macroeconomic Stability at the British High Commission in Nigeria, gave the assurance while speaking at 'The Reform and Diplomatic Roundtable 2026', organised by PEBEC in collaboration with the UK International Development and the Nigeria Economic Stability and Transformation (NEST) programme — a UK-Nigeria partnership focused on macroeconomic reforms and the business environment.</p>
<blockquote>"Businesses don't experience reform in theory. They feel it in permits, power connections, and how institutions respond when things go wrong. Today's assessment gives us a clear picture of where progress is happening and where consistency must improve." — Alice Clarke, British High Commission, Nigeria</blockquote>
<h2>From reform to real capital deployment</h2>
<p>Presenting Nigeria's Investment Outlook 2026, a NEST expert, Mr Afolabi Imoukhuede, described the outlook as "cautiously positive", citing the Central Bank of Nigeria's January position. Nigeria is re-entering the investment radar as macroeconomic reforms improve credibility, with FX, fiscal and policy adjustments stabilising the outlook. The IMF recently projected 4.4% growth for Nigeria in 2026.</p>
<p>However, investment capital remains selective, risk-aware and sector-driven. Inflows are still dominated by short-term portfolio capital, and the economy needs foreign direct investment in the real sector. The prescription: convert macroeconomic stabilisation into bankable real-sector assets; move from passive inflow to targeted deployment; and target FDIs into sectors that earn or save FX and boost job creation.</p>
<h2>Priority sectors for FDI</h2>
<p>The recommended real sectors include agriculture and agro-processing, manufacturing and industrial clusters, logistics and trade infrastructure, power, renewable energy and green jobs, mining, the digital and creative economy, and housing and construction materials — with a focus on FX-earning and job-creating activity.</p>
<h2>States as FDI 'Landing Zones'</h2>
<p>Imoukhuede urged that the top ten states in the PEBEC Ease of Doing Business ranking should become pre-packaged investment destinations designated as FDI 'Landing Zones'. These states show faster approvals, more predictable regulation, better land and permit systems, an improved justice system, stronger investor engagement, digital governance improvements and investor aftercare — translating into lower execution risk and higher investment.</p>
<h2>National development planning as a catalyst</h2>
<p>In a keynote, the Minister of Budget and Economic Planning, Senator Abubakar Atiku Bagudu, noted that Nigeria's federal structure empowers states and local governments — including the ability to contract and administer their own courts — making subnational action critical to attracting investment. Citing Chapter 2 of the Constitution and Section 13 (which obliges all tiers of government to pursue the fundamental objectives), he argued Nigeria's ambition of a US$1 trillion economy by 2030 will depend largely on states and the private sector. Competition among states, supported by reforms and programmes backed by institutions such as the World Bank, has already encouraged improved economic performance across the country.</p>"""


def build_articles():
    now = datetime.now(timezone.utc).isoformat()

    def article(title, slug, category, excerpt, content, tags, source_name, source_title, source_author, source_date, source_url, read_label, featured_image=""):
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "slug": slug,
            "category": category,
            "excerpt": excerpt,
            "content": content,
            "author": "",
            "tags": tags,
            "featured_image": featured_image,
            "published": True,
            "source_name": source_name,
            "source_title": source_title,
            "source_author": source_author,
            "source_date": source_date,
            "source_url": source_url,
            "read_label": read_label,
            "views": 0,
            "created_at": now,
        }

    return [
        article(
            "Nigeria Reforms Tax Laws for 2026, Rewrites Rules for MNEs",
            "nigeria-reforms-tax-laws-2026-mnes",
            "Tax",
            "Nigeria has enacted sweeping changes to its tax framework for 2026, rewriting the rules for multinational enterprises and reshaping how cross-border income is taxed.",
            C1,
            ["tax reform", "MNE", "Nigeria Tax Act 2026", "withholding tax", "transfer pricing"],
            "Bloomberg Tax",
            "Nigeria Reforms Tax Laws for 2026, Rewrites Rules for MNEs",
            "Tayo Ogungbenro and Ngozi Asim-Ita",
            "22 December 2025",
            "https://news.bloombergtax.com/tax-management-international/nigeria-reforms-tax-laws-for-2026-rewrites-rules-for-mnes",
            "Read on Bloomberg Tax",
            "https://bloomberg-bna-brightspot.s3.us-east-1.amazonaws.com/91/f4/4a8faf284afbbe31a14c43671517/bli-tax-management-international-journal.png",
        ),
        article(
            "How Nigeria's 2026 Tax Reform Targets the Gig Economy",
            "nigeria-2026-tax-reform-gig-economy",
            "Tax",
            "New provisions bring freelance and gig workers into the formal tax net, with simplified registration and withholding mechanisms.",
            C2,
            ["gig economy", "tax reform", "freelancers", "digital economy", "PAYE"],
            "BusinessDay",
            "How Nigeria's 2026 Tax Reform Targets the Gig Economy",
            "Ayomide Odunlami",
            "27 February 2026",
            "https://businessday.ng/news/article/how-nigerias-2026-tax-reform-targets-the-gig-economy/",
            "Read on BusinessDay",
            "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=1200&q=80&auto=format&fit=crop",
        ),
        article(
            "2026 Business Outlook on Tax Reforms in Nigeria and Ghana",
            "2026-tax-reforms-nigeria-ghana-ey",
            "Tax",
            "EY's regional outlook maps the legislative and administrative changes shaping West African tax compliance in 2026.",
            C3,
            ["West Africa", "tax outlook", "EY", "Nigeria", "Ghana", "2026"],
            "EY Tax News",
            "West Africa: From legislation to action - 2026 business outlook on tax reforms in Nigeria and Ghana",
            "Ernst & Young (EY Global Tax Insights)",
            "15 January 2026",
            "https://taxnews.ey.com/news/2026-0208-west-africa-from-legislation-to-action-2026-business-outlook-on-tax-reforms-in-nigeria-and-ghana",
            "Read on EY",
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80&auto=format&fit=crop",
        ),
        article(
            "Nigeria - Corporate Significant Developments",
            "nigeria-corporate-significant-developments-pwc",
            "Business",
            "PwC's summary of Nigeria's most significant corporate tax developments, covering the new Tax Act and its implications for companies.",
            C4,
            ["corporate tax", "Nigeria Tax Act", "PwC", "compliance", "developments"],
            "PwC Worldwide Tax Summaries",
            "Nigeria - Corporate - Significant Developments",
            "PwC",
            "last reviewed 29 May 2026",
            "https://taxsummaries.pwc.com/nigeria/corporate/significant-developments",
            "Read on PwC",
            "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80&auto=format&fit=crop",
        ),
        article(
            "What Businesses Need to Know About the 2026 Tax Filing Changes",
            "2026-tax-filing-compliance-changes",
            "Tax",
            "Five key compliance changes in Nigeria's 2026 tax filing rules that every business must prepare for.",
            C5,
            ["tax filing", "compliance", "deadlines", "e-filing", "penalties"],
            "Nigeria Housing Market",
            "2026 Tax Filing: Five Key Compliance Changes Businesses Must Prepare For",
            "Ayomide Fiyinfunoluwa",
            "21 February 2026",
            "https://www.nigeriahousingmarket.com/news/2026-tax-filing-five-key-compliance-changes-businesses-must-prepare-for",
            "Read article",
            "https://images.squarespace-cdn.com/content/v1/665f92f354532c3140db9a8a/279f5f35-2922-47e2-b4e7-42ba1b3c6d5f/Nigeria-Tax-Law.png",
        ),
        article(
            "Revenue Assurance: A Strategic Imperative",
            "revenue-assurance-strategic-imperative-pwc",
            "Revenue Assurance",
            "PwC makes the case that revenue assurance is no longer optional - it is a board-level strategic function.",
            C6,
            ["revenue assurance", "PwC", "leakage", "reconciliation", "strategy"],
            "PwC",
            "Revenue assurance: A strategic imperative in today's complex business landscape",
            "PwC Middle East",
            "24 December 2024",
            "https://www.pwc.com/m1/en/publications/revenue-assurance-strategic-imperative-in-todays-complex-business-landscape.html",
            "Read on PwC",
            "https://www.pwc.com/m1/en/publications/images-new/revenue-assurance-hero.jpg",
        ),
        article(
            "What Is Revenue Assurance in Telecom?",
            "revenue-assurance-telecom-latro",
            "Revenue Assurance",
            "LATRO explains how revenue assurance prevents revenue leakage in telecom and how the same principles apply to tax compliance.",
            C7,
            ["revenue assurance", "telecom", "LATRO", "leakage", "reconciliation"],
            "LATRO",
            "Stop revenue leakage: What is revenue assurance in telecom?",
            "LATRO",
            "11 July 2025",
            "https://latro.com/blog/stop-revenue-leakage-what-is-revenue-assurance-in-telecom/",
            "Read on LATRO",
            "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&q=80&auto=format&fit=crop",
        ),
        article(
            "Revenue Assurance Overview",
            "revenue-assurance-overview-wikipedia",
            "Revenue Assurance",
            "Wikipedia's overview of revenue assurance - the processes, tools and frameworks that protect revenue streams across industries.",
            C8,
            ["revenue assurance", "overview", "reconciliation", "monitoring"],
            "Wikipedia",
            "Revenue assurance",
            "Wikipedia (Wikimedia Foundation)",
            "last edited 12 February 2026",
            "https://en.wikipedia.org/wiki/Revenue_assurance",
            "Read on Wikipedia",
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80&auto=format&fit=crop",
        ),
        article(
            "Nigeria's Foreign Investor Surge: A Guide to Opportunities",
            "nigeria-foreign-investor-surge-kudicompass",
            "Investment",
            "A practical guide to the sectors and structures attracting the most foreign investment into Nigeria in 2026.",
            C9,
            ["foreign investment", "Nigeria", "FDI", "opportunities", "entry structures"],
            "KudiCompass",
            "Nigeria's Foreign Investor Surge: A Comprehensive Guide to Opportunities (2024-2026 Outlook)",
            "Laura Femi",
            "30 April 2026",
            "https://kudicompass.com/nigeria-foreign-investor-participation-surge-guide/",
            "Read on KudiCompass",
            "https://kudicompass.com/wp-content/uploads/2026/04/nigeria-foreign-investor-participation-surge-guide-featured-1024x559.jpg",
        ),
        article(
            "Top 5 Investment Opportunities in Nigeria: 2026 Data-Driven",
            "top-5-investment-opportunities-nigeria-2026",
            "Investment",
            "MOHAC Africa's data-driven breakdown of the five highest-potential investment sectors in Nigeria for 2026.",
            C10,
            ["investment", "Nigeria", "2026", "sectors", "data-driven", "MOHAC"],
            "MOHAC Africa",
            "Top 5 Investment Opportunities in Nigeria: 2026 Data-Driven",
            "MOHAC Africa",
            "19 January 2026",
            "https://mohacafrica.org/investment-opportunities-in-nigeria/",
            "Read on MOHAC Africa",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80&auto=format&fit=crop",
        ),
        article(
            "UK Pledges to Partner Nigeria for Predictable Business Environment",
            "uk-nigeria-predictable-business-environment-allafrica",
            "Business",
            "The UK commits to supporting Nigeria's business environment reforms, signalling stronger bilateral trade and regulatory cooperation.",
            C11,
            ["UK", "Nigeria", "bilateral", "business environment", "trade"],
            "AllAfrica / This Day",
            "UK Pledges to Partner Nigeria for More Predictable Business Environment, Investment Opportunities",
            "Ndubuisi Francis (This Day, Abuja)",
            "30 March 2026",
            "https://allafrica.com/stories/202603310026.html",
            "Read on AllAfrica",
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&q=80&auto=format&fit=crop",
        ),
    ]


def main():
    docs = build_articles()
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", ""),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", ""),
        cursorclass=DictCursor,
        connect_timeout=10,
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM resources")
            existing = cur.fetchone()["n"]

            cur.execute("DELETE FROM resources")

            for doc in docs:
                cur.execute(
                    """
                    INSERT INTO resources
                        (_id, id, title, slug, category, excerpt, content, author,
                         tags, featured_image, created_at, views, doc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid.uuid4().hex[:24],
                        doc["id"],
                        doc["title"],
                        doc["slug"],
                        doc["category"],
                        doc["excerpt"],
                        doc["content"],
                        doc["author"],
                        json.dumps(doc.get("tags", []), ensure_ascii=False),
                        doc.get("featured_image", ""),
                        doc["created_at"],
                        doc.get("views", 0),
                        json.dumps(doc, ensure_ascii=False),
                    ),
                )
            conn.commit()

            cur.execute("SELECT COUNT(*) AS n FROM resources")
            total = cur.fetchone()["n"]

        print(f"[OK] Replaced {existing} previous row(s) with {total} full-length curated resources")
    finally:
        conn.close()


if __name__ == "__main__":
    main()