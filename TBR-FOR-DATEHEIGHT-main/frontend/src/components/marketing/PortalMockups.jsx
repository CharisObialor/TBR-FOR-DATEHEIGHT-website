import React from 'react';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  FileText,
  Landmark,
  FolderLock,
  MessagesSquare,
  Search,
  Bell,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ShieldCheck,
  Building2,
  ReceiptText,
  Calculator,
  Users,
  BrainCircuit,
  Sparkles,
  BadgeCheck,
  Download,
  ChevronRight,
} from 'lucide-react';
import { cn } from '../../lib/utils';

/* ── Shared bits ─────────────────────────────────────────────── */

const navItems = [
  { key: 'overview', icon: LayoutDashboard, label: 'Overview' },
  { key: 'filings', icon: FileText, label: 'Filings' },
  { key: 'documents', icon: FolderLock, label: 'Documents' },
  { key: 'payments', icon: Landmark, label: 'Payments' },
  { key: 'advisory', icon: MessagesSquare, label: 'Advisory' },
];

const AppShell = ({ title, subtitle, actions, children, crumb = 'Overview', activeNav = 'overview', onNavigate }) => (
  <div className="flex min-h-[420px]">
    {/* Sidebar */}
    <aside className="hidden w-44 shrink-0 border-r border-slate-100 bg-slate-50/70 p-3 sm:block">
      <div className="mb-5 flex items-center gap-2 px-2">
        <span className="flex h-6 w-6 items-center justify-center rounded-md bg-slate-900 text-[11px] font-bold text-white">
          T
        </span>
        <span className="text-xs font-semibold text-slate-800">TBR Portal</span>
      </div>
      <div className="space-y-0.5">
        {navItems.map(({ key, icon: Icon, label }) => {
          const active = key === activeNav;
          const navClass = cn(
            'flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-xs font-medium',
            active ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500',
            onNavigate &&
              'cursor-pointer transition-colors hover:bg-white hover:text-slate-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600'
          );
          if (!onNavigate) {
            return (
              <div key={key} className={navClass}>
                <Icon size={14} className={active ? 'text-blue-600' : 'text-slate-400'} />
                {label}
              </div>
            );
          }
          return (
            <button
              key={key}
              type="button"
              onClick={() => onNavigate(key)}
              aria-current={active ? 'page' : undefined}
              className={navClass}
            >
              <Icon size={14} className={active ? 'text-blue-600' : 'text-slate-400'} />
              {label}
            </button>
          );
        })}
      </div>
      <div className="mt-6 rounded-lg border border-blue-100 bg-blue-50/70 p-3">
        <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-blue-700">
          <Sparkles size={11} /> AI Advisor
        </div>
        <p className="mt-1.5 text-[10px] leading-relaxed text-slate-600">
          VAT return ready to review before the 21st.
        </p>
      </div>
    </aside>

    {/* Main */}
    <div className="flex min-w-0 flex-1 flex-col">
      <header className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3 sm:px-5">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-900">{title}</p>
          {subtitle && <p className="truncate text-[11px] text-slate-400">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1.5 md:flex">
            <Search size={12} className="text-slate-400" />
            <span className="text-[11px] text-slate-400">Search…</span>
          </div>
          <span className="relative flex h-7 w-7 items-center justify-center rounded-md border border-slate-200 text-slate-500">
            <Bell size={13} />
            <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-rose-500" />
          </span>
          {actions}
        </div>
      </header>
      <div className="flex-1 p-4 sm:p-5">{children}</div>
    </div>
  </div>
);

const Kpi = ({ label, value, delta, up = true, icon: Icon, onClick, ariaLabel }) => {
  const Wrapper = onClick ? 'button' : 'div';
  return (
    <Wrapper
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      aria-label={onClick ? ariaLabel || label : undefined}
      className={cn(
        'rounded-lg border border-slate-200 bg-white p-3',
        onClick &&
          'block w-full text-left transition-colors hover:border-slate-300 hover:shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600'
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
          {label}
        </span>
        {Icon && <Icon size={14} className="text-slate-300" />}
      </div>
      <div className="mt-1.5 flex items-end gap-1.5">
        <span className="text-lg font-bold tabular-nums text-slate-900">{value}</span>
        {delta && (
          <span
            className={cn(
              'mb-0.5 inline-flex items-center gap-0.5 text-[10px] font-semibold',
              up ? 'text-emerald-600' : 'text-rose-500'
            )}
          >
            {up ? <ArrowUpRight size={11} /> : <ArrowDownRight size={11} />}
            {delta}
          </span>
        )}
      </div>
    </Wrapper>
  );
};

const StatusPill = ({ status }) => {
  const map = {
    Filed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    Due: 'bg-amber-50 text-amber-700 border-amber-200',
    Overdue: 'bg-rose-50 text-rose-700 border-rose-200',
    Paid: 'bg-blue-50 text-blue-700 border-blue-200',
    Draft: 'bg-slate-100 text-slate-600 border-slate-200',
  };
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold',
        map[status] || map.Draft
      )}
    >
      {status}
    </span>
  );
};

