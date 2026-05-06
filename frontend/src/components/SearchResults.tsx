import type { ChunkResult } from '../types'

interface Props {
  results: ChunkResult[]
  loading: boolean
  query: string
}

export default function SearchResults({ results, loading, query }: Props) {
  if (!query.trim()) {
    return <p className="text-gray-500 py-8 text-center">Enter a query to search.</p>
  }

  if (loading) {
    return <p className="text-gray-400 py-8 text-center">Searching...</p>
  }

  if (results.length === 0) {
    return <p className="text-gray-500 py-8 text-center">No results found.</p>
  }

  return (
    <div className="space-y-3">
      {results.map((r, i) => (
        <div
          key={r.chunk_id}
          className="p-4 rounded-lg bg-gray-800/50 border border-gray-700/50"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded font-mono">
                #{i + 1} · score {r.score.toFixed(3)}
              </span>
              <span className="text-sm text-indigo-400 font-medium">
                {r.document_title}
              </span>
              <span className="text-xs text-gray-600">
                chunk {r.chunk_index}
              </span>
            </div>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
            {r.content}
          </p>
        </div>
      ))}
    </div>
  )
}
