import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { analyticsApi, expensesApi, gamificationApi, type AnalyticsOverview, type Expense } from '../api/client'
import { formatCurrency, formatDate } from '../lib/utils'
import { DollarSign, TrendingUp, Receipt, BarChart3, ArrowUpRight, ArrowDownRight, Trophy, Flame, Star } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe', '#4f46e5', '#7c3aed']

export function DashboardPage() {
  const { user } = useAuth()
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null)
  const [recentExpenses, setRecentExpenses] = useState<Expense[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    Promise.all([
      analyticsApi.overview({ staff_id: user.role !== 'admin' ? user.staff_id : undefined }),
      expensesApi.list({ limit: 8 }),
      gamificationApi.stats(user.staff_id),
    ]).then(([ov, ex, gs]) => {
      setOverview(ov)
      setRecentExpenses(ex)
      setStats(gs)
    }).finally(() => setLoading(false))
  }, [user])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    )
  }

  const overall = overview?.overall
  const monthlyData = overview?.monthly?.map((m) => ({
    name: m.month,
    amount: m.total,
    count: m.count,
  })).reverse() || []

  const categoryData = overview?.categories?.map((c) => ({
    name: c.category,
    value: c.total,
    count: c.count,
  })) || []

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">Welcome back, {user?.name}. Here's your expense overview.</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <span className="stat-label">Total Expenses</span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 dark:bg-brand-500/10">
              <Receipt className="h-5 w-5 text-brand-600 dark:text-brand-400" />
            </div>
          </div>
          <div className="stat-value">{overall?.total_expenses || 0}</div>
          <div className="flex items-center gap-1 text-xs text-emerald-600">
            <ArrowUpRight className="h-3 w-3" />
            <span>All time</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center justify-between">
            <span className="stat-label">Total Spent</span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-500/10">
              <DollarSign className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            </div>
          </div>
          <div className="stat-value">{formatCurrency(overall?.total_amount || 0)}</div>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <TrendingUp className="h-3 w-3" />
            <span>Avg {formatCurrency(overall?.avg_amount || 0)}/expense</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center justify-between">
            <span className="stat-label">Current Level</span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 dark:bg-amber-500/10">
              <Star className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <div className="stat-value">Lv. {stats?.level || 1}</div>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <span>{stats?.xp || 0} XP earned</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center justify-between">
            <span className="stat-label">Current Streak</span>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50 dark:bg-orange-500/10">
              <Flame className="h-5 w-5 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
          <div className="stat-value">{stats?.current_streak || 0} days</div>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <span>Best: {stats?.longest_streak || 0} days</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Spending Over Time */}
        <div className="card lg:col-span-2">
          <div className="card-header">
            <h3 className="card-title">Spending Trend</h3>
            <span className="badge-blue">Monthly</span>
          </div>
          <div className="h-[300px]">
            {monthlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthlyData}>
                  <defs>
                    <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
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
                  <Area type="monotone" dataKey="amount" stroke="#6366f1" strokeWidth={2} fill="url(#colorAmount)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-gray-400">
                No data yet. Record your first expense!
              </div>
            )}
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">By Category</h3>
          </div>
          <div className="h-[200px]">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {categoryData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
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
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-gray-400">
                No categories yet
              </div>
            )}
          </div>
          <div className="mt-2 space-y-2">
            {categoryData.slice(0, 5).map((c, i) => (
              <div key={c.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="truncate">{c.name}</span>
                </div>
                <span className="font-medium">{formatCurrency(c.value)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Expenses Table */}
      <div className="table-container">
        <div className="flex items-center justify-between px-4 py-3">
          <h3 className="card-title">Recent Expenses</h3>
          <a href="/expenses" className="text-sm font-medium text-brand-600 hover:text-brand-700">View all</a>
        </div>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Description</th>
              <th>Payment</th>
              <th className="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {recentExpenses.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center text-gray-400 py-8">
                  No expenses recorded yet
                </td>
              </tr>
            ) : (
              recentExpenses.map((exp) => (
                <tr key={exp.id}>
                  <td className="text-gray-500">{formatDate(exp.expense_date)}</td>
                  <td>
                    <span className="badge-purple">{exp.category}</span>
                  </td>
                  <td className="max-w-[200px] truncate text-gray-600 dark:text-gray-300">{exp.description || '-'}</td>
                  <td className="text-gray-500">{exp.payment_method_name || '-'}</td>
                  <td className="text-right font-semibold">{formatCurrency(exp.amount)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