/* ── 1. Hero dashboard ───────────────────────────────────────── */

const months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];
const bars = [42, 58, 49, 71, 63, 88, 76, 95, 84, 69, 91, 99];

const DashboardContent = ({ onNavigate }) => {
  const go = (page) => (onNavigate ? () => onNavigate(page) : undefined);

  return (
    <>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi
          label="Compliance score"
          value="98.4%"
          delta="1.2"
          up
          icon={ShieldCheck}
          onClick={go('overview')}
          ariaLabel="Open compliance overview"
        />
        <Kpi
          label="Open filings"
          value="3"
          delta="2"
          up={false}
          icon={FileText}
          onClick={go('filings')}
          ariaLabel="Open filings"
        />
        <Kpi
          label="Paid year to date"
          value="₦4.2M"
          delta="8.1"
          up
          icon={Landmark}
          onClick={go('payments')}
          ariaLabel="Open payments"
        />
        <Kpi label="Active entities" value="12" delta="1" up icon={Building2} />
      </div>

      <div className="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-5">
        {/* Chart */}
        <div className="rounded-lg border border-slate-200 bg-white p-4 lg:col-span-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-900">Filings completed</p>
              <p className="text-[10px] text-slate-400">Rolling 12 months</p>
            </div>
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
              <span className="h-2 w-2 rounded-full bg-blue-600" />
              {bars.reduce((a, b) => a + b, 0)} filed
            </div>
          </div>
          <div className="mt-4 flex h-28 items-end gap-1.5">
            {bars.map((h, i) => (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                whileInView={{ height: `${h}%` }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, delay: i * 0.04, ease: [0.22, 1, 0.36, 1] }}
                className={cn(
                  'flex-1 rounded-t-sm',
                  i === bars.length - 1 ? 'bg-blue-600' : 'bg-slate-200'
                )}
              />
            ))}
          </div>
          <div className="mt-2 flex justify-between">
            {months.map((m, i) => (
              <span key={i} className="flex-1 text-center text-[9px] text-slate-400">
                {m}
              </span>
            ))}
          </div>
        </div>

        {/* Deadlines */}
        <div className="rounded-lg border border-slate-200 bg-white p-4 lg:col-span-2">
          <p className="text-xs font-semibold text-slate-900">Upcoming deadlines</p>
          <div className="mt-3 space-y-2.5">
            {[
              { name: 'VAT return', date: 'Due in 4 days', status: 'Due', icon: ReceiptText },
              { name: 'PAYE schedule', date: 'Due in 9 days', status: 'Draft', icon: Users },
              { name: 'CIT installment', date: 'Due in 21 days', status: 'Filed', icon: Landmark },
              { name: 'TCC renewal', date: 'Due in 34 days', status: 'Filed', icon: BadgeCheck },
            ].map((row) => {
              const Icon = row.icon;
              const rowContent = (
                <>
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-500">
                    <Icon size={13} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[11px] font-medium text-slate-800">{row.name}</p>
                    <p className="text-[10px] text-slate-400">{row.date}</p>
                  </div>
                  <StatusPill status={row.status} />
                </>
              );
              return onNavigate ? (
                <button
                  key={row.name}
                  type="button"
                  onClick={() => onNavigate('filings')}
                  aria-label={`Open ${row.name} in filings`}
                  className="flex w-full items-center gap-2.5 rounded-md text-left transition-colors hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                >
                  {rowContent}
                </button>
              ) : (
                <div key={row.name} className="flex items-center gap-2.5">
                  {rowContent}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
};

export const ComplianceDashboardMock = () => (
  <AppShell
    title="Compliance Overview"
    subtitle="Dateheight Integrated Nigeria Ltd · TIN 20845119-0001"
    crumb="Overview"
    actions={
      <span className="inline-flex items-center gap-1 rounded-md bg-slate-900 px-2.5 py-1.5 text-[11px] font-semibold text-white">
        <Plus size={12} /> New filing
      </span>
    }
  >
    <DashboardContent />
  </AppShell>
);

/* ── 2. Filings tracker ──────────────────────────────────────── */

const filings = [
  { type: 'Value Added Tax', period: 'Jan 2026', authority: 'FIRS', due: '21 Feb', amount: '₦312,400', status: 'Due' },
  { type: 'PAYE', period: 'Jan 2026', authority: 'LIRS', due: '10 Feb', amount: '₦184,900', status: 'Filed' },
  { type: 'Company Income Tax', period: 'FY 2025', authority: 'FIRS', due: '30 Jun', amount: '₦1,240,000', status: 'Draft' },
  { type: 'Withholding Tax', period: 'Jan 2026', authority: 'FIRS', due: '21 Feb', amount: '₦56,300', status: 'Due' },
  { type: 'CAC Annual Return', period: '2025', authority: 'CAC', due: '31 Mar', amount: '₦12,500', status: 'Overdue' },
  { type: 'Pension Schedule', period: 'Jan 2026', authority: 'PENCOM', due: '07 Feb', amount: '₦98,700', status: 'Paid' },
];

const FilingsContent = ({ onNavigate }) => (
  <>
    <div className="mb-3 flex flex-wrap gap-1.5">
      {['All', 'Due', 'Filed', 'Overdue', 'Draft'].map((t, i) => (
        <span
          key={t}
          className={cn(
            'rounded-full border px-2.5 py-1 text-[10px] font-semibold',
            i === 0
              ? 'border-slate-900 bg-slate-900 text-white'
              : 'border-slate-200 bg-white text-slate-500'
          )}
        >
          {t}
        </span>
      ))}
    </div>
    <div className="overflow-hidden rounded-lg border border-slate-200">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-400">
            <th className="px-3 py-2 font-semibold">Filing</th>
            <th className="hidden px-3 py-2 font-semibold sm:table-cell">Period</th>
            <th className="hidden px-3 py-2 font-semibold md:table-cell">Authority</th>
            <th className="px-3 py-2 font-semibold">Due</th>
            <th className="hidden px-3 py-2 text-right font-semibold sm:table-cell">Amount</th>
            <th className="px-3 py-2 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {filings.map((f) => (
            <tr
              key={f.type + f.period}
              onClick={onNavigate ? () => onNavigate('documents') : undefined}
              onKeyDown={
                onNavigate
                  ? (e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        onNavigate('documents');
                      }
                    }
                  : undefined
              }
              tabIndex={onNavigate ? 0 : undefined}
              aria-label={onNavigate ? `Open ${f.type} documents` : undefined}
              className={cn(
                'text-[11px] text-slate-700',
                onNavigate &&
                  'cursor-pointer transition-colors hover:bg-slate-50 focus:outline-none focus-visible:bg-slate-50 focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-600'
              )}
            >
              <td className="px-3 py-2.5 font-medium text-slate-900">{f.type}</td>
              <td className="hidden px-3 py-2.5 text-slate-500 sm:table-cell">{f.period}</td>
              <td className="hidden px-3 py-2.5 text-slate-500 md:table-cell">{f.authority}</td>
              <td className="px-3 py-2.5 tabular-nums text-slate-500">{f.due}</td>
              <td className="hidden px-3 py-2.5 text-right tabular-nums text-slate-700 sm:table-cell">
                {f.amount}
              </td>
              <td className="px-3 py-2.5">
                <StatusPill status={f.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </>
);

export const FilingsTrackerMock = () => (
  <AppShell
    title="Filings"
    subtitle="All statutory filings across every entity"
    actions={
      <span className="inline-flex items-center gap-1 rounded-md bg-slate-900 px-2.5 py-1.5 text-[11px] font-semibold text-white">
        <Plus size={12} /> New
      </span>
    }
  >
    <FilingsContent />
  </AppShell>
);

/* ── 3. Tax estimator widget ─────────────────────────────────── */

export const TaxEstimatorMock = () => (
  <div className="p-5">
    <div className="mb-4 flex flex-wrap gap-1.5">
      {['PAYE', 'Take-home pay', 'Pension', 'VAT', 'CIT'].map((t, i) => (
        <span
          key={t}
          className={cn(
            'inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-[11px] font-semibold',
            i === 0
              ? 'border-slate-900 bg-slate-900 text-white'
              : 'border-slate-200 bg-white text-slate-500'
          )}
        >
          {i === 0 && <Calculator size={12} className="text-blue-400" />}
          {t}
        </span>
      ))}
    </div>

    <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
      <div className="space-y-3 sm:col-span-3">
        <label className="block">
          <span className="mb-1.5 block text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            Monthly employment income
          </span>
          <div className="flex h-11 items-center justify-between rounded-sm border border-slate-200 bg-white px-3">
            <span className="text-sm font-medium tabular-nums text-slate-900">₦ 850,000</span>
            <span className="text-[10px] text-slate-400">NGN</span>
          </div>
        </label>
        <div className="flex items-center justify-between rounded-sm border border-slate-200 bg-white px-3 py-2.5">
          <span className="text-[11px] text-slate-600">Employee pension (8%)</span>
          <span className="relative h-5 w-9 rounded-full bg-blue-600">
            <span className="absolute right-0.5 top-0.5 h-4 w-4 rounded-full bg-white shadow" />
          </span>
        </div>
        <div className="flex items-center justify-between rounded-sm border border-slate-200 bg-white px-3 py-2.5">
          <span className="text-[11px] text-slate-600">National Housing Fund (2.5%)</span>
          <span className="relative h-5 w-9 rounded-full bg-slate-300">
            <span className="absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white shadow" />
          </span>
        </div>
      </div>

      <div className="rounded-lg bg-slate-900 p-4 text-white sm:col-span-2">
        <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-[0.2em] text-slate-400">
          <Landmark size={12} className="text-blue-400" /> PAYE estimate
        </div>
        <div className="mt-2 border-b border-slate-800 pb-3">
          <p className="text-[10px] text-slate-400">Annual estimate</p>
          <p className="text-2xl font-bold tabular-nums">₦1,296,000</p>
        </div>
        <div className="mt-3 space-y-1.5 text-[11px]">
          {[
            ['Monthly PAYE', '₦108,000'],
            ['Pension relief', '− ₦68,000'],
            ['Rent relief', '− ₦41,667'],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between">
              <span className="text-slate-400">{k}</span>
              <span className="tabular-nums font-medium">{v}</span>
            </div>
          ))}
          <div className="flex justify-between border-t border-slate-800 pt-2">
            <span className="text-slate-400">Monthly take-home</span>
            <span className="font-semibold tabular-nums text-emerald-400">₦606,333</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

/* ── 4. Deadline / alert feed ────────────────────────────────── */

const feed = [
  { sev: 'critical', title: 'CAC Annual Return overdue', meta: 'REVCON Nigeria Ltd · 6 days overdue', tag: 'Compliance', icon: AlertTriangle },
  { sev: 'warning', title: 'VAT remittance window closing', meta: 'Dateheight Integrated · due 21 Feb', tag: 'Tax', icon: Clock },
  { sev: 'info', title: 'New Tax Act 2025 rule detected', meta: 'PAYE bands updated · effective Jan 2026', tag: 'Regulatory', icon: BrainCircuit },
  { sev: 'ok', title: 'TCC issued for Oasis Zing', meta: 'Valid until 14 Feb 2027', tag: 'Certificate', icon: CheckCircle2 },
];

export const DeadlineFeedMock = () => (
  <div className="p-5">
    <div className="mb-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <p className="text-sm font-semibold text-slate-900">Deadline feed</p>
        <span className="rounded-full bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-600">
          4 active
        </span>
      </div>
      <span className="text-[10px] text-slate-400">Updated 2m ago</span>
    </div>
    <div className="space-y-2">
      {feed.map((row) => {
        const Icon = row.icon;
        const sev = {
          critical: 'border-l-rose-500 text-rose-600 bg-rose-50',
          warning: 'border-l-amber-500 text-amber-600 bg-amber-50',
          info: 'border-l-blue-500 text-blue-600 bg-blue-50',
          ok: 'border-l-emerald-500 text-emerald-600 bg-emerald-50',
        }[row.sev];
        return (
          <div
            key={row.title}
            className={cn(
              'flex items-start gap-3 rounded-md border border-slate-200 border-l-4 bg-white p-3',
              row.sev === 'critical' && 'border-l-rose-500',
              row.sev === 'warning' && 'border-l-amber-500',
              row.sev === 'info' && 'border-l-blue-500',
              row.sev === 'ok' && 'border-l-emerald-500'
            )}
          >
            <span className={cn('flex h-7 w-7 shrink-0 items-center justify-center rounded-md', sev)}>
              <Icon size={14} />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-[12px] font-semibold text-slate-800">{row.title}</p>
              <p className="truncate text-[11px] text-slate-400">{row.meta}</p>
            </div>
            <span className="hidden shrink-0 rounded-full border border-slate-200 px-2 py-0.5 text-[10px] font-medium text-slate-500 sm:inline-flex">
              {row.tag}
            </span>
          </div>
        );
      })}
    </div>
  </div>
);

/* ── 5. Document vault ───────────────────────────────────────── */

const docs = [
  { name: 'Tax Clearance Certificate', meta: 'PDF · expires Feb 2027', status: 'Valid', icon: BadgeCheck },
  { name: 'Certificate of Incorporation', meta: 'PDF · CAC RC 1845203', status: 'Valid', icon: Building2 },
  { name: 'VAT Returns — Q4 2025', meta: 'PDF · filed 20 Jan 2026', status: 'Filed', icon: ReceiptText },
  { name: 'Audited Financial Statements', meta: 'PDF · FY 2025', status: 'Draft', icon: FileText },
  { name: 'SCUML Certificate', meta: 'PDF · renews Nov 2026', status: 'Valid', icon: ShieldCheck },
  { name: 'Board Resolution Pack', meta: 'PDF · 8 pages', status: 'Filed', icon: FolderLock },
];

const DocumentsContent = () => (
  <>
    <div className="mb-3 flex items-center justify-between">
      <div>
        <p className="text-sm font-semibold text-slate-900">Document vault</p>
        <p className="text-[11px] text-slate-400">142 documents · encrypted at rest</p>
      </div>
      <span className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1.5 text-[11px] font-semibold text-slate-600">
        <Download size={12} /> Export
      </span>
    </div>
    <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
      {docs.map((d) => {
        const Icon = d.icon;
        return (
          <div
            key={d.name}
            className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 transition-colors hover:border-slate-300"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-500">
              <Icon size={16} />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[12px] font-medium text-slate-800">{d.name}</p>
              <p className="truncate text-[10px] text-slate-400">{d.meta}</p>
            </div>
            <StatusPill status={d.status} />
          </div>
        );
      })}
    </div>
  </>
);

export const DocumentVaultMock = () => (
  <div className="p-5">
    <DocumentsContent />
  </div>
);

/* ── 6. Advisory / optimization ──────────────────────────────── */

const AdvisoryContent = () => (
  <>
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <div className="lg:col-span-3">
        <p className="text-sm font-semibold text-slate-900">Compliance health</p>
        <p className="text-[11px] text-slate-400">Trailing 8 quarters</p>
        <div className="relative mt-4 h-40">
          <svg viewBox="0 0 320 140" className="h-full w-full" preserveAspectRatio="none">
            <defs>
              <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2563eb" stopOpacity="0.18" />
                <stop offset="100%" stopColor="#2563eb" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0 110 L45 96 L90 100 L135 72 L180 66 L225 44 L270 38 L320 18"
              fill="none"
              stroke="#2563eb"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <path
              d="M0 110 L45 96 L90 100 L135 72 L180 66 L225 44 L270 38 L320 18 L320 140 L0 140 Z"
              fill="url(#areaFill)"
            />
          </svg>
        </div>
        <div className="mt-2 flex justify-between text-[9px] text-slate-400">
          {['Q1', 'Q2', 'Q3', 'Q4', 'Q1', 'Q2', 'Q3', 'Q4'].map((q, i) => (
            <span key={i}>{q}</span>
          ))}
        </div>
      </div>

      <div className="space-y-2.5 lg:col-span-2">
        {[
          { label: 'Compliance score', value: '98.4%', delta: '+24 pts', up: true },
          { label: 'Filing on-time rate', value: '100%', delta: '+6.2%', up: true },
          { label: 'Late penalties YTD', value: '₦0', delta: '−₦410k', up: true },
        ].map((s) => (
          <div key={s.label} className="rounded-lg border border-slate-200 bg-white p-3">
            <p className="text-[10px] uppercase tracking-wider text-slate-400">{s.label}</p>
            <div className="mt-1 flex items-end justify-between">
              <span className="text-xl font-bold tabular-nums text-slate-900">{s.value}</span>
              <span className="inline-flex items-center gap-0.5 text-[10px] font-semibold text-emerald-600">
                <ArrowUpRight size={11} /> {s.delta}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>

    <div className="mt-4 flex items-start gap-3 rounded-lg border border-blue-100 bg-blue-50/60 p-3">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-blue-600 text-white">
        <Sparkles size={14} />
      </span>
      <div>
        <p className="text-[12px] font-semibold text-slate-800">Advisor recommendation</p>
        <p className="text-[11px] leading-relaxed text-slate-600">
          Claim the unutilised ₦410,000 capital allowance this period to reduce the Q2 CIT
          installment. Prepared for your review.
        </p>
      </div>
      <ChevronRight size={16} className="ml-auto hidden shrink-0 self-center text-slate-400 sm:block" />
    </div>
  </>
);

export const AdvisoryMock = () => (
  <div className="p-5">
    <AdvisoryContent />
  </div>
);

/* ── 7. Payments ─────────────────────────────────────────────── */

const payments = [
  { ref: 'INV-2041', name: 'VAT remittance · Feb 2026', due: 'Due 21 Feb', amount: '₦312,400', status: 'Due' },
  { ref: 'INV-2038', name: 'PAYE · Jan 2026', due: 'Paid 08 Feb', amount: '₦184,900', status: 'Paid' },
  { ref: 'INV-2032', name: 'CIT installment · Q1 2026', due: 'Due 30 Mar', amount: '₦420,000', status: 'Draft' },
  { ref: 'INV-2027', name: 'CAC annual return', due: 'Overdue 3 days', amount: '₦12,500', status: 'Overdue' },
];

const PaymentsContent = () => (
  <>
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <Kpi label="Outstanding" value="₦744,900" delta="2 invoices" up={false} icon={ReceiptText} />
      <Kpi label="Paid this quarter" value="₦2.1M" delta="6.4" up icon={Landmark} />
      <Kpi label="Next payment due" value="₦312,400" icon={Clock} />
    </div>
    <div className="mt-3 overflow-hidden rounded-lg border border-slate-200">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-400">
            <th className="px-3 py-2 font-semibold">Invoice</th>
            <th className="hidden px-3 py-2 font-semibold sm:table-cell">Description</th>
            <th className="px-3 py-2 font-semibold">Due</th>
            <th className="px-3 py-2 text-right font-semibold">Amount</th>
            <th className="px-3 py-2 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {payments.map((p) => (
            <tr key={p.ref} className="text-[11px] text-slate-700">
              <td className="px-3 py-2.5 font-medium text-slate-900">{p.ref}</td>
              <td className="hidden px-3 py-2.5 text-slate-500 sm:table-cell">{p.name}</td>
              <td className="px-3 py-2.5 text-slate-500">{p.due}</td>
              <td className="px-3 py-2.5 text-right tabular-nums text-slate-700">{p.amount}</td>
              <td className="px-3 py-2.5">
                <StatusPill status={p.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </>
);

/* ── 8. Interactive page wrapper ─────────────────────────────── */

const portalPages = {
  overview: {
    title: 'Compliance Overview',
    subtitle: 'Dateheight Integrated Nigeria Ltd · TIN 20845119-0001',
    action: (onNavigate) => (
      <button
        type="button"
        onClick={() => onNavigate && onNavigate('filings')}
        className="inline-flex items-center gap-1 rounded-md bg-slate-900 px-2.5 py-1.5 text-[11px] font-semibold text-white transition-colors hover:bg-slate-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
      >
        <Plus size={12} /> New filing
      </button>
    ),
    render: (onNavigate) => <DashboardContent onNavigate={onNavigate} />,
  },
  filings: {
    title: 'Filings',
    subtitle: 'All statutory filings across every entity',
    action: () => (
      <span className="inline-flex items-center gap-1 rounded-md bg-slate-900 px-2.5 py-1.5 text-[11px] font-semibold text-white">
        <Plus size={12} /> New
      </span>
    ),
    render: (onNavigate) => <FilingsContent onNavigate={onNavigate} />,
  },
  documents: {
    title: 'Documents',
    subtitle: 'Certificates, returns & resolutions',
    action: () => (
      <span className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1.5 text-[11px] font-semibold text-slate-600">
        <Download size={12} /> Export
      </span>
    ),
    render: () => <DocumentsContent />,
  },
  payments: {
    title: 'Payments',
    subtitle: 'Invoices, remittances and receipts',
    action: () => (
      <span className="inline-flex items-center gap-1 rounded-md bg-slate-900 px-2.5 py-1.5 text-[11px] font-semibold text-white">
        <Landmark size={12} /> Make payment
      </span>
    ),
    render: () => <PaymentsContent />,
  },
  advisory: {
    title: 'Advisory',
    subtitle: 'Compliance health and recommendations',
    render: () => <AdvisoryContent />,
  },
};

export const PortalPageMock = ({ page = 'overview', onNavigate }) => {
  const meta = portalPages[page] || portalPages.overview;
  return (
    <AppShell
      title={meta.title}
      subtitle={meta.subtitle}
      activeNav={page}
      onNavigate={onNavigate}
      actions={meta.action ? meta.action(onNavigate) : undefined}
    >
      {meta.render(onNavigate)}
    </AppShell>
  );
};
