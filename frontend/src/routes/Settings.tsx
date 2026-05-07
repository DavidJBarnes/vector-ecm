import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import type { Settings as SettingsType } from '../types'

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    api.getSettings()
      .then(setSettings)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const handleChange = useCallback((field: keyof SettingsType, value: string | number) => {
    setSettings((prev) => prev ? { ...prev, [field]: value } : prev)
  }, [])

  const handleSave = useCallback(async () => {
    if (!settings) return
    setSaving(true)
    setError(null)
    setSuccess(false)
    try {
      const updated = await api.updateSettings(settings)
      setSettings(updated)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }, [settings])

  if (loading) {
    return <p className="text-gray-400 py-8 text-center">Loading settings...</p>
  }

  if (!settings) {
    return (
      <div className="p-3 rounded-lg bg-red-900/30 border border-red-800 text-red-300 text-sm">
        {error || 'Failed to load settings'}
      </div>
    )
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Settings</h2>
        <p className="text-gray-400 text-sm mt-1">
          Configure AI provider settings. These override environment defaults at runtime.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-900/30 border border-red-800 text-red-300 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {success && (
        <div className="p-3 rounded-lg bg-green-900/30 border border-green-800 text-green-300 text-sm">
          Settings saved successfully.
        </div>
      )}

      <section>
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">API Connection</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1">API Key</label>
            <input
              type="password"
              value={settings.api_key}
              onChange={(e) => handleChange('api_key', e.target.value)}
              placeholder="sk-..."
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Base URL</label>
            <input
              type="text"
              value={settings.base_url}
              onChange={(e) => handleChange('base_url', e.target.value)}
              placeholder="https://api.deepseek.com"
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Chat Model</label>
            <input
              type="text"
              value={settings.chat_model}
              onChange={(e) => handleChange('chat_model', e.target.value)}
              placeholder="deepseek-chat"
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
            />
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">Generation</h3>
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm text-gray-300 mb-1">Temperature</label>
              <input
                type="number"
                value={settings.temperature}
                onChange={(e) => handleChange('temperature', parseFloat(e.target.value) || 0)}
                min={0}
                max={2}
                step={0.1}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 focus:outline-none focus:border-indigo-500 text-sm"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-300 mb-1">Max Tokens</label>
              <input
                type="number"
                value={settings.max_tokens}
                onChange={(e) => handleChange('max_tokens', parseInt(e.target.value) || 0)}
                min={1}
                max={16384}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 focus:outline-none focus:border-indigo-500 text-sm"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-300 mb-1">Top-K (RAG)</label>
              <input
                type="number"
                value={settings.top_k}
                onChange={(e) => handleChange('top_k', parseInt(e.target.value) || 1)}
                min={1}
                max={50}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 focus:outline-none focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">System Prompt</h3>
        <textarea
          value={settings.system_prompt}
          onChange={(e) => handleChange('system_prompt', e.target.value)}
          rows={4}
          placeholder="Custom system prompt for the AI..."
          className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm resize-none"
        />
      </section>

      <button
        onClick={handleSave}
        disabled={saving}
        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
      >
        {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  )
}
