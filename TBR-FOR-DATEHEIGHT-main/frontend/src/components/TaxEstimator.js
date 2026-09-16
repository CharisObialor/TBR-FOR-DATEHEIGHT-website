import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Calculator,
  AlertTriangle,
  UserRound,
  Building2,
  ReceiptText,
  Wallet,
  Info,
  Landmark,
  PiggyBank,
  Banknote,
  Home,
  Globe2,
  Scale,
  TrendingUp,
  Stamp,
  Users,
  HandCoins,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useTaxEstimator } from '../hooks/useTaxEstimator';
import { WHT_RATES, STAMP_DUTY_RATES, formatNairaWords } from '../lib/taxEstimator';

const CALCULATORS = [
  { id: 'PAYE', label: 'PAYE', icon: UserRound, desc: 'Personal income tax on employment income' },
  { id: 'TAKEHOME', label: 'Take-home pay', icon: Wallet, desc: 'Net salary after PAYE, pension & NHF' },
  { id: 'PENSION', label: 'Pension', icon: PiggyBank, desc: '8% employee + 10% employer pension' },
  { id: 'NHF', label: 'NHF', icon: Home, desc: '2.5% National Housing Fund on basic salary' },
  { id: 'CIT', label: 'CIT', icon: Building2, desc: 'Company income tax + development levy' },
  { id: 'DEVLEVY', label: 'Dev. levy', icon: Landmark, desc: 'Standalone 4% development levy' },
  { id: 'VAT', label: 'VAT', icon: ReceiptText, desc: 'Value-added tax on taxable supplies' },
  { id: 'DIGITALVAT', label: 'Digital VAT', icon: Globe2, desc: 'Non-resident digital services VAT' },
  { id: 'WHT', label: 'WHT', icon: HandCoins, desc: 'Withholding tax on payments' },
  { id: 'STAMP', label: 'Stamp duty', icon: Stamp, desc: 'Flat and ad valorem instrument duties' },
  { id: 'CGT', label: 'Capital gains', icon: TrendingUp, desc: 'Tax on chargeable gains on disposal' },
];

const DISCLAIMER_BEFORE =
  'This estimate is for informational purposes only and should not be used to compute, file, or remit taxes. Rates and reliefs change with law and your specific circumstances. ';
const DISCLAIMER_LINK = 'Consult a qualified tax professional';
const DISCLAIMER_AFTER = ' for advice you can rely on.';

const Field = ({ label, children, hint }) => (
  <label className="block">
    <span className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">{label}</span>
    {children}
    {hint && <span className="block text-[11px] text-slate-400 mt-1.5">{hint}</span>}
  </label>
);

const inputClass =
  'w-full h-12 rounded-sm border border-slate-200 bg-white px-4 text-base text-slate-900 shadow-sm outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-100';

const selectClass = `${inputClass} cursor-pointer appearance-none bg-no-repeat bg-[right_0.75rem_center] pr-10`;
const selectChevron =
  'bg-[url("data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20width%3D%2716%27%20height%3D%2716%27%20fill%3D%27%2364748b%27%20viewBox%3D%270%200%2016%2016%27%3E%3Cpath%20d%3D%27M8%2011%204%207h8l-4%204z%27%2F%3E%3C%2Fsvg%3E")]';

const NumberInput = ({ value, onChange, placeholder = '0', suffix, showWords = true }) => {
  const words = showWords && Number(value) > 0 ? formatNairaWords(Number(value)) : '';
  return (
    <div>
      <div className="relative">
        <input
          type="number"
          min="0"
          value={value}
          onChange={(e) => onChange(e.target.value === '' ? '' : Number(e.target.value))}
          placeholder={placeholder}
          className={cn(inputClass, suffix && 'pr-16')}
          inputMode="numeric"
        />
        {suffix && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-medium text-slate-400 pointer-events-none">
            {suffix}
          </span>
        )}
      </div>
      {words && (
        <span className="block mt-1.5 text-xs font-medium text-blue-600">
          {words}
        </span>
      )}
    </div>
  );
};

