import { useState, useCallback } from 'react'
import { api } from '../api/client'
import type { ChunkResult } from '../types'
import SearchResults from '../components/SearchResults'

const COLLECTION_NAME = 'default'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<ChunkResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setSearched(true)

    try {
      const cols = await api.listCollections()
      const col = cols.find((c) => c.name === COLLECTION_NAME)
      if (!col) {
        setError('No collection found. Upload a document first.')
        setResults([])
        return
      }

      const res = await api.search(col.id, query)
      setResults(res.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [query])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Semantic Search</h2>
        <p className="text-gray-400 text-sm mt-1">
          Search indexed documents by meaning, not just keywords.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search documents..."
          className="flex-1 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="p-3 rounded-lg bg-red-900/30 border border-red-800 text-red-300 text-sm">
          {error}
        </div>
      )}

      {searched && results.length > 0 && (
        <p className="text-gray-500 text-sm">
          Found {results.length} result{results.length !== 1 ? 's' : ''}
        </p>
      )}

      <SearchResults results={results} loading={loading} query={searched ? query : ''} />
    </div>
  )
}
