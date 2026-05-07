import { useState, useRef, useCallback, useEffect } from 'react'
import { api } from '../api/client'
import type { Message } from '../types'

const COLLECTION_NAME = 'default'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setError(null)

    const userMsg: Message = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])

    setLoading(true)
    const controller = new AbortController()
    setAbortController(controller)

    try {
      const cols = await api.listCollections()
      let col = cols.find((c) => c.name === COLLECTION_NAME)
      if (!col) {
        col = await api.createCollection({ name: COLLECTION_NAME })
      }

      const reader = await api.chatStream(col.id, text, controller.signal)
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantContent = ''
      let sources: Message['sources'] | undefined

      setMessages((prev) => [...prev, { role: 'assistant', content: '' }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') break

          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'sources') {
              sources = parsed.sources.map((s: { document_title: string; chunk_index: number; score: number }) => ({
                document_title: s.document_title,
                chunk_index: s.chunk_index,
                score: s.score,
              }))
            } else if (parsed.type === 'content') {
              assistantContent += parsed.content
              setMessages((prev) => {
                const next = [...prev]
                next[next.length - 1] = { role: 'assistant', content: assistantContent, sources }
                return next
              })
            }
          } catch { }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError(err instanceof Error ? err.message : 'Chat failed')
      }
    } finally {
      setLoading(false)
      setAbortController(null)
    }
  }, [input, loading])

  const handleStop = () => {
    abortController?.abort()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div>
        <h2 className="text-xl font-semibold text-white">Chat</h2>
        <p className="text-gray-400 text-sm mt-1">
          Ask questions about your indexed documents using AI.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto mt-4 space-y-4 pr-2">
        {messages.length === 0 && (
          <p className="text-gray-500 py-8 text-center">
            Send a message to start chatting with your documents.
          </p>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-800/50 border border-gray-700/50 text-gray-200'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-300">
                    Sources ({msg.sources.length})
                  </summary>
                  <div className="mt-1 space-y-1">
                    {msg.sources.map((s, j) => (
                      <div key={j} className="text-xs text-gray-500 flex gap-2">
                        <span className="text-indigo-400">{s.document_title}</span>
                        <span>chunk {s.chunk_index}</span>
                        <span>score {s.score.toFixed(3)}</span>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}

        {error && (
          <div className="p-3 rounded-lg bg-red-900/30 border border-red-800 text-red-300 text-sm">
            {error}
            <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="mt-4 flex gap-3 items-end">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          rows={2}
          className="flex-1 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm resize-none"
        />
        {loading ? (
          <button
            onClick={handleStop}
            className="px-4 py-3 bg-red-600 hover:bg-red-500 rounded-lg text-sm font-medium transition-colors"
          >
            Stop
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="px-4 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            Send
          </button>
        )}
      </div>
    </div>
  )
}
