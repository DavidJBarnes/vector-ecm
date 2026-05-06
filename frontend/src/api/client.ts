const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  // Collections
  listCollections: () => request<import('../types').Collection[]>('/collections'),
  createCollection: (data: { name: string; description?: string; metadata?: Record<string, unknown> }) =>
    request<import('../types').Collection>('/collections', { method: 'POST', body: JSON.stringify(data) }),
  deleteCollection: (id: string) =>
    request<void>(`/collections/${id}`, { method: 'DELETE' }),

  // Documents
  listDocuments: (collectionId: string) =>
    request<import('../types').Document[]>(`/collections/${collectionId}/documents`),
  getDocument: (collectionId: string, docId: string) =>
    request<import('../types').Document & { chunks: unknown[] }>(`/collections/${collectionId}/documents/${docId}`),
  createDocument: (collectionId: string, data: { title: string; content: string; metadata?: Record<string, unknown> }) =>
    request<import('../types').Document>(`/collections/${collectionId}/documents`, { method: 'POST', body: JSON.stringify(data) }),
  deleteDocument: (collectionId: string, docId: string) =>
    request<void>(`/collections/${collectionId}/documents/${docId}`, { method: 'DELETE' }),

  // Search
  search: (collectionId: string, query: string, topK = 5) =>
    request<import('../types').SearchResponse>(`/collections/${collectionId}/search`, {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    }),

  // Chat
  chat: (collectionId: string, message: string, topK = 5) =>
    request<import('../types').ChatResponse>(`/collections/${collectionId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, top_k: topK }),
    }),
}
