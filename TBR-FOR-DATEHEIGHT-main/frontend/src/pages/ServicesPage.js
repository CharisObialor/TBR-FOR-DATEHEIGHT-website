import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight, ChevronDown, Calculator, FileBarChart, Users,
  Receipt, Building2, FileText, CheckCircle
} from 'lucide-react';

const categories = [
  {
    id: 'accounting',
    label: 'Accounting & Bookkeeping Services',
    icon: Calculator,
    color: 'bg-blue-100 text-blue-700',
    services: [
      {
        title: 'Bookkeeping',
        description: 'Comprehensive recording and organization of daily financial transactions, ensuring accurate ledgers and up-to-date financial records for informed business decisions.'
      },
      {
        title: 'Bank Reconciliation',
        description: 'Matching your internal financial records against bank statements to identify discrepancies, prevent errors, and maintain accurate cash position reporting.'
      },
      {
        title: 'Accounts Payable Management',
        description: 'End-to-end management of vendor invoices, payment scheduling, and supplier relationship tracking to optimize cash flow and avoid late payment penalties.'
      },
      {
        title: 'Accounts Receivable Management',
        description: 'Systematic tracking of customer invoices, payment follow-ups, and aging analysis to accelerate cash collection and reduce outstanding receivables.'
      },
      {
        title: 'Inventory Reconciliation',
        description: 'Periodic verification of physical inventory against recorded stock levels, identifying variances and ensuring accurate asset valuation on your balance sheet.'
      },
      {
        title: 'General Ledger Review',
        description: 'Thorough examination of general ledger entries to verify accuracy, completeness, and proper categorization of all financial transactions.'
      },
      {
        title: 'Trial Balance Preparation',
        description: 'Preparation of a complete trial balance summarizing all ledger accounts, forming the foundation for accurate financial statement generation.'
      },
    ],
  },
  {
    id: 'financial-statements',
    label: 'Financial Statement Preparation',
    icon: FileBarChart,
    color: 'bg-emerald-100 text-emerald-700',
    services: [
      {
        title: 'Annual Financial Statements',
        description: 'Preparation of statutory financial statements including income statement, balance sheet, cash flow statement, and notes to accounts in compliance with applicable accounting standards.'
      },
      {
        title: 'Management Accounts',
        description: 'Customized monthly or quarterly financial reports providing management with actionable insights into business performance, margins, and operational efficiency.'
      },
      {
        title: 'Financial Statement Review',
        description: 'Independent review of prepared financial statements to ensure consistency, accuracy, and adherence to regulatory and reporting requirements.'
      },
    ],
  },
  {
    id: 'payroll',
    label: 'Payroll Services',
    icon: Users,
    color: 'bg-purple-100 text-purple-700',
    services: [
      {
        title: 'Payroll Processing',
        description: 'Complete payroll management including salary computation, statutory deductions, overtime calculations, and net pay disbursement for organizations of all sizes.'
      },
      {
        title: 'Pension Schedule',
        description: 'Preparation and management of pension contribution schedules ensuring compliance with the Pension Reform Act and timely remittances to designated Pension Fund Administrators.'
      },
      {
        title: 'PAYE Schedule',
        description: 'Computation and scheduling of Pay-As-You-Earn taxes, ensuring accurate deductions per staff and timely remittance to the relevant tax authorities.'
      },
      {
        title: 'NHF Schedule',
        description: 'Management of National Housing Fund contributions, including accurate calculation of 2.5% deductions and compliance with NHF regulations.'
      },
      {
        title: 'NSITF Schedule',
        description: 'Preparation of Nigeria Social Insurance Trust Fund schedules, ensuring proper employee registration and contribution remittance as required by law.'
      },
      {
        title: 'Payroll Reports',
        description: 'Generation of detailed payroll analytics including cost centers analysis, department summaries, and year-to-date earning statements for strategic planning.'
      },
    ],
  },
  {
    id: 'tax',
    label: 'Tax Compliance Services',
    icon: Receipt,
    color: 'bg-amber-100 text-amber-700',
    services: [
      {
        title: 'Company Income Tax (CIT)',
        description: 'Preparation and filing of annual company income tax returns, ensuring compliance with the Companies Income Tax Act while optimizing legitimate tax positions.'
      },
      {
        title: 'VAT Filing',
        description: 'Monthly or quarterly Value Added Tax computation, remittance, and filing with the Federal Inland Revenue Service, including input/output VAT reconciliation.'
      },
      {
        title: 'Withholding Tax Filing',
        description: 'Management of withholding tax deductions, credit notes generation, and quarterly filings to ensure compliance with WHT regulations.'
      },
      {
        title: 'PAYE Filing',
        description: 'Monthly filing of Pay-As-You-Earn tax returns with the relevant state internal revenue service, including employee-by-employee schedules.'
      },
      {
        title: 'Capital Gains Tax',
        description: 'Advisory and filing services for capital gains tax arising from the disposal of assets, ensuring compliance and application of available reliefs and exemptions.'
      },
      {
        title: 'Stamp Duty',
        description: 'Processing and payment of stamp duties on applicable instruments and documents as required by the Stamp Duties Act.'
      },
      {
        title: 'Annual Tax Health Check',
        description: 'Comprehensive review of your tax compliance status, identifying exposure areas, unclaimed reliefs, and recommending strategies for tax efficiency.'
      },
      {
        title: 'Tax Clearance Certificate Processing',
        description: 'End-to-end processing of Tax Clearance Certificates, including reconciliation of tax payments and liaison with tax authorities for timely issuance.'
      },
    ],
  },
  {
    id: 'registration',
    label: 'Company Registration & Regulatory Services',
    icon: Building2,
    color: 'bg-rose-100 text-rose-700',
    services: [
      {
        title: 'Company Registration',
        description: 'Full incorporation services including name reservation, preparation of incorporation documents, registration with the Corporate Affairs Commission, and issuance of certificate of incorporation.'
      },
      {
        title: 'Business Name Registration',
        description: 'Registration of business names with the Corporate Affairs Commission, providing legal recognition and protection for your trade name.'
      },
      {
        title: 'Annual Returns Filing',
        description: 'Preparation and filing of annual returns with the Corporate Affairs Commission, maintaining your company\'s good standing and statutory compliance.'
      },
      {
        title: 'PAYE Registration',
        description: 'Registration of your business with the relevant state internal revenue service for Pay-As-You-Earn tax compliance.'
      },
      {
        title: 'SCUML Registration',
        description: 'Registration with the Special Control Unit against Money Laundering, ensuring compliance with anti-money laundering regulations for designated non-financial businesses.'
      },
      {
        title: 'CAC Document Recovery',
        description: 'Assistance with recovery, update, and certification of corporate documents from the Corporate Affairs Commission, including status reports and certified true copies.'
      },
    ],
  },
];

