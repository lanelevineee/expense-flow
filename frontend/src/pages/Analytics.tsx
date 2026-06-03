import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { analyticsApi, type AnalyticsOverview } from '../api/client'
import { formatCurrency } from '../lib/utils'
import { BarChart3, TrendingUp, DollarSign, Hash } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#4f46e5', '#7c3aed', '#5b21b6']

export function AnalyticsPage() {
  const { user } = useAuth()
  const [data, setData] = useState<AnalyticsOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    analyticsApi.overview({ staff_id: user.role !== 'admin' ? user.staff_id : undefined })
      .then(setData)
      .finally(() => setLoading(false))
  }, [user])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    )
  }

  const monthlyData = data?.monthly?.map((m) => ({
    name: m.month,
    amount: m.total,
    count: m.count,
    avg: m.avg,
  })).reverse() || []

  const categoryData = data?.categories?.map((c, i) => ({
    name: c.category,
    value: c.total,
    count: c.count,
    budget: c.budget,
    fill: COLORS[i % COLORS.length],
  })) || []

  const overall = data?.overall

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-description">Visual breakdown of your spending patterns</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 dark:bg-brand-500/10">
            <Hash className="h-5 w-5 text-brand-600" />
          </div>
          <div className="stat-value">{overall?.total_expenses || 0}</div>
          <div className="stat-label">Total Expenses</div>
        </div>
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-500/10">
            <DollarSign className="h-5 w-5 text-emerald-600" />
          </div>
          <div className="stat-value">{formatCurrency(overall?.total_amount || 0)}</div>
          <div className="stat-label">Total Spent</div>
        </div>
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-500/10">
            <TrendingUp className="h-5 w-5 text-blue-600" />
          </div>
          <div className="stat-value">{formatCurrency(overall?.avg_amount || 0)}</div>
          <div className="stat-label">Average Expense</div>
        </div>
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 dark:bg-amber-500/10">
            <BarChart3 className="h-5 w-5 text-amber-600" />
          </div>
          <div className="stat-value">{formatCurrency(overall?.max_amount || 0)}</div>
          <div className="stat-label">Largest Expense</div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Monthly Bar Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Monthly Spending</h3>
          </div>
          <div className="h-[350px]">
            {monthlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(17, 24, 39, 0.95)',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#f3f4f6',
                      fontSize: '12px',
                    }}
                    formatter={(value: number) => [formatCurrency(value), 'Amount']}
                  />
                  <Bar dataKey="amount" fill="#6366f1" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-gray-400">No data</div>
            )}
          </div>
        </div>

        {/* Category Pie Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Category Distribution</h3>
          </div>
          <div className="h-[350px]">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {categoryData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(17, 24, 39, 0.95)',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#f3f4f6',
                      fontSize: '12px',
                    }}
                    formatter={(value: number) => [formatCurrency(value), 'Total']}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-gray-400">No data</div>
            )}
          </div>
        </div>
      </div>

      {/* Category Table */}
      <div className="table-container">
        <div className="px-4 py-3">
          <h3 className="card-title">Category Breakdown</h3>
        </div>
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th className="text-right">Count</th>
              <th className="text-right">Total</th>
              <th className="text-right">Average</th>
              <th className="text-right">Budget</th>
              <th className="text-right">Used %</th>
            </tr>
          </thead>
          <tbody>
            {categoryData.map((c) => {
              const pct = c.budget > 0 ? Math.round((c.value / c.budget) * 100) : 0
              return (
                <tr key={c.name}>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: c.fill }} />
                      <span className="font-medium">{c.name}</span>
                    </div>
                  </td>
                  <td className="text-right text-gray-500">{c.count}</td>
                  <td className="text-right font-semibold">{formatCurrency(c.value)}</td>
                  <td className="text-right text-gray-500">{formatCurrency(c.value / c.count)}</td>
                  <td className="text-right text-gray-500">{c.budget > 0 ? formatCurrency(c.budget) : '-'}</td>
                  <td className="text-right">
                    {c.budget > 0 ? (
                      <span className={pct > 100 ? 'badge-red' : pct > 75 ? 'badge-yellow' : 'badge-green'}>
                        {pct}%
                      </span>
                    ) : '-'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
