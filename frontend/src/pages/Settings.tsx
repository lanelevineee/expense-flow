import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { settingsApi } from '../api/client'
import { useTheme } from '../store/theme'
import { Settings, CreditCard, Trash2, Plus, X, Palette, DollarSign } from 'lucide-react'

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'INR', 'BRL', 'MXN', 'GHS']

export function SettingsPage() {
  const { user } = useAuth()
  const { dark, toggle } = useTheme()
  const [currency, setCurrency] = useState('USD')
  const [budgets, setBudgets] = useState<{ name: string; budget: number }[]>([])
  const [paymentMethods, setPaymentMethods] = useState<{ id: number; name: string; type: string; is_default: boolean }[]>([])
  const [showAddPm, setShowAddPm] = useState(false)
  const [pmForm, setPmForm] = useState({ name: '', type: 'credit' })
  const [budgetForm, setBudgetForm] = useState({ category: '', amount: '' })
  const [showAddBudget, setShowAddBudget] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      settingsApi.getCurrency(),
      settingsApi.getBudgets(),
      settingsApi.getPaymentMethods(),
    ]).then(([c, b, pm]) => {
      setCurrency(c.currency)
      setBudgets(b)
      setPaymentMethods(pm)
    }).finally(() => setLoading(false))
  }, [])

  const handleCurrencyChange = async (c: string) => {
    await settingsApi.setCurrency(c)
    setCurrency(c)
  }

  const handleAddPm = async () => {
    if (!pmForm.name) return
    await settingsApi.addPaymentMethod(pmForm)
    setPmForm({ name: '', type: 'credit' })
    setShowAddPm(false)
    setPaymentMethods(await settingsApi.getPaymentMethods())
  }

  const handleDeletePm = async (id: number) => {
    await settingsApi.deletePaymentMethod(id)
    setPaymentMethods(await settingsApi.getPaymentMethods())
  }

  const handleAddBudget = async () => {
    if (!budgetForm.category || !budgetForm.amount) return
    await settingsApi.setBudget(budgetForm.category, parseFloat(budgetForm.amount))
    setBudgetForm({ category: '', amount: '' })
    setShowAddBudget(false)
    setBudgets(await settingsApi.getBudgets())
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-description">Configure your expense tracker preferences</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Appearance */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2"><Palette className="h-5 w-5" /> Appearance</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium">Dark Mode</div>
                <div className="text-xs text-gray-500">Toggle between light and dark theme</div>
              </div>
              <button
                onClick={toggle}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  dark ? 'bg-brand-600' : 'bg-gray-200'
                }`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  dark ? 'translate-x-6' : 'translate-x-1'
                }`} />
              </button>
            </div>
          </div>
        </div>

        {/* Currency */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2"><DollarSign className="h-5 w-5" /> Currency</h3>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {CURRENCIES.map((c) => (
              <button
                key={c}
                onClick={() => handleCurrencyChange(c)}
                className={`rounded-lg border p-2.5 text-sm font-medium transition-all ${
                  currency === c
                    ? 'border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Payment Methods */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2"><CreditCard className="h-5 w-5" /> Payment Methods</h3>
            <button onClick={() => setShowAddPm(true)} className="btn-primary btn-sm">
              <Plus className="h-3.5 w-3.5" /> Add
            </button>
          </div>
          {showAddPm && (
            <div className="mb-4 rounded-lg border p-3">
              <div className="flex gap-3">
                <input className="input flex-1" placeholder="Name (e.g. Visa)" value={pmForm.name} onChange={(e) => setPmForm({ ...pmForm, name: e.target.value })} autoFocus />
                <select className="input w-32" value={pmForm.type} onChange={(e) => setPmForm({ ...pmForm, type: e.target.value })}>
                  <option value="credit">Credit</option>
                  <option value="debit">Debit</option>
                  <option value="cash">Cash</option>
                  <option value="bank">Bank</option>
                </select>
                <button onClick={handleAddPm} className="btn-primary btn-sm">Save</button>
                <button onClick={() => setShowAddPm(false)} className="btn-ghost btn-sm p-1.5"><X className="h-4 w-4" /></button>
              </div>
            </div>
          )}
          <div className="space-y-2">
            {paymentMethods.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">No payment methods</p>
            ) : (
              paymentMethods.map((pm) => (
                <div key={pm.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <div className="text-sm font-medium">{pm.name}</div>
                    <div className="text-xs text-gray-500 capitalize">{pm.type}{pm.is_default ? ' (default)' : ''}</div>
                  </div>
                  <button onClick={() => handleDeletePm(pm.id)} className="btn-ghost btn-sm p-1.5 text-red-500">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Budgets */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2"><Settings className="h-5 w-5" /> Category Budgets</h3>
            <button onClick={() => setShowAddBudget(true)} className="btn-primary btn-sm">
              <Plus className="h-3.5 w-3.5" /> Set Budget
            </button>
          </div>
          {showAddBudget && (
            <div className="mb-4 rounded-lg border p-3">
              <div className="flex gap-3">
                <input className="input flex-1" placeholder="Category name" value={budgetForm.category} onChange={(e) => setBudgetForm({ ...budgetForm, category: e.target.value })} autoFocus />
                <input type="number" step="0.01" className="input w-32" placeholder="Amount" value={budgetForm.amount} onChange={(e) => setBudgetForm({ ...budgetForm, amount: e.target.value })} />
                <button onClick={handleAddBudget} className="btn-primary btn-sm">Save</button>
                <button onClick={() => setShowAddBudget(false)} className="btn-ghost btn-sm p-1.5"><X className="h-4 w-4" /></button>
              </div>
            </div>
          )}
          <div className="space-y-2">
            {budgets.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">No budgets set</p>
            ) : (
              budgets.map((b) => (
                <div key={b.name} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="text-sm font-medium">{b.name}</div>
                  <div className="text-sm font-semibold">${b.budget.toFixed(2)}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
