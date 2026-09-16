// Tax estimator helpers — informational estimates only.
// Rates/reliefs reflect the Nigeria Tax Act 2025 (effective 1 January 2026) as
// commonly published. These are NOT advice and must always be accompanied by
// the estimator disclaimer. Figures are kept in one place for easy maintenance.

import { toWords } from './currencyWords';

// ── PAYE (2026) ───────────────────────────────────────────────────────────────
// Progressive bands on chargeable income (gross − allowable deductions):
//   First ₦800,000                         0%
//   Next ₦2,200,000  (₦800,001 – ₦3M)     15%
//   Next ₦9,000,000  (₦3,000,001 – ₦12M)  18%
//   Next ₦13,000,000 (₦12,000,001 – ₦25M) 21%
//   Next ₦25,000,000 (₦25,000,001 – ₦50M) 23%
//   Above ₦50M                            25%
export const PAYE_BRACKETS = [
  { start: 0, end: 800_000, rate: 0 },
  { start: 800_000, end: 3_000_000, rate: 0.15 },
  { start: 3_000_000, end: 12_000_000, rate: 0.18 },
  { start: 12_000_000, end: 25_000_000, rate: 0.21 },
  { start: 25_000_000, end: 50_000_000, rate: 0.23 },
  { start: 50_000_000, end: Infinity, rate: 0.25 },
];

export const PENSION_DEFAULT_RATE = 0.08; // 8% employee pension contribution (of gross)
export const PENSION_EMPLOYER_RATE = 0.10; // 10% employer pension contribution
export const NHF_RATE = 0.025; // 2.5% of basic monthly salary
export const RENT_RELIEF_CAP = 500_000; // 20% of annual rent, capped at ₦500,000
export const LIFE_ASSURANCE_CAP = 100_000; // life assurance premium, capped at ₦100,000
export const EXCESS_DIVIDEND_RATE = 0.1;

// ── CIT (2026) ────────────────────────────────────────────────────────────────
// Small company: turnover ≤ ₦100M AND fixed assets < ₦250M (professional
// service firms never qualify). Small → 0% CIT + 0% development levy.
// Everyone else → 30% + 4% development levy.
export const CIT_SMALL_TURNOVER = 100_000_000;
export const CIT_SMALL_ASSETS = 250_000_000;
export const CIT_STANDARD_RATE = 0.3;
export const DEV_LEVY_RATE = 0.04;

// ── VAT ───────────────────────────────────────────────────────────────────────
export const DEFAULT_VAT_RATE = 0.075; // 7.5%

// ── WHT (2026) ────────────────────────────────────────────────────────────────
// Amounts < ₦2,000,000 with a valid TIN are exempt. Without a TIN the rate is
// doubled, capped at 20%.
export const WHT_TIN_THRESHOLD = 2_000_000;
export const WHT_NO_TIN_CAP = 0.2;

export const WHT_RATES = [
  { id: 'dividends', label: 'Dividends', rate: 0.1, noTinRate: 0.2 },
  { id: 'interest', label: 'Interest', rate: 0.1, noTinRate: 0.2 },
  { id: 'rent', label: 'Rent', rate: 0.1, noTinRate: 0.2 },
  { id: 'professional', label: 'Professional / consultancy / management fees', rate: 0.05, noTinRate: 0.1 },
  { id: 'technical', label: 'Technical services', rate: 0.05, noTinRate: 0.1 },
  { id: 'management', label: 'Management services', rate: 0.05, noTinRate: 0.1 },
  { id: 'goods', label: 'Supply of goods & materials', rate: 0.02, noTinRate: 0.04 },
  { id: 'contracts', label: 'Contract / construction payments', rate: 0.02, noTinRate: 0.04 },
];

