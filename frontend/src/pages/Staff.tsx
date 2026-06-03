import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { staffApi, type Staff } from '../api/client'
import { Plus, Trash2, X, User, Mail, Building } from 'lucide-react'

export function StaffPage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [staffList, setStaffList] = useState<Staff[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ name: '', department: '', email: '' })
  const [loading, setLoading] = useState(true)

  const load = () => staffApi.list().then(setStaffList).finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const handleAdd = async () => {
    if (!form.name) return
    await staffApi.create(form)
    setForm({ name: '', department: '', email: '' })
    setShowAdd(false)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Remove this staff member?')) return
    await staffApi.delete(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="page-header">
          <h1 className="page-title">Staff</h1>
          <p className="page-description">Manage team members</p>
        </div>
        {isAdmin && (
          <button onClick={() => setShowAdd(true)} className="btn-primary">
            <Plus className="h-4 w-4" /> Add Staff
          </button>
        )}
      </div>

      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card w-full max-w-md mx-4">
            <div className="card-header">
              <h3 className="card-title">Add Staff Member</h3>
              <button onClick={() => setShowAdd(false)} className="btn-ghost btn-sm p-1.5"><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="label">Full Name</label>
                <input className="input" placeholder="John Doe" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} autoFocus />
              </div>
              <div>
                <label className="label">Department</label>
                <input className="input" placeholder="Engineering" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
              </div>
              <div>
                <label className="label">Email</label>
                <input type="email" className="input" placeholder="john@company.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary">Cancel</button>
                <button onClick={handleAdd} className="btn-primary">Add Member</button>
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
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Email</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {staffList.map((s) => (
                <tr key={s.id}>
                  <td>
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/20 dark:text-brand-400">
                        <User className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="font-medium">{s.name}</div>
                        {s.id === user?.staff_id && <div className="text-[10px] text-gray-400">You</div>}
                      </div>
                    </div>
                  </td>
                  <td className="text-gray-500">{s.department || '-'}</td>
                  <td className="text-gray-500">{s.email || '-'}</td>
                  <td className="text-right">
                    {isAdmin && s.id !== user?.staff_id && (
                      <button onClick={() => handleDelete(s.id)} className="btn-ghost btn-sm p-1.5 text-red-500 hover:text-red-700">
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
