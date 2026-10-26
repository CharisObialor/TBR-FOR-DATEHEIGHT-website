import React from 'react';
import { cn } from '../../lib/utils';
import { Reveal } from '../Reveal';

export const SectionIntro = ({
  overline,
  number,
  title,
  description,
  align = 'left',
  className,
  children,
}) => {
  return (
    <Reveal
      className={cn(
        'max-w-2xl',
        align === 'center' && 'mx-auto text-center',
        className
      )}
    >
      {(overline || number) && (
        <div
          className={cn(
            'mb-4 flex items-center gap-3',
            align === 'center' && 'justify-center'
          )}
        >
          {number && (
            <span className="font-mono text-xs font-semibold tracking-widest text-blue-600">
              {number}
            </span>
          )}
          {number && overline && <span className="h-px w-6 bg-slate-300" />}
          {overline && (
            <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              {overline}
            </span>
          )}
        </div>
      )}
      {title && (
        <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
          {title}
        </h2>
      )}
      {description && (
        <p className="mt-5 text-base leading-relaxed text-slate-600">{description}</p>
      )}
      {children}
    </Reveal>
  );
};

export default SectionIntro;