// ── Stamp duty (Nigeria Tax Act 2025) ─────────────────────────────────────────
export const STAMP_DUTY_RATES = [
  { id: 'conveyance', label: 'Conveyance / transfer on sale (real property)', rate: 0.015, flat: null, exemptBelow: 10_000_000 },
  { id: 'lease-short', label: 'Lease — not exceeding 7 years', rate: 0.0078, flat: null, exemptBelow: null },
  { id: 'lease-long', label: 'Lease — exceeding 7 years', rate: 0.03, flat: null, exemptBelow: null },
  { id: 'mortgage', label: 'Mortgage / security', rate: 0.00375, flat: null, exemptBelow: null },
  { id: 'share-capital', label: 'Nominal share capital', rate: 0.0075, flat: null, exemptBelow: null },
  { id: 'loan-capital', label: 'Loan capital', rate: 0.00125, flat: null, exemptBelow: null },
  { id: 'mineral', label: 'Transfer of mineral assets', rate: 0.02, flat: null, exemptBelow: null },
  { id: 'marketable', label: 'Marketable securities', rate: 0.00225, flat: null, exemptBelow: null },
  { id: 'contract-note', label: 'Contract note', rate: 0.0008, flat: null, exemptBelow: null },
  { id: 'electronic', label: 'Electronic transfer (≥ ₦10,000)', rate: null, flat: 50, exemptBelow: null },
  { id: 'agreement', label: 'Agreement / contract (not otherwise specified)', rate: null, flat: 1_000, exemptBelow: null },
];

const naira = (n) => `₦${new Intl.NumberFormat('en-NG').format(Math.round(n))}`;

const applyBrackets = (income) => {
  let tax = 0;
  const breakdown = [];
  let prev = 0;

  for (const bracket of PAYE_BRACKETS) {
    if (income <= prev) break;
    const taxableInBand = Math.min(Math.max(income - prev, 0), bracket.end - prev);
    if (taxableInBand > 0) {
      const bandTax = taxableInBand * bracket.rate;
      tax += bandTax;
      if (bracket.rate > 0 || taxableInBand > 0) {
        breakdown.push({
          line: `${naira(prev)} – ${bracket.end === Infinity ? 'above' : naira(bracket.end)} @ ${bracket.rate * 100}%`,
          value: bandTax,
        });
      }
    }
    prev = bracket.end;
  }

  return { tax, breakdown };
};

// ── PAYE ──────────────────────────────────────────────────────────────────────
export function calcPAYE({
  monthlySalary = 0,
  pension = false,
  nhf = false,
  basicSalary = 0,
  annualRent = 0,
  lifeAssurance = 0,
} = {}) {
  const annualGross = monthlySalary * 12;
  const reliefs = [];

  const pensionContrib = pension ? annualGross * PENSION_DEFAULT_RATE : 0;
  const nhfContrib = nhf && basicSalary > 0 ? basicSalary * 12 * NHF_RATE : 0;
  const rentRelief = annualRent > 0 ? Math.min(annualRent * 0.2, RENT_RELIEF_CAP) : 0;
  const lifeRelief = lifeAssurance > 0 ? Math.min(lifeAssurance, LIFE_ASSURANCE_CAP) : 0;

  if (pensionContrib) reliefs.push({ line: `Employee pension (8% of gross)`, value: pensionContrib, cash: true });
  if (nhfContrib) reliefs.push({ line: `NHF (2.5% of basic salary)`, value: nhfContrib, cash: true });
  if (rentRelief) reliefs.push({ line: `Rent relief (20% of rent, capped ₦500k)`, value: rentRelief, cash: false });
  if (lifeRelief) reliefs.push({ line: `Life assurance premium (capped ₦100k)`, value: lifeRelief, cash: false });

  const totalRelief = pensionContrib + nhfContrib + rentRelief + lifeRelief;
  const chargeable = Math.max(annualGross - totalRelief, 0);

  const { tax, breakdown } = applyBrackets(chargeable);
  const monthlyTax = tax / 12;
  const cashDeductions = pensionContrib + nhfContrib;
  const monthlyTakeHome = monthlySalary - cashDeductions / 12 - monthlyTax;

  return {
    type: 'PAYE',
    period: 'annually',
    gross: annualGross,
    reliefs,
    chargeableIncome: chargeable,
    totalTax: tax,
    monthlyTax,
    monthlyTakeHome,
    breakdown,
  };
}

// ── Take-home pay (PAYE + pension + NHF) ──────────────────────────────────────
export function calcTakeHome({ monthlySalary = 0, pension = true, nhf = false, basicSalary = 0 } = {}) {
  const paye = calcPAYE({ monthlySalary, pension, nhf, basicSalary });
  return {
    ...paye,
    type: 'Take-home pay',
    employerPension: monthlySalary * 12 * PENSION_EMPLOYER_RATE,
  };
}

