import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { recurringApi, categoriesApi, type RecurringExpense, type Category } from '../api/client'
import { formatCurrency, formatDate } from '../lib/utils'
import { Plus, Trash2, X, RefreshCw, Pause, Play } from 'lucide-react'

export function RecurringPage() {
  const { user } = useAuth()
  const [items, setItems] = useState<RecurringExpense[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ amount: '', category: '', description: '', frequency: 'monthly', next_date: '' })
  const [loading, setLoading] = useState(true)

  const load = () => {
    recurringApi.list({ staff_id: user?.staff_id }).then(setItems).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [user])
  useEffect(() => { categoriesApi.list().then(setCategories) }, [])

  const handleAdd = async () => {
    if (!user || !form.amount || !form.category) return
    await recurringApi.create({
      staff_id: user.staff_id,
      amount: parseFloat(form.amount),
      category: form.category,
      description: form.description,
      frequency: form.frequency,
      next_date: form.next_date || undefined,
    })
    setForm({ amount: '', category: '', description: '', frequency: 'monthly', next_date: '' })
    setShowAdd(false)
    load()
  }

  const handleToggle = async (id: number) => {
    await recurringApi.toggle(id)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this recurring expense?')) return
    await recurringApi.delete(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="page-header">
          <h1 className="page-title">Recurring Expenses</h1>
          <p className="page-description">Manage your recurring subscriptions and bills</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="btn-primary">
          <Plus className="h-4 w-4" /> Add Recurring
        </button>
      </div>

      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card w-full max-w-lg mx-4">
            <div className="card-header">
              <h3 className="card-title">New Recurring Expense</h3>
              <button onClick={() => setShowAdd(false)} className="btn-ghost btn-sm p-1.5"><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Amount</label>
                  <input type="number" step="0.01" className="input" placeholder="0.00" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
                </div>
                <div>
                  <label className="label">Category</label>
                  <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
                    <option value="">Select...</option>
                    {categories.map((c) => <option key={c.id} value={c.name}>{c.name}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Description</label>
                <input className="input" placeholder="Netflix, rent, etc." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Frequency</label>
                  <select className="input" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="biweekly">Biweekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
                <div>
                  <label className="label">Next Date</label>
                  <input type="date" className="input" value={form.next_date} onChange={(e) => setForm({ ...form, next_date: e.target.value })} />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary">Cancel</button>
                <button onClick={handleAdd} className="btn-primary">Create</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex h-40 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
        </div>
      ) : items.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-16 text-center">
          <RefreshCw className="h-12 w-12 text-gray-300 dark:text-gray-600" />
          <h3 className="mt-4 text-lg font-semibold">No recurring expenses</h3>
          <p className="mt-1 text-sm text-gray-500">Set up subscriptions and bills to track automatically</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <div key={item.id} className="card group relative">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">{item.description || item.category}</h4>
                    {item.is_active ? (
                      <span className="badge-green">Active</span>
                    ) : (
                      <span className="badge-yellow">Paused</span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-gray-500">{item.category} &middot; {item.frequency}</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold">{formatCurrency(item.amount)}</div>
                  <div className="text-xs text-gray-400">Next: {formatDate(item.next_date)}</div>
                </div>
              </div>
              <div className="mt-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={() => handleToggle(item.id)} className="btn-secondary btn-sm flex-1">
                  {item.is_active ? <><Pause className="h-3.5 w-3.5" /> Pause</> : <><Play className="h-3.5 w-3.5" /> Resume</>}
                </button>
                <button onClick={() => handleDelete(item.id)} className="btn-ghost btn-sm p-1.5 text-red-500 hover:text-red-700">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
