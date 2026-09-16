import { useMemo } from 'react';
import {
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
  WHT_RATES,
  STAMP_DUTY_RATES,
  formatNaira,
  PENSION_DEFAULT_RATE,
  PENSION_EMPLOYER_RATE,
  NHF_RATE,
} from '../lib/taxEstimator';

const fmt = (v) => formatNaira(v);

const nairaNum = (v) => `₦${new Intl.NumberFormat('en-NG').format(Math.round(v))}`;

export function useTaxEstimator(inputs) {
  return useMemo(() => {
    const {
      taxType,
      // PAYE / take-home
      monthlySalary,
      pension,
      nhf,
      basicSalary,
      annualRent,
      lifeAssurance,
      // CIT / dev levy
      turnover,
      fixedAssets,
      profit,
      isProfessional,
      // VAT / digital VAT
      sales,
      inputPurchases,
      digitalTurnover,
      // WHT
      whtType,
      whtAmount,
      whtHasTin,
      // stamp duty
      stampType,
      stampValue,
      // CGT
      cgtGain,
      cgtTaxpayer,
      cgtSmallCompany,
    } = inputs;

    try {
      if (taxType === 'PAYE') {
        const r = calcPAYE({
          monthlySalary,
          pension,
          nhf,
          basicSalary,
          annualRent,
          lifeAssurance,
        });
        return {
          result: {
            period: 'annual',
            total: fmt(r.totalTax),
            rows: [
              { line: 'Gross annual income', value: nairaNum(r.gross), negative: true },
              ...r.reliefs.map((rel) => ({
                line: `− ${rel.line}`,
                value: fmt(rel.value),
                negative: true,
              })),
              { line: 'Chargeable income', value: nairaNum(r.chargeableIncome) },
              ...r.breakdown.map((b) => ({ line: b.line, value: fmt(b.value) })),
              { line: 'Total annual PAYE', value: fmt(r.totalTax) },
            ],
            takeHome: fmt(r.monthlyTakeHome),
            note: 'Deductions shown follow the Nigeria Tax Act 2025 (employee pension 8%, NHF 2.5%, rent relief capped at ₦500,000, life assurance capped at ₦100,000).',
          },
          error: null,
        };
      }

      if (taxType === 'TAKEHOME') {
        const r = calcTakeHome({ monthlySalary, pension, nhf, basicSalary });
        return {
          result: {
            period: 'monthly',
            total: nairaNum(r.monthlyTakeHome),
            rows: [
              { line: 'Gross monthly income', value: fmt(r.gross / 12), negative: true },
              ...r.reliefs
                .filter((rel) => rel.cash)
                .map((rel) => ({ line: `− ${rel.line}`, value: fmt(rel.value / 12), negative: true })),
              { line: 'Monthly PAYE', value: fmt(r.monthlyTax), negative: true },
              { line: 'Net take-home pay', value: fmt(r.monthlyTakeHome) },
              { line: "Employer pension (10%, not deducted)", value: fmt(r.employerPension / 12), negative: true },
            ],
            takeHome: fmt(r.monthlyTakeHome),
            note: `Take-home combines PAYE with ${nhf ? 'NHF (2.5%) and ' : ''}the 8% employee pension contribution. The 10% employer pension is an extra cost to the employer, not a deduction from your pay.`,
          },
          error: null,
        };
      }

      if (taxType === 'PENSION') {
        const r = calcPension({ monthlySalary });
        return {
          result: {
            period: 'monthly',
            total: fmt(r.monthlyTotal),
            rows: [
              { line: `Employee contribution (${PENSION_DEFAULT_RATE * 100}%)`, value: fmt(r.monthlyEmployee) },
              { line: `Employer contribution (${PENSION_EMPLOYER_RATE * 100}%)`, value: fmt(r.monthlyEmployer) },
              { line: 'Total monthly contribution', value: fmt(r.monthlyTotal) },
              { line: 'Total annual contribution', value: fmt(r.annualTotal) },
            ],
            note: 'Pension contributions are calculated on gross monthly pay as required by Nigerian pension law.',
          },
          error: null,
        };
      }

      if (taxType === 'NHF') {
        const r = calcNHF({ basicSalary });
        return {
          result: {
            period: 'monthly',
            total: fmt(r.monthly),
            rows: [
              { line: `NHF contribution (${NHF_RATE * 100}% of basic salary)`, value: fmt(r.monthly) },
              { line: 'Annual equivalent', value: fmt(r.annual) },
            ],
            note: 'NHF of 2.5% applies on basic salary for employees earning above the minimum wage threshold.',
          },
          error: null,
        };
      }

      if (taxType === 'CIT') {
        if (turnover <= 0) return { result: null, error: null };
        const r = calcCIT({ annualTurnover: turnover, fixedAssets, annualProfit: profit, isProfessional });
        return {
          result: {
            period: 'annual',
            total: fmt(r.totalTax),
            rows: [
              { line: 'Company classification', value: r.tierLabel },
              { line: 'Assessable profit', value: fmt(r.assessableProfit) },
              ...r.breakdown.map((b) => ({ line: b.line, value: fmt(b.value) })),
            ],
            note: r.note,
          },
          error: null,
        };
      }

      if (taxType === 'DEVLEVY') {
        const r = calcDevelopmentLevy({ annualProfit: profit });
        return {
          result: {
            period: 'annual',
            total: fmt(r.totalTax),
            rows: [
              { line: 'Assessable profit', value: fmt(r.assessableProfit) },
              { line: `Development levy (4% of assessable profit)`, value: fmt(r.totalTax) },
            ],
            note: 'The development levy applies to non-small companies in addition to CIT. Small companies are exempt.',
          },
          error: null,
        };
      }

      if (taxType === 'VAT') {
        if (sales <= 0) return { result: null, error: null };
        const r = calcVAT({ annualSales: sales, annualInputPurchases: inputPurchases });
        return {
          result: {
            period: 'annual',
            total: fmt(r.totalTax),
            rows: r.breakdown.map((b) => ({
              line: b.line,
              value: fmt(b.value < 0 ? Math.abs(b.value) : b.value),
              negative: b.value < 0,
            })),
            payable: r.totalTax >= 0 ? fmt(r.totalTax) : null,
            carryOver: r.totalTax < 0 ? fmt(Math.abs(r.totalTax)) : null,
            note: r.note,
          },
          error: null,
        };
      }

      if (taxType === 'DIGITALVAT') {
        const r = calcDigitalVAT({ annualTurnover: digitalTurnover });
        return {
          result: {
            period: 'annual',
            total: fmt(r.totalTax),
            rows: [{ line: 'Taxable digital turnover (no threshold)', value: fmt(digitalTurnover) }],
            payable: fmt(r.totalTax),
            note: r.note,
          },
          error: null,
        };
      }

      if (taxType === 'WHT') {
        if (whtAmount <= 0) return { result: null, error: null, rateOptions: WHT_RATES };
        const r = calcWHT({ paymentType: whtType, amount: whtAmount, hasTin: whtHasTin });
        return {
          result: {
            period: 'per payment',
            total: fmt(r.totalTax),
            rows: [
              ...r.breakdown.map((b) => ({ line: b.line, value: fmt(b.value) })),
              { line: 'Net payment to vendor', value: fmt(r.netPayment) },
            ],
            payable: fmt(r.netPayment),
            note: r.note,
          },
          error: null,
          rateOptions: WHT_RATES,
        };
      }

      if (taxType === 'STAMP') {
        const r = calcStampDuty({ instrumentType: stampType, value: stampValue });
        return {
          result: {
            period: 'per instrument',
            total: fmt(r.totalTax),
            rows: r.breakdown.map((b) => ({ line: b.line, value: fmt(b.value) })),
            note: r.note,
          },
          error: null,
          stampOptions: STAMP_DUTY_RATES,
        };
      }

      if (taxType === 'CGT') {
        const r = calcCGT({ gains: cgtGain, taxpayer: cgtTaxpayer, isSmallCompany: cgtSmallCompany });
        const hasExemption = cgtTaxpayer === 'individual' && cgtGain > 0;
        return {
          result: {
            period: 'per disposal',
            total: fmt(r.totalTax),
            rows: [
              ...(hasExemption
                ? [
                    { line: 'Gross gains', value: nairaNum(cgtGain), negative: true },
                    { line: 'Less: first-time exemption (₦50M)', value: fmt(Math.min(cgtGain, 50000000)), negative: true },
                  ]
                : []),
              { line: 'Chargeable gains', value: nairaNum(r.taxableGain) },
              ...(r.breakdown ? r.breakdown.map((b) => ({ line: b.line, value: fmt(b.value) })) : []),
            ],
            note: r.note,
          },
          error: null,
        };
      }

      return { result: null, error: null, rateOptions: WHT_RATES, stampOptions: STAMP_DUTY_RATES };
    } catch (e) {
      return { result: null, error: 'Could not compute this estimate. Please review your inputs.' };
    }
  }, [inputs]);
}

export default useTaxEstimator;