// ── Pension contribution ──────────────────────────────────────────────────────
export function calcPension({ monthlySalary = 0 } = {}) {
  const monthlyEmployee = monthlySalary * PENSION_DEFAULT_RATE;
  const monthlyEmployer = monthlySalary * PENSION_EMPLOYER_RATE;
  return {
    type: 'Pension',
    period: 'monthly',
    monthlyEmployee,
    monthlyEmployer,
    monthlyTotal: monthlyEmployee + monthlyEmployer,
    annualTotal: (monthlyEmployee + monthlyEmployer) * 12,
  };
}

// ── NHF ───────────────────────────────────────────────────────────────────────
export function calcNHF({ basicSalary = 0 } = {}) {
  const monthly = basicSalary * NHF_RATE;
  return {
    type: 'NHF',
    period: 'monthly',
    monthly,
    annual: monthly * 12,
  };
}

// ── CIT + Development Levy ────────────────────────────────────────────────────
export function calcCIT({ annualTurnover = 0, fixedAssets = 0, annualProfit = 0, isProfessional = false } = {}) {
  const isSmall =
    !isProfessional && annualTurnover <= CIT_SMALL_TURNOVER && fixedAssets < CIT_SMALL_ASSETS;

  const profit = annualProfit || annualTurnover * 0.4; // default profit margin assumption
  const citRate = isSmall ? 0 : CIT_STANDARD_RATE;
  const levyRate = isSmall ? 0 : DEV_LEVY_RATE;

  const cit = Math.max(profit * citRate, 0);
  const devLevy = Math.max(profit * levyRate, 0);

  return {
    type: 'CIT',
    period: 'annually',
    isSmall,
    citRate,
    levyRate,
    assessableProfit: profit,
    tierLabel: isSmall
      ? 'Small company (turnover ≤ ₦100M & assets < ₦250M, not a professional firm)'
      : 'Standard company (30% + 4% development levy)',
    breakdown: [
      { line: `Income tax — ${citRate * 100}% of assessable profit`, value: cit },
      ...(devLevy ? [{ line: `Development levy — ${levyRate * 100}% of assessable profit`, value: devLevy }] : []),
    ],
    totalTax: cit + devLevy,
    note: isSmall
      ? 'Small companies pay 0% CIT and are exempt from the development levy. Professional service firms never qualify as small.'
      : 'Assessable profit is estimated at 40% of turnover when profit is not provided.',
  };
}

// ── Development levy (standalone) ─────────────────────────────────────────────
export function calcDevelopmentLevy({ annualProfit = 0 } = {}) {
  const levy = Math.max(annualProfit * DEV_LEVY_RATE, 0);
  return {
    type: 'Development levy',
    period: 'annually',
    assessableProfit: annualProfit,
    totalTax: levy,
  };
}

// ── VAT ───────────────────────────────────────────────────────────────────────
export function calcVAT({ annualSales = 0, annualInputPurchases = 0 } = {}) {
  const outputVat = Math.max(annualSales, 0) * DEFAULT_VAT_RATE;
  const inputVat = Math.max(annualInputPurchases, 0) * DEFAULT_VAT_RATE;
  const netVat = outputVat - inputVat;

  return {
    type: 'VAT',
    period: 'annually',
    outputVat,
    inputVat,
    totalTax: netVat,
    breakdown: [
      { line: `Output VAT @ 7.5% on taxable supplies`, value: outputVat },
      ...(inputVat ? [{ line: `Input VAT @ 7.5% on qualifying purchases`, value: -inputVat }] : []),
    ],
    note: netVat < 0
      ? 'Input VAT exceeds output VAT. The excess credit carries forward or is claimed as a refund.'
      : 'Output shown before registration-threshold and exemption considerations.',
  };
}

// ── Non-resident digital services VAT (2026) ──────────────────────────────────
export function calcDigitalVAT({ annualTurnover = 0 } = {}) {
  const vat = Math.max(annualTurnover, 0) * DEFAULT_VAT_RATE;
  return {
    type: 'Digital services VAT',
    period: 'annually',
    totalTax: vat,
    note: 'Foreign providers of SaaS, streaming and ad services to Nigerian users are liable to 7.5% VAT with no turnover threshold.',
  };
}