const Toggle = ({ checked, onChange, label, hint }) => (
  <div className="flex items-center justify-between gap-4">
    <div>
      <span className="block text-sm font-medium text-slate-700">{label}</span>
      {hint && <span className="block text-[11px] text-slate-400 mt-0.5">{hint}</span>}
    </div>
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        'relative h-6 w-11 shrink-0 rounded-full transition-colors',
        checked ? 'bg-blue-600' : 'bg-slate-300'
      )}
    >
      <span
        className={cn(
          'absolute top-[2px] h-5 w-5 rounded-full bg-white shadow transition-all duration-200',
          checked ? 'left-[22px]' : 'left-[2px]'
        )}
      />
    </button>
  </div>
);

const SegmentedControl = ({ options, value, onChange }) => (
  <div className="grid grid-cols-2 gap-1 rounded-sm bg-slate-100 p-1">
    {options.map((opt) => (
      <button
        key={opt.value}
        type="button"
        onClick={() => onChange(opt.value)}
        className={cn(
          'h-10 rounded-sm text-sm font-semibold transition-colors',
          value === opt.value
            ? 'bg-white text-slate-900 shadow-sm'
            : 'text-slate-500 hover:text-slate-700'
        )}
        aria-pressed={value === opt.value}
      >
        {opt.label}
      </button>
    ))}
  </div>
);

function ResultRow({ line, value, negative }) {
  return (
    <div className="flex items-center justify-between py-2 text-sm">
      <span className="text-slate-600 pr-4">{line}</span>
      <span className={cn('font-semibold tabular-nums whitespace-nowrap', negative ? 'text-slate-500' : 'text-slate-900')}>
        {negative ? `− ${value}` : value}
      </span>
    </div>
  );
}

