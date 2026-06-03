import { useState } from 'react'
import { useAuth } from '../store/auth'
import { Link, Navigate } from 'react-router-dom'
import { Zap, Eye, EyeOff } from 'lucide-react'

export function LoginPage() {
  const { user, login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) return <Navigate to="/" replace />

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
    } catch (err: any) {
      setError(err?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left - Branding */}
      <div className="hidden w-1/2 bg-brand-600 lg:flex lg:flex-col lg:items-center lg:justify-center">
        <div className="text-center">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
            <Zap className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white">Smart Expense Tracker</h1>
          <p className="mt-3 text-lg text-brand-200">AI-powered expense management for your team</p>
          <div className="mt-8 flex items-center justify-center gap-8 text-brand-200">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">100%</div>
              <div className="text-sm">Open Source</div>
            </div>
            <div className="h-8 w-px bg-brand-400/30" />
            <div className="text-center">
              <div className="text-2xl font-bold text-white">AI</div>
              <div className="text-sm">Powered Insights</div>
            </div>
            <div className="h-8 w-px bg-brand-400/30" />
            <div className="text-center">
              <div className="text-2xl font-bold text-white">Fun</div>
              <div className="text-sm">Gamification</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right - Form */}
      <div className="flex w-full items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-md">
          <div className="mb-8 lg:hidden">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 text-white">
                <Zap className="h-5 w-5" />
              </div>
              <div>
                <div className="font-bold">Smart Expense</div>
                <div className="text-xs text-gray-500">Tracker</div>
              </div>
            </div>
          </div>

          <h2 className="text-2xl font-bold">Welcome back</h2>
          <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">
            Sign in to your account to continue
          </p>

          {error && (
            <div className="mt-4 rounded-lg bg-red-50 p-3.5 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="label">Email address</label>
              <input
                type="email"
                className="input"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
