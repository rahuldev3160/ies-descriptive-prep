"""RBI DEPR Phase 1 Prep — Key Data Cards + Tier 2 MCQ Quiz."""
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from styles import apply_theme, chip

st.set_page_config(page_title="RBI Prep · DEPR 2026", layout="wide", page_icon="🏦")
apply_theme()

RBI_DATE = "2026-06-14"


def days_to_rbi() -> int:
    return (datetime.strptime(RBI_DATE, "%Y-%m-%d").date() - datetime.today().date()).days


# ── Key Data sections ──────────────────────────────────────────────────────────
# Each item: (name, value, explanation, needs_verify)
KEY_SECTIONS = [
    {
        "label": "LAF Corridor & Policy Rates",
        "color": "#8AB4F8",
        "items": [
            ("Repo Rate", "5.25%", "MPC Feb 2026 kept unchanged at 5.25%. Cumulative 125 bps cuts since Feb 2025 (from 6.50%). MPC stance: Neutral.", False),
            ("SDF Rate", "5.00% (Repo − 25 bps)", "Standing Deposit Facility (Apr 2022). LAF floor. Banks park surplus with RBI collateral-free. Replaced reverse repo as operative floor.", False),
            ("MSF Rate", "5.50% (Repo + 25 bps)", "Marginal Standing Facility. LAF ceiling. Emergency window — banks use up to 3% of NDTL of SLR portfolio.", False),
            ("Bank Rate", "= MSF Rate", "Rate for long-term advances outside LAF. Used as benchmark for penalty/penal rates.", False),
            ("LAF Corridor width", "±25 bps = 50 bps total", "Symmetric: SDF (floor) ↔ Repo (policy signal) ↔ MSF (ceiling). Post-Apr 2022 structure.", False),
            ("Reverse Repo", "3.35% (de facto superseded by SDF)", "Exists in statute but SDF is the operative floor since Apr 2022. Exam trap: SDF ≠ reverse repo.", False),
        ],
    },
    {
        "label": "Reserve Ratios & PSL",
        "color": "#C084FC",
        "items": [
            ("CRR", "4% of NDTL ⚠ verify no further cuts", "% of NDTL held as cash with RBI. No interest paid. RBI cut CRR injecting ₹2.5 lakh crore in FY26. Standard level 4%.", True),
            ("SLR", "18% of NDTL ⚠ verify", "% of NDTL held in approved G-secs/gold/cash. Standard level 18%. No news-event revision reported in FY26. Banks borrow under MSF against SLR.", True),
            ("Base for both CRR & SLR", "NDTL (Net Demand and Time Liabilities)", "NDTL = Demand liabilities + Time liabilities − Inter-bank liabilities.", False),
            ("PSL — domestic SCBs", "40% of ANBC", "Priority Sector Lending total. Sub-targets: Agriculture 18% (incl. 10% to SMFs), Micro enterprises 7.5%, Weaker sections 12%.", False),
            ("Agriculture PSL sub-target", "18% of ANBC", "Of which ≥10% must go to Small & Marginal Farmers specifically.", False),
        ],
    },
    {
        "label": "Banking Regulation & Asset Quality",
        "color": "#F28B82",
        "items": [
            ("NPA trigger", "90 days overdue", "Interest/installment unpaid for 90 days → Sub-Standard NPA. Applies to term loans and OD/CC (90 days out of order).", False),
            ("NPA categories", "Sub-standard → Doubtful → Loss", "Sub-standard (<12 months NPA) → Doubtful (12–36 months) → Loss (>3 yrs or deemed unrecoverable).", False),
            ("CRAR minimum (India)", "9% (Basel III global: 8%)", "RBI mandates 9%. With Capital Conservation Buffer (CCB = 2.5%) → effective minimum = 11.5%.", False),
            ("Stressed assets", "Gross NPA + Restructured Standard Assets", "Broader than GNPA. Captures restructured loans that avoided NPA classification.", False),
            ("PCA triggers", "Net NPA > 6%; CRAR below threshold; ROA < 0 for 2 yrs", "Prompt Corrective Action. Any one trigger → restrictions on dividends, lending, branches.", False),
            ("IBC CIRP timeline", "180 days + 90 days extension = 270 days max", "Insolvency & Bankruptcy Code 2016. Time-bound NCLT process to maximise creditor recovery.", False),
        ],
    },
    {
        "label": "Payment Infrastructure",
        "color": "#81C995",
        "items": [
            ("RTGS", "Min ₹2 lakh · Real-time · 24×7 · Operated by RBI", "Real Time Gross Settlement. Individual transaction, gross settlement instantly. No upper limit.", False),
            ("NEFT", "No minimum · 48 half-hourly batches · 24×7 · Operated by RBI", "Deferred Net Settlement (DNS). Retail payments. Available 24×7 since Dec 2019.", False),
            ("NPCI operates", "UPI, IMPS, RuPay, NACH, FASTag, AePS, BBPS", "National Payments Corporation of India. Exam trap: RTGS and NEFT are RBI; UPI/IMPS etc. are NPCI.", False),
            ("e-RUPI", "Digital voucher — NOT CBDC", "Person/purpose-specific prepaid e-voucher for targeted DBT (health, education). Developed by NPCI. Aug 2021.", False),
            ("Digital Rupee (e₹)", "CBDC — Central Bank Digital Currency", "Legal tender issued by RBI. Retail pilot Nov 2022, Wholesale Dec 2022. Not a cryptocurrency.", False),
            ("NACH", "Bulk recurring: salary / pension / EMI / utilities", "National Automated Clearing House (NPCI). Replaced ECS. Handles bulk credit and debit mandates.", False),
        ],
    },
    {
        "label": "Fiscal Framework",
        "color": "#FDD663",
        "items": [
            ("GFD formula", "Total Expenditure − Revenue Receipts − Non-debt Capital Receipts", "Gross Fiscal Deficit = total borrowing requirement. Non-debt capital receipts include disinvestment.", False),
            ("GFD — FY26-27 BE", "4.3% of GDP · Rs 16,95,768 cr", "Down from 4.4% (FY25-26 RE) and 4.8% (FY24-25 actual). Govt pivot: now targeting debt/GDP ≤ 50% ± 1% by 2031.", False),
            ("Revenue Deficit — FY26-27 BE", "1.5% of GDP · Rs 5,92,344 cr", "Revenue Expenditure − Revenue Receipts. Flat at 1.5% — borrowing partly for recurring spending.", False),
            ("Primary Deficit — FY26-27 BE", "0.7% of GDP · Rs 2,91,796 cr", "GFD − Interest Payments. Declining fast (was 2.5% in FY22). Shows improving underlying fiscal position.", False),
            ("Capital Expenditure — FY26-27 BE", "Rs 12.21 lakh crore (+11.5% over RE)", "Highest ever. Share of capex in total expenditure rose from 12.5% (FY20) to 22.1% (FY25). Effective capex = Rs 17.1 lakh crore.", False),
            ("Gross Market Borrowing FY26-27", "Rs 17.2 lakh crore · Net: Rs 11.7 lakh crore", "G-sec supply figure. Difference = repayment of maturing securities (~Rs 5.5 lakh crore).", False),
            ("Disinvestment FY26-27 BE", "Rs 80,000 crore", "First increase in target after 5 consecutive years of cuts/shortfalls. FY25-26 actual ~Rs 34,000 crore.", False),
            ("States' share in divisible pool (16th FC)", "41% (unchanged from 15th FC)", "16th FC Chair: Dr Arvind Panagariya. Report tabled Feb 1, 2026. Total grants 2026-31: Rs 9.47 lakh crore.", False),
            ("FRBM / debt anchor", "GFD ≤ 3% of GDP (target) · Debt anchor: 50% ± 1% by 2031", "Centre not yet at 3% (currently 4.3%). Pivoted to debt-GDP targeting. 16th FC recommends 3.5% by 2030-31.", False),
            ("Interest payments burden", "26% of total expenditure · 40% of revenue receipts", "Rs 14.04 lakh crore in FY26-27 BE. 65.3% of revenue receipts go to committed expenditure.", False),
            ("Economic Survey", "Day before Union Budget · Prepared by CEA", "Chief Economic Adviser's macroeconomic review of the year. Not the budget itself.", False),
            ("Union Budget date", "February 1 (since 2017)", "Changed from last-day-of-Feb (colonial practice) to Feb 1 under Arun Jaitley.", False),
        ],
    },
    {
        "label": "Indian Economy — Quick Facts",
        "color": "#9AA0A6",
        "items": [
            ("GDP rank by nominal size", "4th largest globally (surpassed Japan)", "Surpassed Japan to become 4th largest (Vision IAS PT 365 2026). Aspiration: 3rd by early 2030s.", False),
            ("Real GDP growth FY26", "7.6% (2nd Advance Estimate, new base 2022-23)", "GDP base year revised to 2022-23. FY25: 7.1%. FY27 projection: 6.8–7.2% (Economic Survey).", False),
            ("GDP composition (FY26 FAE)", "Services 9.1% growth · Manufacturing 7.0% · Agriculture 3.1%", "Sectoral growth rates. Services = 57–60% of GVA; Agriculture ~15% of GVA but ~45% of employment.", False),
            ("GDP base year", "2022-23 (newly revised from 2011-12)", "MoSPI revised base year in FY26. Earlier base was 2011-12 (from 2004-05). Growth rates may differ slightly.", False),
            ("Headline CPI — FY26 (Apr–Dec)", "1.7% · Core CPI: 4.3% (2.9% excl. gold/silver)", "Sharp disinflation from food prices. Core ex-gold = 2.9% — limited demand overheating.", False),
            ("CPI base year", "2024 (newly revised from 2012)", "MoSPI revised CPI base year. RBI targets CPI (Combined) at 4% ± 2% under FITF.", False),
            ("MPC inflation target", "4% ± 2% (2%–6%) · FITF ⚠ verify renewal", "FITF was effective until March 31, 2026. Typically renewed every 5 years. Verify if new target differs.", True),
            ("Gross NPA ratio", "2.2% (Sep 2025) — multi-decade low", "Peak was 11.2% (March 2018). Slippage ratio: 0.7%. Bank credit growth: ~11.4% YoY (Nov 2025).", False),
            ("RBI surplus transfer to Govt", "Rs 2.68 lakh crore (FY25 — record)", "27% higher than FY24 transfer. Under revised Economic Capital Framework (ECF, 2025 review).", False),
            ("S&P sovereign rating", "BBB (upgraded from BBB–)", "First upgrade from a major agency in ~2 decades. India also got Morningstar DBRS and R&I upgrades in 2025.", False),
            ("PMJDY", "~56 crore beneficiaries", "Zero-balance, ₹10,000 OD, RuPay card, ₹2L accidental insurance. Linked to Aadhaar for DBT.", False),
            ("FI-Index (RBI)", "67 in 2025 (↑ 24.3% since 2021)", "Scale 0-100. Three dimensions: Access (35%), Usage (45%), Quality (20%). Published annually in July.", False),
            ("MUDRA (PMMY)", "52 crore borrowers · Rs 32.61 lakh crore credit", "10 years in 2025. Kishor loans grew from 5.9% (FY16) to 44.7% (FY25) of total.", False),
            ("Unemployment survey", "PLFS — Periodic Labour Force Survey (MoSPI)", "LFPR: 59.6% (2024). Unemployment rate 4.9% (Dec 2025). Revamped PLFS from Jan 2024.", False),
        ],
    },
]