// ── WHT ───────────────────────────────────────────────────────────────────────
export function calcWHT({ paymentType = 'professional', amount = 0, hasTin = true } = {}) {
  const rule = WHT_RATES.find((r) => r.id === paymentType) || WHT_RATES[0];

  let rate = rule.rate;
  let exemptionNote = null;

  if (!hasTin) {
    rate = Math.min(rule.rate * 2, WHT_NO_TIN_CAP);
    exemptionNote = 'No TIN provided — WHT doubled, capped at 20%.';
  } else if (amount < WHT_TIN_THRESHOLD) {
    rate = 0;
    exemptionNote = 'Payment under ₦2,000,000 with a valid TIN — WHT exempt.';
  }

  const tax = Math.max(amount * rate, 0);

  return {
    type: 'WHT',
    period: 'per payment',
    rate,
    breakdown: [{ line: `${rule.label} — ${rate * 100}% withheld`, value: tax }],
    totalTax: tax,
    netPayment: Math.max(amount - tax, 0),
    note: exemptionNote || 'WHT is withheld from the payment and remitted to NRS by the 21st of the following month.',
  };
}

// ── Stamp duty ────────────────────────────────────────────────────────────────
export function calcStampDuty({ instrumentType = 'conveyance', value = 0 } = {}) {
  const rule = STAMP_DUTY_RATES.find((r) => r.id === instrumentType) || STAMP_DUTY_RATES[0];
  const amount = Math.max(value, 0);

  let duty = 0;
  let note = null;

  if (rule.flat) {
    duty = rule.flat;
  } else if (rule.exemptBelow !== null && amount < rule.exemptBelow) {
    duty = 0;
    note = `Exempt — transaction below ₦${new Intl.NumberFormat('en-NG').format(rule.exemptBelow)}.`;
  } else {
    duty = amount * (rule.rate || 0);
  }

  return {
    type: 'Stamp duty',
    period: 'per instrument',
    breakdown: [
      { line: rule.flat ? `${rule.label} — flat ₦${rule.flat.toLocaleString()}` : `${rule.label} — ${((rule.rate || 0) * 100).toLocaleString()}% of value`, value: duty },
    ],
    totalTax: duty,
    note: note || 'Duty is payable within 30 days of executing the instrument.',
  };
}

// ── Capital gains tax (2026) ──────────────────────────────────────────────────
// Individuals pay the same progressive rates as PAYE, with the first ₦50M of
// gains exempt. Companies pay 30% (small companies 0%).
export const CGT_INDIVIDUAL_EXEMPTION = 50_000_000;

export function calcCGT({ gains = 0, taxpayer = 'individual', isSmallCompany = false } = {}) {
  const amount = Math.max(gains, 0);

  if (taxpayer === 'company') {
    const rate = isSmallCompany ? 0 : 0.3;
    const tax = amount * rate;
    return {
      type: 'Capital gains tax',
      period: 'per disposal',
      totalTax: tax,
      taxableGain: amount,
      note: isSmallCompany
        ? 'Small companies are exempt from capital gains tax (0%).'
        : 'Companies pay 30% on chargeable gains.',
    };
  }

  const chargeable = Math.max(amount - CGT_INDIVIDUAL_EXEMPTION, 0);
  const { tax, breakdown } = applyBrackets(chargeable);
  return {
    type: 'Capital gains tax',
    period: 'per disposal',
    totalTax: tax,
    taxableGain: chargeable,
    breakdown,
    note: 'Individuals are taxed at the progressive PAYE rates, with the first ₦50,000,000 of gains exempt.',
  };
}

// ── Formatting helpers ────────────────────────────────────────────────────────
export function formatNaira(value) {
  return naira(value);
}

export function formatNairaWords(value) {
  const { words } = toWords(value);
  return words;
}

export function capitalize(str = '') {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default {
  calcPAYE,
  calcTakeHome,
  calcPension,
  calcNHF,
  calcCIT,
  calcDevelopmentLevy,
  calcVAT,
  calcDigitalVAT,
  calcWHT,
  calcStampDuty,
  calcCGT,
  PAYE_BRACKETS,
  WHT_RATES,
  STAMP_DUTY_RATES,
  DEFAULT_VAT_RATE,
  formatNaira,
};