const TaxEstimator = () => {
  const [taxType, setTaxType] = useState('PAYE');

  const [monthlySalary, setMonthlySalary] = useState('');
  const [pension, setPension] = useState(true);
  const [nhf, setNhh] = useState(false);
  const [basicSalary, setBasicSalary] = useState('');
  const [annualRent, setAnnualRent] = useState('');
  const [lifeAssurance, setLifeAssurance] = useState('');

  const [turnover, setTurnover] = useState('');
  const [fixedAssets, setFixedAssets] = useState('');
  const [profit, setProfit] = useState('');
  const [isProfessional, setIsProfessional] = useState(false);

  const [sales, setSales] = useState('');
  const [inputs, setInputs] = useState('');
  const [digitalTurnover, setDigitalTurnover] = useState('');

  const [whtType, setWhtType] = useState('professional');
  const [whtAmount, setWhtAmount] = useState('');
  const [whtHasTin, setWhtHasTin] = useState(true);

  const [stampType, setStampType] = useState('conveyance');
  const [stampValue, setStampValue] = useState('');

  const [cgtGain, setCgtGain] = useState('');
  const [cgtTaxpayer, setCgtTaxpayer] = useState('individual');
  const [cgtSmallCompany, setCgtSmallCompany] = useState(false);

  const { result, error, rateOptions } = useTaxEstimator({
    taxType,
    monthlySalary: monthlySalary === '' ? 0 : monthlySalary,
    pension,
    nhf,
    basicSalary: basicSalary === '' ? 0 : basicSalary,
    annualRent: annualRent === '' ? 0 : annualRent,
    lifeAssurance: lifeAssurance === '' ? 0 : lifeAssurance,
    turnover: turnover === '' ? 0 : turnover,
    fixedAssets: fixedAssets === '' ? 0 : fixedAssets,
    profit: profit === '' ? 0 : profit,
    isProfessional,
    sales: sales === '' ? 0 : sales,
    inputPurchases: inputs === '' ? 0 : inputs,
    digitalTurnover: digitalTurnover === '' ? 0 : digitalTurnover,
    whtType,
    whtAmount: whtAmount === '' ? 0 : whtAmount,
    whtHasTin,
    stampType,
    stampValue: stampValue === '' ? 0 : stampValue,
    cgtGain: cgtGain === '' ? 0 : cgtGain,
    cgtTaxpayer,
    cgtSmallCompany,
  });

  const hasInput = useMemo(() => {
    switch (taxType) {
      case 'PAYE':
        return monthlySalary > 0;
      case 'TAKEHOME':
        return monthlySalary > 0;
      case 'PENSION':
        return monthlySalary > 0;
      case 'NHF':
        return basicSalary > 0;
      case 'CIT':
        return turnover > 0;
      case 'DEVLEVY':
        return profit > 0;
      case 'VAT':
        return sales > 0;
      case 'DIGITALVAT':
        return digitalTurnover > 0;
      case 'WHT':
        return whtAmount > 0;
      case 'STAMP':
        return stampValue > 0;
      case 'CGT':
        return cgtGain > 0;
      default:
        return false;
    }
  }, [taxType, monthlySalary, basicSalary, turnover, profit, sales, digitalTurnover, whtAmount, stampValue, cgtGain]);

  const activeCalc = CALCULATORS.find((c) => c.id === taxType);

  return (
    <section id="tax-estimator" className="py-24 sm:py-32 bg-slate-50 border-y border-slate-200" data-testid="tax-estimator">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500 mb-4">
            Tax Estimator
          </p>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-slate-900 mb-6">
            Get a sense of your tax obligations in seconds
          </h2>
          <p className="text-base text-slate-600 leading-relaxed">
            Estimate PAYE, take-home pay, pension, NHF, Company Income Tax, VAT, Withholding Tax,
            stamp duty and more — every calculator updated for the Nigeria Tax Act 2025 (effective
            January 2026). Free, no sign-up, no data saved.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-10 items-start">
          {/* Inputs */}
          <div className="lg:col-span-3 bg-white border border-slate-200 p-6 sm:p-8">
            <div className="flex flex-wrap gap-2 mb-8">
              {CALCULATORS.map((t) => {
                const Icon = t.icon;
                const active = taxType === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setTaxType(t.id)}
                    title={t.desc}
                    className={cn(
                      'flex items-center gap-1.5 rounded-sm px-3 py-2 text-sm font-semibold transition-colors border',
                      active
                        ? 'bg-slate-900 text-white border-slate-900'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    )}
                    aria-pressed={active}
                  >
                    <Icon size={16} className={active ? 'text-blue-400' : 'text-slate-400'} />
                    {t.label}
                  </button>
                );
              })}
            </div>

            <div className="mb-6 flex items-start gap-2 text-xs text-slate-500">
              <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
              <span>
                {activeCalc ? activeCalc.desc : ''}
              </span>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={taxType}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                {(taxType === 'PAYE' || taxType === 'TAKEHOME') && (
                  <>
                    <Field label="Monthly employment income (₦)">
                      <NumberInput value={monthlySalary} onChange={setMonthlySalary} />
                    </Field>
                    <Toggle checked={pension} onChange={setPension} label="Employee pension contribution (8%)" />
                    <Toggle checked={nhf} onChange={setNhh} label="National Housing Fund (2.5% of basic salary)" />
                    {nhf && (
                      <Field label="Basic monthly salary (₦)" hint="NHF is calculated on basic salary, not gross pay.">
                        <NumberInput value={basicSalary} onChange={setBasicSalary} />
                      </Field>
                    )}
                    {taxType === 'PAYE' && (
                      <>
                        <Field label="Annual rent paid (₦)" hint="Optional — rent relief is 20% of annual rent, capped at ₦500,000 (documented).">
                          <NumberInput value={annualRent} onChange={setAnnualRent} />
                        </Field>
                        <Field label="Life assurance premium (₦)" hint="Optional — deductible up to ₦100,000 per annum.">
                          <NumberInput value={lifeAssurance} onChange={setLifeAssurance} />
                        </Field>
                      </>
                    )}
                  </>
                )}

                {taxType === 'PENSION' && (
                  <>
                    <Field label="Gross monthly pay (₦)">
                      <NumberInput value={monthlySalary} onChange={setMonthlySalary} />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      8% employee plus 10% employer, both on gross monthly pay.
                    </p>
                  </>
                )}

                {taxType === 'NHF' && (
                  <>
                    <Field label="Basic monthly salary (₦)" hint="NHF applies to employees earning above the minimum wage threshold.">
                      <NumberInput value={basicSalary} onChange={setBasicSalary} />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      2.5% of basic monthly salary.
                    </p>
                  </>
                )}

                {taxType === 'CIT' && (
                  <>
                    <Field label="Annual turnover (₦)">
                      <NumberInput value={turnover} onChange={setTurnover} />
                    </Field>
                    <Field label="Fixed assets (₦)" hint="Required to check the small-company threshold (< ₦250M).">
                      <NumberInput value={fixedAssets} onChange={setFixedAssets} />
                    </Field>
                    <Field label="Assessable profit (₦) — optional" hint="Leave blank to estimate profit at 40% of turnover.">
                      <NumberInput value={profit} onChange={setProfit} placeholder="Auto-estimated" />
                    </Field>
                    <Toggle
                      checked={isProfessional}
                      onChange={setIsProfessional}
                      label="Professional services firm"
                      hint="Legal, accounting, medical and consulting firms never qualify as small."
                    />
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      Small companies (turnover ≤ ₦100M and assets under ₦250M, not professional) pay 0%.
                      All other companies pay 30% CIT plus a 4% development levy.
                    </p>
                  </>
                )}

                {taxType === 'DEVLEVY' && (
                  <>
                    <Field label="Assessable profit (₦)">
                      <NumberInput value={profit} onChange={setProfit} />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      Standalone 4% development levy for medium and large companies.
                    </p>
                  </>
                )}

                {taxType === 'VAT' && (
                  <>
                    <Field label="Annual taxable sales — exclusive of VAT (₦)">
                      <NumberInput value={sales} onChange={setSales} />
                    </Field>
                    <Field label="Qualifying input purchases (₦) — optional" hint="Input VAT on these purchases is credited against output VAT.">
                      <NumberInput value={inputs} onChange={setInputs} placeholder="0" />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      Standard rate of 7.5%. Excess input VAT carries forward or is claimed as a refund.
                    </p>
                  </>
                )}

                {taxType === 'DIGITALVAT' && (
                  <>
                    <Field label="Annual turnover from Nigerian users — exclusive of VAT (₦)">
                      <NumberInput value={digitalTurnover} onChange={setDigitalTurnover} />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      Foreign SaaS, streaming and ad platforms serving Nigerian users owe 7.5% VAT
                      with no turnover threshold (2026 rule).
                    </p>
                  </>
                )}

                {taxType === 'WHT' && (
                  <>
                    <Field label="Payment type">
                      <select
                        value={whtType}
                        onChange={(e) => setWhtType(e.target.value)}
                        className={`${selectClass} ${selectChevron}`}
                      >
                        {(rateOptions || WHT_RATES).map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.label} ({option.rate * 100}%)
                          </option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Payment amount (₦)">
                      <NumberInput value={whtAmount} onChange={setWhtAmount} />
                    </Field>
                    <Toggle
                      checked={whtHasTin}
                      onChange={setWhtHasTin}
                      label="Vendor has a valid TIN"
                      hint="Without a TIN, WHT is doubled (capped at 20%). Transactions under ₦2M with a TIN are exempt."
                    />
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      WHT is withheld from the payment and remitted to NRS by the 21st of the
                      following month.
                    </p>
                  </>
                )}

                {taxType === 'STAMP' && (
                  <>
                    <Field label="Instrument type">
                      <select
                        value={stampType}
                        onChange={(e) => setStampType(e.target.value)}
                        className={`${selectClass} ${selectChevron}`}
                      >
                        {STAMP_DUTY_RATES.map((option) => (
                          <option key={option.id} value={option.id}>
                            {option.label}
                            {option.flat
                              ? ` — ₦${option.flat.toLocaleString()}`
                              : option.rate
                                ? ` — ${(option.rate * 100).toLocaleString()}%`
                                : ''}
                          </option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Transaction value (₦)" hint="Not required for flat-rate instruments.">
                      <NumberInput value={stampValue} onChange={setStampValue} />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      Ad valorem and flat rates per the Nigeria Tax Act 2025. Instruments must be
                      stamped within 30 days of execution.
                    </p>
                  </>
                )}

                {taxType === 'CGT' && (
                  <>
                    <Field label="Taxpayer type">
                      <SegmentedControl
                        options={[
                          { label: 'Individual', value: 'individual' },
                          { label: 'Company', value: 'company' },
                        ]}
                        value={cgtTaxpayer}
                        onChange={setCgtTaxpayer}
                      />
                    </Field>
                    {cgtTaxpayer === 'company' && (
                      <Toggle
                        checked={cgtSmallCompany}
                        onChange={setCgtSmallCompany}
                        label="Small company"
                        hint="Small companies are exempt from capital gains tax (0%)."
                      />
                    )}
                    <Field label="Chargeable gains (₦)">
                      <NumberInput value={cgtGain} onChange={setCgtGain} />
                    </Field>
                    <p className="text-xs text-slate-500 flex items-start gap-1.5">
                      <Info size={14} className="mt-0.5 shrink-0 text-slate-400" />
                      Individuals pay the progressive PAYE rates up to 25%, with the first
                      ₦50,000,000 of gains exempt. Companies pay 30%.
                    </p>
                  </>
                )}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Results */}
          <div className="lg:col-span-2 lg:sticky lg:top-40">
            <div className="bg-slate-900 text-white p-6 sm:p-8" data-testid="tax-estimator-result">
              <div className="flex items-center gap-2 mb-4">
                <Landmark size={18} className="text-blue-400" />
                <span className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  {activeCalc
                    ? `${activeCalc.label} estimate`
                    : 'Tax estimate'}
                </span>
              </div>

              {!hasInput && !error && (
                <p className="text-sm text-slate-400 leading-relaxed">
                  Enter your figures on the left and your estimate will appear here instantly.
                </p>
              )}

              {hasInput && !error && result && (
                <>
                  <div className="border-b border-slate-800 pb-4 mb-4">
                    <div className="text-xs text-slate-400 mb-1">{result.period} estimate</div>
                    <div className="text-4xl font-bold tabular-nums text-white">
                      {result.total}
                    </div>
                  </div>
                  <div className="space-y-1 divide-y divide-slate-800/60">
                    {result.rows.map((row, i) => (
                      <ResultRow key={i} {...row} />
                    ))}
                    {result.payable && (
                      <div className="flex items-center justify-between pt-3 pb-1 text-sm">
                        <span className="text-slate-400">Net payable</span>
                        <span className="font-semibold tabular-nums text-blue-400">{result.payable}</span>
                      </div>
                    )}
                    {result.carryOver && (
                      <div className="flex items-center justify-between pt-3 pb-1 text-sm">
                        <span className="text-slate-400">Credit carried forward / refund</span>
                        <span className="font-semibold tabular-nums text-sky-400">{result.carryOver}</span>
                      </div>
                    )}
                    {result.takeHome && (
                      <div className="flex items-center justify-between pt-3 pb-1 text-sm">
                        <span className="text-slate-400">Monthly take-home</span>
                        <span className="font-semibold tabular-nums text-emerald-400">{result.takeHome}</span>
                      </div>
                    )}
                  </div>
                  {result.note && (
                    <p className="mt-4 text-[11px] text-slate-500 leading-relaxed">{result.note}</p>
                  )}
                </>
              )}

              {error && (
                <p className="text-sm text-amber-400 leading-relaxed">{error}</p>
              )}

              <div
                className="mt-6 pt-4 border-t border-slate-800 flex items-start gap-2"
                data-testid="tax-estimator-disclaimer"
              >
                <AlertTriangle size={16} className="shrink-0 mt-0.5 text-amber-400" />
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {DISCLAIMER_BEFORE}
                  <Link
                    to="/contact"
                    data-testid="tax-estimator-consult-link"
                    className="font-semibold text-amber-300 underline underline-offset-2 transition-colors hover:text-amber-200"
                  >
                    {DISCLAIMER_LINK}
                  </Link>
                  {DISCLAIMER_AFTER}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TaxEstimator;