const ServicesPage = () => {
  const [expanded, setExpanded] = useState(() => {
    const init = {};
    categories.forEach((c) => { init[c.id] = true; });
    return init;
  });

  const toggle = (id) => setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div className="bg-white">
      <section className="pt-32 pb-16 bg-slate-950 text-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-4">Our Services</p>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tighter leading-none mb-4 sm:mb-6">
              Comprehensive Business Solutions
            </h1>
            <p className="text-base sm:text-xl text-slate-300 max-w-3xl leading-relaxed">
              From tax compliance to corporate registration, we provide end-to-end solutions that empower businesses to focus on growth while staying compliant.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          {categories.map((category) => {
            const Icon = category.icon;
            const isOpen = expanded[category.id];
            return (
              <div key={category.id} className="mb-12 last:mb-0">
                <button
                  onClick={() => toggle(category.id)}
                  className="w-full flex items-center justify-between p-5 bg-slate-50 border border-slate-200 hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 flex items-center justify-center ${category.color}`}>
                      <Icon size={24} />
                    </div>
                    <div className="text-left">
                      <h2 className="text-2xl font-bold text-slate-900">{category.label}</h2>
                      <p className="text-sm text-slate-500">{category.services.length} service{category.services.length !== 1 ? 's' : ''}</p>
                    </div>
                  </div>
                  <ChevronDown
                    size={24}
                    className={`text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                  />
                </button>

                {isOpen && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mt-6">
                    {category.services.map((service, index) => (
                      <motion.div
                        key={service.title}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.03 }}
                      >
                        <a
                          href="https://portal.tbrsolutions.ng/register"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="group block h-full"
                        >
                          <div className="bg-white border border-slate-200 p-6 hover:shadow-lg hover:border-slate-300 transition-all duration-200 h-full flex flex-col">
                            <div className="flex items-start gap-3 mb-3">
                              <CheckCircle size={18} className="text-blue-500 mt-0.5 shrink-0" />
                              <h3 className="text-lg font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">
                                {service.title}
                              </h3>
                            </div>
                            <p className="text-sm text-slate-600 leading-relaxed flex-grow">
                              {service.description}
                            </p>
                            <div className="mt-4 pt-3 border-t border-slate-100">
                              <span className="text-sm font-medium text-blue-600 group-hover:text-blue-700 inline-flex items-center gap-1">
                                Get Started
                                <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                              </span>
                            </div>
                          </div>
                        </a>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <section className="py-24 bg-slate-950 text-white">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-6">Need a Custom Solution?</h2>
          <p className="text-xl text-slate-300 mb-8">Our team can design a tailored compliance strategy for your unique needs.</p>
          <a href="https://portal.tbrsolutions.ng/register" target="_blank" rel="noopener noreferrer">
            <button className="bg-white text-slate-900 hover:bg-slate-100 rounded-sm h-14 px-8 text-base font-semibold inline-flex items-center gap-2">
              Get Started
              <ArrowRight size={20} />
            </button>
          </a>
        </div>
      </section>
    </div>
  );
};

export default ServicesPage;
