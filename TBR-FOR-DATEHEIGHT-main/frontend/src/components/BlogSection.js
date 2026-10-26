import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Newspaper, CalendarDays } from 'lucide-react';
import { resourcesAPI } from '../lib/api';
import { Stagger, RevealItem } from './Reveal';
import { SectionIntro } from './marketing/SectionIntro';

const formatDate = (d) => {
  if (!d) return '';
  const match = String(d).match(/(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/) || String(d).match(/(\w+ \d{1,2}, \d{4})/);
  if (match) return String(d);
  const parsed = new Date(d);
  return isNaN(parsed.getTime()) ? String(d) : parsed.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
};

const CATEGORY_STYLES = {
  Tax: 'bg-blue-50 text-blue-700 border-blue-200',
  Business: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Revenue Assurance': 'bg-amber-50 text-amber-700 border-amber-200',
  Investment: 'bg-violet-50 text-violet-700 border-violet-200',
  default: 'bg-slate-100 text-slate-600 border-slate-200',
};

const BlogSection = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    resourcesAPI
      .list({ published: true })
      .then((res) => {
        if (!mounted) return;
        setArticles((res.data || []).slice(0, 3));
      })
      .catch(() => {
        if (mounted) setArticles([]);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section className="py-24 sm:py-32" data-testid="blog-section">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mb-14 flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <SectionIntro
            overline="Insights & Resources"
            title="Tax, business & investment intelligence"
            description="Curated articles from trusted Nigerian publications and authorities — so you can stay current on the rules that keep changing."
            className="max-w-2xl"
          />
          <Link
            to="/resources"
            className="inline-flex shrink-0 items-center gap-2 self-start rounded-full border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-900 transition-colors hover:border-slate-400 hover:bg-slate-50 sm:self-auto"
            data-testid="view-all-resources-button"
          >
            View all articles
            <ArrowUpRight size={16} />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-72 animate-pulse rounded-2xl bg-slate-100" />
            ))}
          </div>
        ) : articles.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 p-10 text-center text-slate-500">
            Articles are being prepared — check back soon.
          </div>
        ) : (
          <Stagger className="grid grid-cols-1 gap-6 md:grid-cols-3" stagger={0.12}>
            {articles.map((article) => {
              const style = CATEGORY_STYLES[article.category] || CATEGORY_STYLES.default;
              const isExternal = Boolean(article.source_url);
              const Card = (
                <>
                  {article.featured_image && (
                    <div className="relative -mx-6 -mt-6 mb-4 h-40 overflow-hidden">
                      <img
                        src={article.featured_image}
                        alt={article.title}
                        loading="lazy"
                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                      />
                      <span className={`absolute left-3 top-3 inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                        {article.category}
                      </span>
                    </div>
                  )}
                  <div className="mb-4 flex items-start justify-between gap-3">
                    {!article.featured_image && (
                      <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${style}`}>
                        {article.category}
                      </span>
                    )}
                    {isExternal && <ArrowUpRight size={16} className="text-slate-400" />}
                  </div>
                  <h3 className="mb-3 text-lg font-semibold leading-snug text-slate-900 transition-colors group-hover:text-blue-700">
                    {article.title}
                  </h3>
                  <p className="mb-6 line-clamp-3 text-sm text-slate-600">{article.excerpt}</p>
                  <div className="mt-auto flex items-center justify-between gap-2 border-t border-slate-100 pt-4 text-xs text-slate-500">
                    <span className="truncate font-medium">{article.source_name}</span>
                    <span className="inline-flex shrink-0 items-center gap-1">
                      <CalendarDays size={12} />
                      {formatDate(article.source_date) || (article.read_label || 'Read article')}
                    </span>
                  </div>
                </>
              );

              const cls = 'group flex h-full flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_60px_-40px_rgba(15,23,42,0.5)]';

              return (
                <RevealItem key={article.id || article.slug} className="h-full">
                  {isExternal ? (
                    <a
                      href={article.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={cls}
                      data-testid={`blog-card-${article.slug}`}
                    >
                      {Card}
                    </a>
                  ) : (
                    <Link to={`/resources/${article.slug}`} className={cls} data-testid={`blog-card-${article.slug}`}>
                      {Card}
                    </Link>
                  )}
                </RevealItem>
              );
            })}
          </Stagger>
        )}
      </div>
    </section>
  );
};

export default BlogSection;
