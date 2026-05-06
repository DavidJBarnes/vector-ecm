export interface Collection {
  id: string
  name: string
  description: string | null
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
  document_count: number
}

export interface Document {
  id: string
  collection_id: string
  title: string
  content: string
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
  chunk_count: number
}

export interface ChunkResult {
  chunk_id: string
  document_id: string
  document_title: string
  chunk_index: number
  content: string
  score: number
  metadata: Record<string, unknown>
}

export interface SearchResponse {
  query: string
  results: ChunkResult[]
  total: number
}

export interface ChatResponse {
  answer: string
  sources: {
    chunk_id: string
    document_id: string
    document_title: string
    chunk_index: number
    score: number
  }[]
  model: string
}
