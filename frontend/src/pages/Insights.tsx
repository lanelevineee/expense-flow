import { useState } from 'react'
import { api } from '../api/client'
import { Sparkles, Send, Loader2, AlertCircle } from 'lucide-react'

export function InsightsPage() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!query.trim() || loading) return
    setLoading(true)
    setError('')
    setResponse('')
    try {
      const data = await api.post<{ response: string }>('/reports/ai-insight', { query: query.trim() })
      setResponse(data.response)
    } catch (err: any) {
      setError(err?.detail || 'Failed to get insight. Make sure your AI API key is configured in Settings.')
    } finally {
      setLoading(false)
    }
  }

  const suggestions = [
    'Where am I spending the most money?',
    'What are my top 3 expense categories?',
    'How can I reduce my monthly expenses?',
    'Show me spending trends over time',
    'Compare my spending to last month',
  ]

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">AI Insights</h1>
        <p className="page-description">Ask AI to analyze your spending patterns</p>
      </div>

      {/* Chat Interface */}
      <div className="card">
        <div className="flex flex-col">
          {/* Response area */}
          <div className="min-h-[300px] max-h-[500px] overflow-y-auto p-6">
            {!response && !loading && !error ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 dark:bg-brand-500/10">
                  <Sparkles className="h-8 w-8 text-brand-600 dark:text-brand-400" />
                </div>
                <h3 className="mt-6 text-lg font-semibold">Ask about your expenses</h3>
                <p className="mt-2 max-w-md text-sm text-gray-500">
                  Get AI-powered insights about your spending habits, trends, and recommendations.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => { setQuery(s); }}
                      className="rounded-full border px-3 py-1.5 text-xs text-gray-600 transition-colors hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : error ? (
              <div className="rounded-lg bg-red-50 p-4 dark:bg-red-500/10">
                <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  <span className="text-sm">{error}</span>
                </div>
              </div>
            ) : loading ? (
              <div className="flex flex-col items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
                <p className="mt-4 text-sm text-gray-500">Analyzing your expenses...</p>
              </div>
            ) : (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <div className="rounded-lg bg-brand-50/50 p-4 dark:bg-brand-500/5">
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{response}</p>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex gap-3">
              <input
                className="input flex-1"
                placeholder="Ask about your spending..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                disabled={loading}
              />
              <button onClick={handleSubmit} className="btn-primary" disabled={loading || !query.trim()}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
