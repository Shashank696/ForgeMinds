import { useState, useCallback } from 'react';
import { searchDocuments } from '../services/api';

export default function useSearch() {
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [searchTimeMs, setSearchTimeMs] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('forgeminds-search-history') || '[]');
    } catch { return []; }
  });

  const executeSearch = useCallback(async (data) => {
    setIsLoading(true);
    try {
      const res = await searchDocuments(data);
      setResults(res.results || []);
      setTotalResults(res.total_results || 0);
      setSearchTimeMs(res.search_time_ms || 0);
      // save to history
      if (data.query) {
        setSearchHistory((prev) => {
          const updated = [data.query, ...prev.filter((q) => q !== data.query)].slice(0, 10);
          localStorage.setItem('forgeminds-search-history', JSON.stringify(updated));
          return updated;
        });
      }
    } catch (e) {
      console.error('Search failed', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setTotalResults(0);
    setSearchTimeMs(0);
  }, []);

  return {
    results, totalResults, searchTimeMs, isLoading, searchHistory,
    executeSearch, clearResults,
  };
}
