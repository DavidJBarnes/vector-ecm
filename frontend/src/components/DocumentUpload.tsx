import { useState, useRef, type DragEvent, type ChangeEvent } from 'react'

interface Props {
  onUpload: (file: File) => Promise<void>
  uploading: boolean
}

export default function DocumentUpload({ onUpload, uploading }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)

  const handleDragEnter = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(true)
  }

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)
  }

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) setFile(selected)
  }

  const handleSubmit = async () => {
    if (!file) return
    try {
      await onUpload(file)
      setFile(null)
      if (fileInput.current) fileInput.current.value = ''
    } catch {
      // handled by parent
    }
  }

  return (
    <div
      className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
        dragOver
          ? 'border-indigo-400 bg-indigo-400/10'
          : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
      }`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => fileInput.current?.click()}
    >
      <input
        ref={fileInput}
        type="file"
        accept=".txt,.md,.csv,.json,.html,.xml,.pdf"
        onChange={handleFileChange}
        className="hidden"
      />

      {file ? (
        <div className="space-y-3">
          <p className="text-gray-200 font-medium">{file.name}</p>
          <p className="text-gray-400 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
          <button
            onClick={(e) => { e.stopPropagation(); handleSubmit() }}
            disabled={uploading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            {uploading ? 'Uploading...' : 'Upload & Index'}
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-gray-300 font-medium">Drop a file here</p>
          <p className="text-gray-500 text-sm">or click to browse</p>
          <p className="text-gray-600 text-xs">TXT, MD, CSV, JSON, HTML, XML, PDF</p>
        </div>
      )}
    </div>
  )
}
