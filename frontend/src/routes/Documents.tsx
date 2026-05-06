import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import type { Document as DocType } from '../types'
import DocumentUpload from '../components/DocumentUpload'
import DocumentList from '../components/DocumentList'

const COLLECTION_NAME = 'default'

export default function DocumentsPage() {
  const [collectionId, setCollectionId] = useState<string | null>(null)
  const [documents, setDocuments] = useState<DocType[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const ensureCollection = useCallback(async () => {
    try {
      const cols = await api.listCollections()
      const existing = cols.find((c) => c.name === COLLECTION_NAME)
      if (existing) {
        setCollectionId(existing.id)
        return existing.id
      }
      const created = await api.createCollection({ name: COLLECTION_NAME })
      setCollectionId(created.id)
      return created.id
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to init collection')
      return null
    }
  }, [])

  const loadDocuments = useCallback(async (colId: string) => {
    setLoading(true)
    try {
      const docs = await api.listDocuments(colId)
      setDocuments(docs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    ensureCollection().then((id) => {
      if (id) loadDocuments(id)
    })
  }, [ensureCollection, loadDocuments])

  const handleUpload = async (title: string, content: string) => {
    if (!collectionId) return
    setUploading(true)
    setError(null)
    try {
      await api.createDocument(collectionId, { title, content })
      await loadDocuments(collectionId)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (docId: string) => {
    if (!collectionId) return
    try {
      await api.deleteDocument(collectionId, docId)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Document Management</h2>
        <p className="text-gray-400 text-sm mt-1">
          Upload documents to index them for semantic search. Text is automatically chunked and embedded.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-900/30 border border-red-800 text-red-300 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      <DocumentUpload onUpload={handleUpload} uploading={uploading} />

      <div>
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
          Indexed Documents ({documents.length})
        </h3>
        <DocumentList documents={documents} loading={loading} onDelete={handleDelete} />
      </div>
    </div>
  )
}
