import type { Document } from '../types'

interface Props {
  documents: Document[]
  loading: boolean
  onDelete: (id: string) => void
}

export default function DocumentList({ documents, loading, onDelete }: Props) {
  if (loading) {
    return <p className="text-gray-400 py-4">Loading documents...</p>
  }

  if (documents.length === 0) {
    return <p className="text-gray-500 py-4">No documents yet. Upload one above.</p>
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 border border-gray-700/50"
        >
          <div className="min-w-0 flex-1">
            <p className="text-gray-200 font-medium truncate">{doc.title}</p>
            <p className="text-gray-500 text-xs mt-0.5">
              {doc.chunk_count} chunks · {new Date(doc.created_at).toLocaleDateString()}
            </p>
          </div>
          <button
            onClick={() => onDelete(doc.id)}
            className="ml-4 px-3 py-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded transition-colors"
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  )
}
