import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { expensesApi, categoriesApi, type Expense, type Category } from '../api/client'
import { formatCurrency, formatDate } from '../lib/utils'
import { Plus, Search, Trash2, Edit3, X } from 'lucide-react'

export function ExpensesPage() {
  const { user } = useAuth()
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  const [form, setForm] = useState({ amount: '', category: '', description: '', expense_date: '' })

  const load = () => {
    expensesApi.list({
      search: search || undefined,
      category: filterCategory || undefined,
      limit: 50,
    }).then(setExpenses).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [search, filterCategory])
  useEffect(() => { categoriesApi.list().then(setCategories) }, [])

  const handleAdd = async () => {
    if (!user || !form.amount || !form.category) return
    await expensesApi.create({
      staff_id: user.staff_id,
      amount: parseFloat(form.amount),
      category: form.category,
      description: form.description,
      expense_date: form.expense_date || undefined,
    })
    setForm({ amount: '', category: '', description: '', expense_date: '' })
    setShowAdd(false)
    load()
  }

  const handleUpdate = async () => {
    if (!editingId) return
    await expensesApi.update(editingId, {
      amount: form.amount ? parseFloat(form.amount) : undefined,
      category: form.category || undefined,
      description: form.description || undefined,
    })
    setEditingId(null)
    setForm({ amount: '', category: '', description: '', expense_date: '' })
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this expense?')) return
    await expensesApi.delete(id)
    load()
  }

  const startEdit = (e: Expense) => {
    setEditingId(e.id)
    setForm({ amount: String(e.amount), category: e.category, description: e.description, expense_date: e.expense_date })
    setShowAdd(true)
  }

  const resetForm = () => {
    setShowAdd(false)
    setEditingId(null)
    setForm({ amount: '', category: '', description: '', expense_date: '' })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="page-header">
          <h1 className="page-title">Expenses</h1>
          <p className="page-description">Track and manage all your expenses</p>
        </div>
        <button onClick={() => { resetForm(); setShowAdd(true) }} className="btn-primary">
          <Plus className="h-4 w-4" /> Add Expense
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            className="input pl-9"
            placeholder="Search expenses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input max-w-[200px]"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.name}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Add/Edit Form Modal */}
      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card w-full max-w-lg mx-4">
            <div className="card-header">
              <h3 className="card-title">{editingId ? 'Edit Expense' : 'New Expense'}</h3>
              <button onClick={resetForm} className="btn-ghost btn-sm p-1.5"><X className="h-4 w-4" /></button>
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
                <input className="input" placeholder="What was this expense for?" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </div>
              <div>
                <label className="label">Date</label>
                <input type="date" className="input" value={form.expense_date} onChange={(e) => setForm({ ...form, expense_date: e.target.value })} />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button onClick={resetForm} className="btn-secondary">Cancel</button>
                <button onClick={editingId ? handleUpdate : handleAdd} className="btn-primary">
                  {editingId ? 'Save Changes' : 'Add Expense'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Description</th>
              <th>Payment</th>
              <th className="text-right">Amount</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Loading...</td></tr>
            ) : expenses.length === 0 ? (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">No expenses found</td></tr>
            ) : (
              expenses.map((e) => (
                <tr key={e.id}>
                  <td className="text-gray-500">{formatDate(e.expense_date)}</td>
                  <td><span className="badge-purple">{e.category}</span></td>
                  <td className="max-w-[200px] truncate">{e.description || '-'}</td>
                  <td className="text-gray-500">{e.payment_method_name || '-'}</td>
                  <td className="text-right font-semibold">{formatCurrency(e.amount)}</td>
                  <td className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button onClick={() => startEdit(e)} className="btn-ghost btn-sm p-1.5"><Edit3 className="h-3.5 w-3.5" /></button>
                      <button onClick={() => handleDelete(e.id)} className="btn-ghost btn-sm p-1.5 text-red-500 hover:text-red-700"><Trash2 className="h-3.5 w-3.5" /></button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
