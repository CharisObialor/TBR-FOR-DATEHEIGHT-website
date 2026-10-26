import React from 'react';
import { cn } from '../../lib/utils';

const dotColors = ['bg-rose-400', 'bg-amber-400', 'bg-emerald-400'];

export const ProductFrame = ({
  url = 'portal.tbrsolutions.ng/overview',
  children,
  className,
  bodyClassName,
  tabs,
  activeTab,
}) => {
  return (
    <div
      className={cn(
        'overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[0_24px_70px_-30px_rgba(15,23,42,0.35)]',
        className
      )}
    >
      {/* Window chrome */}
      <div className="flex items-center gap-3 border-b border-slate-200 bg-slate-50 px-4 py-2.5">
        <div className="flex items-center gap-1.5">
          {dotColors.map((c) => (
            <span key={c} className={cn('h-3 w-3 rounded-full', c)} />
          ))}
        </div>
        <div className="mx-auto hidden min-w-0 max-w-md flex-1 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-1.5 sm:flex">
          <span className="h-3.5 w-3.5 shrink-0 rounded-full border border-slate-300" />
          <span className="truncate font-mono text-[11px] text-slate-500">{url}</span>
        </div>
        <div className="ml-auto hidden gap-1.5 sm:flex">
          <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
          <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
        </div>
      </div>

      {/* Optional in-app tabs */}
      {tabs && (
        <div className="flex items-center gap-1 overflow-x-auto border-b border-slate-200 bg-white px-3">
          {tabs.map((tab) => (
            <span
              key={tab}
              className={cn(
                'whitespace-nowrap border-b-2 px-3 py-2.5 text-xs font-medium transition-colors',
                tab === activeTab
                  ? 'border-blue-600 text-slate-900'
                  : 'border-transparent text-slate-400'
              )}
            >
              {tab}
            </span>
          ))}
        </div>
      )}

      <div className={cn('bg-white', bodyClassName)}>{children}</div>
    </div>
  );
};

export default ProductFrame;