# ── MCQ buckets ────────────────────────────────────────────────────────────────
# correct must be an exact string match of one of opts
BUCKETS = {
    "rbi_instruments": {
        "label": "RBI Instruments & Liquidity",
        "icon": "⚙",
        "qs": [
            {
                "id": "ri_1",
                "q": "Which rate serves as the floor of the LAF corridor as of April 2022?",
                "opts": ["A) Reverse Repo Rate", "B) Standing Deposit Facility (SDF) Rate", "C) Bank Rate", "D) Repo Rate"],
                "correct": "B) Standing Deposit Facility (SDF) Rate",
                "exp": "SDF replaced reverse repo as the LAF floor in April 2022. Collateral-free — banks park surplus with RBI without pledging G-secs. SDF = Repo − 25 bps.",
            },
            {
                "id": "ri_2",
                "q": "The Marginal Standing Facility (MSF) rate is fixed at:",
                "opts": ["A) Repo − 25 bps", "B) Repo + 50 bps", "C) Repo + 25 bps", "D) Equal to Bank Rate"],
                "correct": "C) Repo + 25 bps",
                "exp": "MSF is the LAF corridor ceiling at Repo + 25 bps. Emergency overnight window; banks can dip into up to 3% of NDTL from their SLR portfolio.",
            },
            {
                "id": "ri_3",
                "q": "Both CRR and SLR are computed as a percentage of:",
                "opts": ["A) Total Assets", "B) Risk-Weighted Assets", "C) Gross Advances", "D) Net Demand and Time Liabilities (NDTL)"],
                "correct": "D) Net Demand and Time Liabilities (NDTL)",
                "exp": "NDTL = demand liabilities + time liabilities − inter-bank liabilities. Both CRR and SLR use NDTL as the base for computation.",
            },
            {
                "id": "ri_4",
                "q": "When RBI conducts OMO by buying G-secs from banks, the primary effect is:",
                "opts": ["A) Liquidity absorption from the system", "B) Liquidity injection into the system", "C) Increase in SLR requirement", "D) Reduction in repo rate"],
                "correct": "B) Liquidity injection into the system",
                "exp": "OMO Purchase → RBI pays banks → money enters system (injection). OMO Sale → RBI sells G-secs → absorbs liquidity. Used for durable liquidity management.",
            },
            {
                "id": "ri_5",
                "q": "The LAF corridor is bounded by:",
                "opts": ["A) Reverse Repo Rate and MSF Rate", "B) SDF Rate and MSF Rate", "C) Repo Rate and Bank Rate", "D) CRR floor and SLR ceiling"],
                "correct": "B) SDF Rate and MSF Rate",
                "exp": "Post-April 2022: SDF (floor, Repo−25bps) ↔ Repo (policy rate) ↔ MSF (ceiling, Repo+25bps). Symmetric ±25 bps = 50 bps total corridor width.",
            },
            {
                "id": "ri_6",
                "q": "Variable Rate Reverse Repo (VRRR) auctions are primarily used by RBI to:",
                "opts": ["A) Inject durable liquidity at a fixed rate", "B) Absorb excess surplus liquidity from banks", "C) Signal a reduction in repo rate", "D) Regulate NBFC borrowings"],
                "correct": "B) Absorb excess surplus liquidity from banks",
                "exp": "VRRR is a market-based absorption tool. Banks bid at market-determined rates, letting RBI drain surplus liquidity in a calibrated manner, complementing the SDF.",
            },
        ],
    },
    "banking_norms": {
        "label": "Banking Regulation & NPA",
        "icon": "🏛",
        "qs": [
            {
                "id": "bn_1",
                "q": "A loan account is classified as NPA if interest or installment remains overdue for more than:",
                "opts": ["A) 30 days", "B) 60 days", "C) 90 days", "D) 180 days"],
                "correct": "C) 90 days",
                "exp": "90-day NPA norm: unpaid interest/principal for 90 days → Sub-Standard asset. Applies to term loans and OD/CC accounts (90 days continuously out of order).",
            },
            {
                "id": "bn_2",
                "q": "Under Basel III as implemented by RBI, the minimum CRAR for commercial banks is:",
                "opts": ["A) 8%", "B) 9%", "C) 10%", "D) 11.5%"],
                "correct": "B) 9%",
                "exp": "Basel III global minimum = 8%. RBI mandates 9% for Indian banks. Including Capital Conservation Buffer (CCB = 2.5%), effective minimum CRAR = 11.5%.",
            },
            {
                "id": "bn_3",
                "q": "'Stressed assets' in the Indian banking system refers to:",
                "opts": ["A) NPAs alone", "B) Restructured standard assets alone", "C) NPAs + Restructured Standard Assets", "D) Doubtful assets only"],
                "correct": "C) NPAs + Restructured Standard Assets",
                "exp": "Stressed assets = Gross NPAs + Restructured Standard Assets. Captures the full extent of asset quality problems including restructured loans that avoided NPA classification.",
            },
            {
                "id": "bn_4",
                "q": "Under IBC 2016, the maximum duration of the Corporate Insolvency Resolution Process (CIRP) is:",
                "opts": ["A) 90 days", "B) 180 days", "C) 270 days", "D) 365 days"],
                "correct": "C) 270 days",
                "exp": "CIRP: 180 days initial + 90 days NCLT-approved extension = 270 days max. Time-bound to prevent value erosion. Resolution plan voted by Committee of Creditors.",
            },
            {
                "id": "bn_5",
                "q": "One of the triggers for RBI's Prompt Corrective Action (PCA) framework is:",
                "opts": ["A) CRAR falls below 12%", "B) Net NPA ratio exceeds 6%", "C) Credit growth exceeds 20% YoY", "D) ROE falls below 8%"],
                "correct": "B) Net NPA ratio exceeds 6%",
                "exp": "PCA triggers (any one): CRAR below threshold; Net NPA > 6%; ROA negative for 2 consecutive years. PCA restricts dividends, branch opening, fresh lending.",
            },
            {
                "id": "bn_6",
                "q": "Gross NPA Ratio of a bank is calculated as:",
                "opts": ["A) Net NPA / Net Advances × 100", "B) Gross NPA / Risk-Weighted Assets × 100", "C) Gross NPA / Gross Advances × 100", "D) Total Provisions / Total Assets × 100"],
                "correct": "C) Gross NPA / Gross Advances × 100",
                "exp": "Gross NPA Ratio = (Gross NPAs / Gross Advances) × 100. Net NPA Ratio uses Net NPAs (after provisions) over Net Advances. Both are standard asset-quality metrics.",
            },
        ],
    },
    "payment_systems": {
        "label": "Payment Systems & Infra",
        "icon": "💳",
        "qs": [
            {
                "id": "ps_1",
                "q": "RTGS is designed for:",
                "opts": ["A) Retail transactions below ₹2 lakh", "B) High-value real-time transactions with minimum ₹2 lakh", "C) G-sec auction settlements only", "D) Cross-border SWIFT alternative"],
                "correct": "B) High-value real-time transactions with minimum ₹2 lakh",
                "exp": "RTGS: continuous, individual, real-time gross settlement. Min ₹2 lakh, no upper limit. Available 24×7 since Dec 2020. Operated by RBI.",
            },
            {
                "id": "ps_2",
                "q": "NEFT uses which settlement mechanism?",
                "opts": ["A) Real-time individual gross settlement", "B) Deferred Net Settlement in half-hourly batches", "C) Daily end-of-day batch netting", "D) Weekly bilateral netting"],
                "correct": "B) Deferred Net Settlement in half-hourly batches",
                "exp": "NEFT = Deferred Net Settlement (DNS), 48 half-hourly batches, 24×7 since Dec 2019. No minimum/maximum. Retail payments. Operated by RBI.",
            },
            {
                "id": "ps_3",
                "q": "Which of the following is operated by RBI, NOT by NPCI?",
                "opts": ["A) IMPS", "B) UPI", "C) NEFT", "D) RuPay"],
                "correct": "C) NEFT",
                "exp": "RBI operates: RTGS and NEFT. NPCI operates: UPI, IMPS, RuPay, NACH, FASTag, AePS, BBPS. Classic MCQ trap — NEFT looks like an NPCI product but it is RBI.",
            },
            {
                "id": "ps_4",
                "q": "e-RUPI (launched August 2021) is best described as:",
                "opts": ["A) India's retail Central Bank Digital Currency", "B) A UPI-based credit facility for BPL households", "C) A person/purpose-specific digital voucher for targeted benefit delivery", "D) A mobile wallet issued by RBI"],
                "correct": "C) A person/purpose-specific digital voucher for targeted benefit delivery",
                "exp": "e-RUPI: digital prepaid voucher — redeemable only by the intended beneficiary for the specified purpose. Developed by NPCI with DFS and NHA. NOT the same as the CBDC (e₹).",
            },
            {
                "id": "ps_5",
                "q": "The Digital Rupee (e₹) introduced by RBI is classified as:",
                "opts": ["A) A private-sector cryptocurrency backed by gold", "B) A Central Bank Digital Currency (CBDC)", "C) An upgraded UPI with offline capability", "D) A SEBI-regulated stablecoin"],
                "correct": "B) A Central Bank Digital Currency (CBDC)",
                "exp": "e₹ is India's CBDC — legal tender, issued and backed by RBI. Retail pilot Nov 2022; Wholesale Dec 2022. Not decentralised, not mined. Distinct from cryptocurrency.",
            },
            {
                "id": "ps_6",
                "q": "NACH (National Automated Clearing House) is primarily used for:",
                "opts": ["A) Large-value real-time interbank settlement", "B) Bulk recurring transactions like salary, pension, EMI, utility bills", "C) Foreign currency trade settlements", "D) Government securities auctions"],
                "correct": "B) Bulk recurring transactions like salary, pension, EMI, utility bills",
                "exp": "NACH (NPCI) replaced ECS. Handles large-volume, recurring, low-value credit (salary) and debit (EMI mandate) flows efficiently.",
            },
        ],
    },
    "financial_inclusion": {
        "label": "Financial Inclusion & PSL",
        "icon": "🤝",
        "qs": [
            {
                "id": "fi_1",
                "q": "A key feature of PMJDY basic savings accounts is:",
                "opts": ["A) Mandatory minimum balance of ₹500", "B) Zero balance with ₹10,000 overdraft facility", "C) No overdraft, ₹50,000 accident insurance only", "D) Fixed deposit linked to Aadhaar only"],
                "correct": "B) Zero balance with ₹10,000 overdraft facility",
                "exp": "PMJDY (Aug 2014): zero-balance BSBD account, RuPay card, ₹2 lakh accidental insurance, ₹30,000 life cover, ₹10,000 OD for Aadhaar-seeded accounts active ≥6 months.",
            },
            {
                "id": "fi_2",
                "q": "Under MUDRA Yojana, the 'Shishu' category covers loan amounts:",
                "opts": ["A) Up to ₹50,000", "B) ₹50,001 to ₹5 lakh", "C) ₹5 lakh to ₹10 lakh", "D) Up to ₹1 lakh"],
                "correct": "A) Up to ₹50,000",
                "exp": "MUDRA: Shishu ≤ ₹50,000 | Kishore ₹50,001–₹5 lakh | Tarun ₹5–₹10 lakh. For non-corporate, non-farm micro-enterprises. No collateral for Shishu/Kishore.",
            },
            {
                "id": "fi_3",
                "q": "The PSL sub-target for agriculture for domestic scheduled commercial banks is:",
                "opts": ["A) 10% of ANBC", "B) 15% of ANBC", "C) 18% of ANBC", "D) 25% of ANBC"],
                "correct": "C) 18% of ANBC",
                "exp": "Agriculture PSL sub-target = 18% of ANBC, of which ≥10% must go to Small & Marginal Farmers. Total PSL = 40% of ANBC for domestic SCBs.",
            },
            {
                "id": "fi_4",
                "q": "The total PSL target for domestic scheduled commercial banks is:",
                "opts": ["A) 32% of ANBC", "B) 35% of ANBC", "C) 40% of ANBC", "D) 45% of ANBC"],
                "correct": "C) 40% of ANBC",
                "exp": "40% of ANBC (or CEOBSE, whichever higher) for domestic SCBs. Foreign banks ≥20 branches: same 40%. Sub-targets: Agriculture 18%, Micro 7.5%, Weaker sections 12%.",
            },
            {
                "id": "fi_5",
                "q": "RBI's Financial Inclusion Index (FI-Index) is measured on a scale of:",
                "opts": ["A) 0 to 10", "B) 0 to 100", "C) 0 to 1 (decimal)", "D) 0 to 500"],
                "correct": "B) 0 to 100",
                "exp": "FI-Index: 0 = complete exclusion, 100 = full inclusion. Three dimensions: Access (weight 35), Usage (45), Quality (20). Published annually in July by RBI.",
            },
            {
                "id": "fi_6",
                "q": "CGTMSE (Credit Guarantee Fund Trust for MSEs) is jointly established by:",
                "opts": ["A) RBI and SEBI", "B) NABARD and World Bank", "C) Government of India and SIDBI", "D) Ministry of Finance and NPCI"],
                "correct": "C) Government of India and SIDBI",
                "exp": "CGTMSE (est. 2000): collateral-free credit guarantees for MSE loans up to ₹5 crore. Set up by MoMSME (GoI) and SIDBI. Reduces bank risk for MSME lending.",
            },
        ],
    },
    "fiscal_framework": {
        "label": "Budget & Fiscal Framework",
        "icon": "📋",
        "qs": [
            {
                "id": "ff_1",
                "q": "Primary Deficit is defined as:",
                "opts": ["A) Revenue Expenditure minus Revenue Receipts", "B) Gross Fiscal Deficit minus Interest Payments", "C) Capital Expenditure minus Capital Receipts", "D) GFD minus Revenue Deficit"],
                "correct": "B) Gross Fiscal Deficit minus Interest Payments",
                "exp": "Primary Deficit = GFD − Interest Payments. Zero Primary Deficit means borrowing is solely to service past debt. The portion of deficit policymakers can control in the short run.",
            },
            {
                "id": "ff_2",
                "q": "Revenue Deficit is:",
                "opts": ["A) Revenue Receipts minus Revenue Expenditure", "B) Revenue Expenditure minus Revenue Receipts", "C) GFD minus Capital Expenditure", "D) Total Expenditure minus Total Receipts"],
                "correct": "B) Revenue Expenditure minus Revenue Receipts",
                "exp": "Revenue Deficit = Revenue Expenditure − Revenue Receipts. Negative = revenue surplus. Revenue items are recurring (salaries, subsidies, interest, tax receipts).",
            },
            {
                "id": "ff_3",
                "q": "The Chief Economic Adviser (CEA) is responsible for:",
                "opts": ["A) Presenting the Union Budget in Parliament", "B) Chairing the Monetary Policy Committee", "C) Preparing the Economic Survey", "D) Approving the annual credit policy"],
                "correct": "C) Preparing the Economic Survey",
                "exp": "CEA prepares the Economic Survey (macroeconomic review). Finance Minister presents the Budget. MPC is chaired by RBI Governor. RBI does not separately announce a 'credit policy' anymore.",
            },
            {
                "id": "ff_4",
                "q": "The FRBM Act's medium-term Gross Fiscal Deficit target is:",
                "opts": ["A) 2% of GDP", "B) 2.5% of GDP", "C) 3% of GDP", "D) 4% of GDP"],
                "correct": "C) 3% of GDP",
                "exp": "FRBM Act 2003: medium-term GFD target = 3% of GDP. NK Singh Committee 2017 recommended 2.5% as the long-run floor and 40% debt/GDP by 2024-25.",
            },
            {
                "id": "ff_5",
                "q": "Gross Fiscal Deficit (GFD) equals:",
                "opts": ["A) Revenue Expenditure minus Revenue Receipts", "B) Total Expenditure minus Revenue Receipts minus Non-debt Capital Receipts", "C) Capital Expenditure minus Capital Receipts", "D) Total Expenditure minus Total Receipts"],
                "correct": "B) Total Expenditure minus Revenue Receipts minus Non-debt Capital Receipts",
                "exp": "GFD = Total Expenditure − Revenue Receipts − Non-debt Capital Receipts. Non-debt capital receipts include disinvestment proceeds. GFD = total net borrowing requirement.",
            },
            {
                "id": "ff_6",
                "q": "The Economic Survey is presented to Parliament:",
                "opts": ["A) On April 1 (first day of fiscal year)", "B) On the last working day of February", "C) The day before the Union Budget", "D) Simultaneously with the Union Budget"],
                "correct": "C) The day before the Union Budget",
                "exp": "Economic Survey is presented the day before the Union Budget. It sets the macroeconomic context and policy narrative. Prepared by CEA's office in the Finance Ministry.",
            },
        ],
    },
    "india_economy": {
        "label": "Indian Economy Structure",
        "icon": "🇮🇳",
        "qs": [
            {
                "id": "ie_1",
                "q": "India is currently the _____ largest economy by nominal GDP:",
                "opts": ["A) 3rd largest", "B) 4th largest", "C) 5th largest", "D) 6th largest"],
                "correct": "C) 5th largest",
                "exp": "India overtook UK to become 5th largest (~2023). Target is 3rd largest by early 2030s. Verify current ranking before exam as it may change by 2026.",
            },
            {
                "id": "ie_2",
                "q": "India's services sector contributes approximately what share of GDP?",
                "opts": ["A) About 30%", "B) About 40%", "C) About 50%", "D) Over 55%"],
                "correct": "D) Over 55%",
                "exp": "Services ~57–60% of GVA. Industry ~26–28%. Agriculture ~15–17%. Despite agriculture's declining GVA share, it still employs ~45% of the workforce.",
            },
            {
                "id": "ie_3",
                "q": "The current base year for India's GDP calculation is:",
                "opts": ["A) 2004-05", "B) 2007-08", "C) 2011-12", "D) 2017-18"],
                "correct": "C) 2011-12",
                "exp": "CSO revised base year from 2004-05 to 2011-12 in January 2015 and switched to GVA methodology. A new revision to 2022-23 base is underway.",
            },
            {
                "id": "ie_4",
                "q": "India's merchandise trade deficit is primarily driven by:",
                "opts": ["A) Software and IT service imports", "B) Oil and gold imports", "C) External debt repayment outflows", "D) Capital goods imports only"],
                "correct": "B) Oil and gold imports",
                "exp": "India's CAD is driven by the merchandise deficit, primarily oil (energy import dependent) and gold (structural demand). Partially offset by services surplus (IT/BPO).",
            },
            {
                "id": "ie_5",
                "q": "Consumer Price Index (CPI) in India is published by:",
                "opts": ["A) RBI", "B) MoSPI (Ministry of Statistics & PI)", "C) Labour Bureau, Ministry of Labour", "D) SEBI"],
                "correct": "B) MoSPI (Ministry of Statistics & PI)",
                "exp": "MoSPI releases monthly CPI (Combined). RBI uses CPI as its inflation target under Flexible Inflation Targeting (FIT). Trap: RBI uses CPI but does NOT publish it.",
            },
            {
                "id": "ie_6",
                "q": "India's official unemployment rate is measured using which survey?",
                "opts": ["A) Census of India", "B) Economic Census", "C) Annual Survey of Industries (ASI)", "D) PLFS (Periodic Labour Force Survey)"],
                "correct": "D) PLFS (Periodic Labour Force Survey)",
                "exp": "PLFS published by MoSPI replaced the NSSO Employment-Unemployment Survey. Provides quarterly LFPR, WPR, UR for urban; annual for rural+urban combined.",
            },
        ],
    },
}

