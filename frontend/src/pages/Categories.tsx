import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { categoriesApi, type Category } from '../api/client'
import { formatCurrency } from '../lib/utils'
import { Plus, Trash2, X, Tag } from 'lucide-react'

const ICONS = ['food', 'transport', 'shopping', 'entertainment', 'bills', 'health', 'education', 'travel', 'other']

export function CategoriesPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [categories, setCategories] = useState<Category[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ name: '', icon: 'other', budget: '' })
  const [loading, setLoading] = useState(true)

  const load = () => categoriesApi.list().then(setCategories).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const handleAdd = async () => {
    if (!form.name) return
    await categoriesApi.create({ name: form.name, icon: form.icon, budget: form.budget ? parseFloat(form.budget) : 0 })
    setForm({ name: '', icon: 'other', budget: '' })
    setShowAdd(false)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this category?')) return
    await categoriesApi.delete(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="page-header">
          <h1 className="page-title">Categories</h1>
          <p className="page-description">Organize expenses by category</p>
        </div>
        {isAdmin && (
          <button onClick={() => setShowAdd(true)} className="btn-primary">
            <Plus className="h-4 w-4" /> Add Category
          </button>
        )}
      </div>

      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card w-full max-w-md mx-4">
            <div className="card-header">
              <h3 className="card-title">New Category</h3>
              <button onClick={() => setShowAdd(false)} className="btn-ghost btn-sm p-1.5"><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="label">Name</label>
                <input className="input" placeholder="Category name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} autoFocus />
              </div>
              <div>
                <label className="label">Icon</label>
                <div className="flex flex-wrap gap-2">
                  {ICONS.map((icon) => (
                    <button
                      key={icon}
                      onClick={() => setForm({ ...form, icon })}
                      className={`rounded-lg border px-3 py-1.5 text-xs capitalize transition-colors ${
                        form.icon === icon
                          ? 'border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="label">Monthly Budget</label>
                <input type="number" step="0.01" className="input" placeholder="0.00" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} />
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
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {categories.map((cat) => (
            <div key={cat.id} className="card group relative">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-xl dark:bg-brand-500/10">
                    <Tag className="h-6 w-6 text-brand-600 dark:text-brand-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold">{cat.name}</h4>
                    {cat.budget > 0 && (
                      <p className="text-xs text-gray-500">Budget: {formatCurrency(cat.budget)}/mo</p>
                    )}
                  </div>
                </div>
                {isAdmin && (
                  <button
                    onClick={() => handleDelete(cat.id)}
                    className="btn-ghost btn-sm p-1.5 opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
