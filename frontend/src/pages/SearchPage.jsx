import { useState } from 'react';
import { Search } from 'lucide-react';
import useSearch from '../hooks/useSearch';
import { SEARCH_TYPE_LABELS } from '../utils/constants';
import { ENTITY_TYPE_COLORS } from '../utils/constants';
import { capitalize, truncateText } from '../utils/formatters';

export default function SearchPage() {
  const { results, totalResults, searchTimeMs, isLoading, searchHistory, executeSearch } = useSearch();
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('hybrid');

  const handleSearch = (q) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;
    executeSearch({ query: searchQuery.trim(), search_type: searchType, limit: 10 });
    if (q) setQuery(q);
  };

  return (
    <div className="page animate-fade-in">
      <div className="search-hero">
        <h1 style={{ marginBottom: 'var(--spacing-sm)' }}>Search Knowledge Base</h1>
        <p className="text-secondary" style={{ marginBottom: 'var(--spacing-xl)' }}>Semantic, keyword, and graph-powered search across all your industrial documents</p>

        <div className="search-input-large">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search documents, procedures, equipment..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>

        <div className="flex gap-xs justify-center" style={{ marginTop: 'var(--spacing-lg)' }}>
          {Object.entries(SEARCH_TYPE_LABELS).map(([key, label]) => (
            <button key={key} className={`tab ${searchType === key ? 'active' : ''}`} onClick={() => setSearchType(key)}>{label}</button>
          ))}
        </div>
      </div>

      {searchHistory.length > 0 && !results.length && (
        <div style={{ marginBottom: 'var(--spacing-xl)' }}>
          <p className="text-xs text-muted font-semibold" style={{ textTransform: 'uppercase', marginBottom: 'var(--spacing-sm)' }}>Recent Searches</p>
          <div className="flex flex-wrap gap-sm">
            {searchHistory.map((q, i) => (
              <button key={i} className="chat-followup-chip" onClick={() => { setQuery(q); handleSearch(q); }}>{q}</button>
            ))}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex flex-col gap-md">{[1,2,3].map(i => <div key={i} className="skeleton skeleton-card" />)}</div>
      )}

      {!isLoading && results.length > 0 && (
        <>
          <p className="text-sm text-muted" style={{ marginBottom: 'var(--spacing-lg)' }}>
            Found <strong>{totalResults}</strong> results in <strong>{searchTimeMs}ms</strong>
          </p>
          <div className="flex flex-col gap-md">
            {results.map((r, i) => (
              <div key={i} className="search-result-card animate-fade-in-up" style={{ animationDelay: `${i * 50}ms` }}>
                <div className="flex items-center gap-sm" style={{ marginBottom: 'var(--spacing-sm)' }}>
                  <h4 className="text-base font-semibold">{r.document_title}</h4>
                  <span className="badge badge-primary">{capitalize(r.document_category)}</span>
                  {r.page_number && <span className="text-xs text-muted">p.{r.page_number}</span>}
                </div>
                <p className="text-sm text-secondary" style={{ marginBottom: 'var(--spacing-sm)', lineHeight: 1.6 }}>{truncateText(r.chunk_text, 200)}</p>
                <div className="flex items-center gap-md">
                  <div className="flex items-center gap-sm flex-1">
                    <span className="text-xs text-muted">Relevance</span>
                    <div className="progress-bar" style={{ width: 80, height: 4 }}>
                      <div className="progress-fill" style={{ width: `${(r.relevance_score || 0) * 100}%` }} />
                    </div>
                    <span className="text-xs font-medium">{Math.round((r.relevance_score || 0) * 100)}%</span>
                  </div>
                  {r.entities?.length > 0 && (
                    <div className="flex gap-xs">
                      {r.entities.slice(0, 3).map((ent, j) => (
                        <span key={j} className="badge" style={{ background: `${ENTITY_TYPE_COLORS[ent.entity_type] || '#666'}22`, color: ENTITY_TYPE_COLORS[ent.entity_type] || '#666', fontSize: '0.6rem' }}>
                          {ent.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