BUCKET_KEYS = list(BUCKETS.keys())
BUCKET_LABELS = [f"{BUCKETS[k]['icon']} {BUCKETS[k]['label']}" for k in BUCKET_KEYS]

# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("rbi6_bucket", BUCKET_KEYS[0]),
    ("rbi6_submitted", False),
    ("rbi6_answers", {}),
    ("rbi6_session", str(uuid.uuid4())),
    ("rbi6_scores", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏦 RBI Prep")
    d = days_to_rbi()
    color = "#F28B82" if d <= 7 else "#FDD663" if d <= 14 else "#81C995"
    st.markdown(
        f'<div class="gem-card" style="text-align:center;border-color:{color}33">'
        f'<div style="font-size:2rem;font-weight:700;color:{color}">{d}</div>'
        f'<div style="font-size:0.72rem;color:#9AA0A6;text-transform:uppercase;letter-spacing:.06em">Days to RBI DEPR</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption("**June 14:** RBI DEPR Phase 1")
    st.caption("Paper 1: Economics MCQ (100m, 65 Qs)")
    st.caption("Paper 2: English Typed (100m, 120 min)")
    st.divider()

    scores = st.session_state.rbi6_scores
    if scores:
        st.markdown('<div class="section-header">Quiz Progress</div>', unsafe_allow_html=True)
        for bk in BUCKET_KEYS:
            if bk in scores:
                s = scores[bk]
                pct = s["correct"] / s["total"]
                color_q = "#81C995" if pct >= 0.8 else "#FDD663" if pct >= 0.5 else "#F28B82"
                label = BUCKETS[bk]["icon"]
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
                    f'<span style="font-size:0.78rem;color:#9AA0A6">{label} {BUCKETS[bk]["label"][:22]}…</span>'
                    f'<span style="font-size:0.78rem;font-weight:600;color:{color_q}">{s["correct"]}/{s["total"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.caption("Complete quiz buckets to see progress here.")

    st.divider()
    st.caption("⚠ Items marked ⚠ need live verification at rbi.org.in")

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("## 🏦 RBI DEPR Phase 1 Prep")
st.caption("Tier 2 quick reference + 36 MCQs across 6 topic buckets · no AI cost")

tab1, tab2 = st.tabs(["📊 Key Data Cards", "❓ Tier 2 Quiz"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Key Data Cards
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.info("Items marked ⚠ depend on current RBI/MoSPI data — verify at rbi.org.in before exam day.", icon="⚠")

    for section in KEY_SECTIONS:
        label = section["label"]
        color = section["color"]
        items = section["items"]

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:24px 0 10px">'
            f'<div style="width:4px;height:20px;background:{color};border-radius:2px"></div>'
            f'<span style="font-size:0.95rem;font-weight:600;color:#E8EAED">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for name, value, note, verify in items:
            verify_badge = (
                '<span style="font-size:0.68rem;font-weight:700;color:#F28B82;background:rgba(242,139,130,0.12);'
                'border:1px solid rgba(242,139,130,0.3);border-radius:10px;padding:1px 7px;margin-left:6px">⚠ VERIFY</span>'
                if verify else ""
            )
            st.markdown(
                f'<div class="gem-card-sm" style="border-left:3px solid {color}40">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:4px">'
                f'<span style="font-size:0.82rem;font-weight:600;color:#E8EAED">{name}{verify_badge}</span>'
                f'<span style="font-size:0.82rem;font-weight:700;color:{color};text-align:right;max-width:55%">{value}</span>'
                f'</div>'
                f'<div style="font-size:0.76rem;color:#9AA0A6;margin-top:5px;line-height:1.4">{note}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Tier 2 Quiz
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    col_left, col_right = st.columns([1, 3], gap="large")

    with col_left:
        st.markdown('<div class="section-header">Topic Bucket</div>', unsafe_allow_html=True)
        selected_label = st.radio(
            "Select bucket",
            BUCKET_LABELS,
            index=BUCKET_KEYS.index(st.session_state.rbi6_bucket),
            key="rbi6_bucket_radio",
            label_visibility="collapsed",
        )
        selected_bucket_key = BUCKET_KEYS[BUCKET_LABELS.index(selected_label)]

        if selected_bucket_key != st.session_state.rbi6_bucket:
            st.session_state.rbi6_bucket = selected_bucket_key
            st.session_state.rbi6_submitted = False
            st.session_state.rbi6_answers = {}
            st.session_state.rbi6_session = str(uuid.uuid4())
            st.rerun()

        st.divider()
        total_done = sum(1 for bk in BUCKET_KEYS if bk in st.session_state.rbi6_scores)
        st.markdown(
            f'<div style="font-size:0.78rem;color:#9AA0A6">Buckets completed: '
            f'<strong style="color:#E8EAED">{total_done}/{len(BUCKET_KEYS)}</strong></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        bucket = BUCKETS[selected_bucket_key]
        questions = bucket["qs"]

        st.markdown(f"### {bucket['icon']} {bucket['label']}")
        st.caption(f"{len(questions)} questions · instant grading · no AI")

        # ── RESULT VIEW ─────────────────────────────────────────────────────
        if st.session_state.rbi6_submitted:
            answers = st.session_state.rbi6_answers
            correct_count = sum(
                1 for q in questions
                if answers.get(q["id"], "").strip() == q["correct"].strip()
            )
            total = len(questions)
            score_pct = correct_count / total

            score_color_cls = "score-green" if score_pct >= 0.8 else "score-amber" if score_pct >= 0.5 else "score-red"
            icon = "🟢" if score_pct >= 0.8 else "🟡" if score_pct >= 0.5 else "🔴"

            st.markdown(
                f'<div class="score-card {score_color_cls}" style="margin-bottom:16px">'
                f'<div class="score-num">{icon} {correct_count}/{total}</div>'
                f'<div class="score-label">{int(score_pct * 100)}% correct</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown("#### Per-question breakdown")
            for i, q in enumerate(questions):
                user_ans = answers.get(q["id"], "")
                is_correct = user_ans.strip() == q["correct"].strip()
                icon_q = "✅" if is_correct else "❌"
                with st.expander(f"{icon_q} Q{i+1}  ·  {q['q'][:80]}{'…' if len(q['q']) > 80 else ''}"):
                    for opt in q["opts"]:
                        is_opt_correct = opt.strip() == q["correct"].strip()
                        is_opt_chosen = opt.strip() == user_ans.strip()
                        if is_opt_correct and is_opt_chosen:
                            st.markdown(f"**✓ {opt}** ← your answer ✅")
                        elif is_opt_correct:
                            st.markdown(f"**✓ {opt}** ← correct answer")
                        elif is_opt_chosen:
                            st.markdown(f"~~{opt}~~ ← your answer ❌")
                        else:
                            st.markdown(f"  {opt}")
                    st.info(f"**Why:** {q['exp']}")

            col_retry, col_next = st.columns(2)
            with col_retry:
                if st.button("↩ Retry this bucket", use_container_width=True):
                    st.session_state.rbi6_submitted = False
                    st.session_state.rbi6_answers = {}
                    st.session_state.rbi6_session = str(uuid.uuid4())
                    st.rerun()
            with col_next:
                curr_idx = BUCKET_KEYS.index(selected_bucket_key)
                next_idx = (curr_idx + 1) % len(BUCKET_KEYS)
                next_key = BUCKET_KEYS[next_idx]
                next_label = BUCKETS[next_key]["label"][:28]
                if st.button(f"Next → {next_label}…", use_container_width=True, type="primary"):
                    st.session_state.rbi6_bucket = next_key
                    st.session_state.rbi6_submitted = False
                    st.session_state.rbi6_answers = {}
                    st.session_state.rbi6_session = str(uuid.uuid4())
                    st.rerun()

        # ── QUIZ FORM ────────────────────────────────────────────────────────
        else:
            st.markdown("Answer all questions, then submit.")
            st.caption("Explanations shown after submission.")

            answers: dict[str, str] = {}
            form_key = f"rbi6_form_{selected_bucket_key}_{st.session_state.rbi6_session}"

            with st.form(form_key):
                for i, q in enumerate(questions):
                    st.markdown(f"**Q{i+1}.** {q['q']}")
                    chosen = st.radio(
                        "",
                        q["opts"],
                        index=None,
                        key=f"rbi6_radio_{q['id']}",
                        label_visibility="collapsed",
                    )
                    answers[q["id"]] = chosen or ""
                    if i < len(questions) - 1:
                        st.markdown("---")

                st.markdown("")
                submitted = st.form_submit_button("Submit →", use_container_width=True, type="primary")

            if submitted:
                unanswered = [i + 1 for i, q in enumerate(questions) if not answers.get(q["id"])]
                if unanswered:
                    nums = ", ".join(f"Q{n}" for n in unanswered)
                    st.warning(f"Please answer {nums} before submitting.")
                else:
                    correct_count = sum(
                        1 for q in questions
                        if answers.get(q["id"], "").strip() == q["correct"].strip()
                    )
                    st.session_state.rbi6_scores[selected_bucket_key] = {
                        "correct": correct_count,
                        "total": len(questions),
                    }
                    st.session_state.rbi6_answers = answers
                    st.session_state.rbi6_submitted = True
                    st.rerun()
