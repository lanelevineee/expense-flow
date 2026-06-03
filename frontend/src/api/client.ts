const API_BASE = '/api'

interface RequestOptions extends RequestInit {
  token?: string
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('token')
  }

  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { token, ...fetchOptions } = options
    const authToken = token || this.getToken()

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(fetchOptions.headers as Record<string, string>),
    }

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...fetchOptions,
      headers,
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw { status: res.status, ...body }
    }

    return res.json()
  }

  async get<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
    let url = path
    if (params) {
      const qs = new URLSearchParams()
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') qs.set(k, String(v))
      })
      const str = qs.toString()
      if (str) url += `?${str}`
    }
    return this.request<T>(url, { method: 'GET' })
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' })
  }
}

export const api = new ApiClient()

// Auth
export const authApi = {
  login: (email: string, password: string, totpCode?: string, emailOtp?: string) =>
    api.post<{ access_token: string; refresh_token: string; staff_id: number; name: string; role: string }>(
      '/auth/login',
      { email, password, totp_code: totpCode, email_otp: emailOtp }
    ),
  register: (name: string, email: string, password: string, department?: string) =>
    api.post<{ access_token: string; refresh_token: string; staff_id: number; name: string; role: string }>(
      '/auth/register',
      { name, email, password, department: department || '' }
    ),
  me: () => api.get<{ staff_id: number; role: string; name: string; department: string }>('/auth/me'),
  refresh: (refreshToken: string) =>
    api.post<{ access_token: string; refresh_token: string }>('/auth/refresh', { refresh_token: refreshToken }),
}

// Expenses
export interface Expense {
  id: number
  staff_id: number
  amount: number
  category: string
  description: string
  payment_method_id: number | null
  payment_method_name: string
  expense_date: string
  created_at: string
}

export const expensesApi = {
  list: (params?: { staff_id?: number; category?: string; search?: string; sort_by?: string; limit?: number }) =>
    api.get<Expense[]>('/expenses/', params as Record<string, string | number>),
  create: (data: { staff_id: number; amount: number; category: string; description?: string; expense_date?: string; payment_method_id?: number }) =>
    api.post<{ id: number }>('/expenses/', data),
  update: (id: number, data: { amount?: number; category?: string; description?: string; payment_method_id?: number }) =>
    api.put<{ success: boolean }>(`/expenses/${id}`, data),
  delete: (id: number) => api.delete<{ success: boolean }>(`/expenses/${id}`),
}

// Categories
export interface Category {
  id: number
  name: string
  icon: string
  color: string
  budget: number
}

export const categoriesApi = {
  list: () => api.get<Category[]>('/categories/'),
  create: (data: { name: string; icon?: string; budget?: number }) =>
    api.post<{ id: number; name: string }>('/categories/', data),
  update: (id: number, data: { icon?: string; budget?: number }) =>
    api.put<{ success: boolean }>(`/categories/${id}`, data),
  delete: (id: number) => api.delete<{ success: boolean }>(`/categories/${id}`),
}

// Staff
export interface Staff {
  id: number
  name: string
  department: string
  email: string
}

export const staffApi = {
  list: () => api.get<Staff[]>('/staff/'),
  get: (id: number) => api.get<Staff>(`/staff/${id}`),
  create: (data: { name: string; department?: string; email?: string }) =>
    api.post<{ id: number; name: string }>('/staff/', data),
  update: (id: number, data: { name?: string; department?: string; email?: string }) =>
    api.put<{ success: boolean }>(`/staff/${id}`, data),
  delete: (id: number) => api.delete<{ success: boolean }>(`/staff/${id}`),
}

// Recurring
export interface RecurringExpense {
  id: number
  staff_id: number
  amount: number
  category: string
  description: string
  frequency: string
  next_date: string
  is_active: boolean
}

export const recurringApi = {
  list: (params?: { staff_id?: number }) =>
    api.get<RecurringExpense[]>('/recurring/', params as Record<string, string | number>),
  create: (data: { staff_id: number; amount: number; category: string; description?: string; frequency?: string; next_date?: string }) =>
    api.post<{ id: number }>('/recurring/', data),
  delete: (id: number) => api.delete<{ success: boolean }>(`/recurring/${id}`),
  toggle: (id: number) => api.post<{ success: boolean }>(`/recurring/${id}/toggle`),
}

// Analytics
export interface AnalyticsOverview {
  overall: { total_expenses: number; total_amount: number; avg_amount: number; min_amount: number; max_amount: number }
  categories: { category: string; count: number; total: number; avg: number; budget: number }[]
  monthly: { month: string; total: number; count: number; avg: number }[]
}

export const analyticsApi = {
  overview: (params?: { staff_id?: number }) =>
    api.get<AnalyticsOverview>('/analytics/overview', params as Record<string, string | number>),
}

// Gamification
export interface GamificationStats {
  xp: number
  level: number
  current_streak: number
  longest_streak: number
  total_expenses: number
  days_active: number
  total_achievements: number
}

export interface Achievement {
  id: number
  name: string
  description: string
  icon: string
  xp_reward: number
}

export interface LeaderboardEntry {
  staff_id: number
  name: string
  xp: number
  level: number
}

export interface Challenge {
  id: number
  title: string
  description: string
  goal_type: string
  goal_value: number
  xp_reward: number
  ends_at: string
}

export const gamificationApi = {
  stats: (staffId: number) => api.get<GamificationStats>(`/gamification/stats/${staffId}`),
  achievements: () => api.get<Achievement[]>('/gamification/achievements'),
  myAchievements: (staffId: number) => api.get<{ name: string; description: string; icon: string; earned_at: string }[]>(`/gamification/achievements/${staffId}`),
  leaderboard: () => api.get<LeaderboardEntry[]>('/gamification/leaderboard'),
  challenges: () => api.get<Challenge[]>('/gamification/challenges'),
}

// Settings
export const settingsApi = {
  getCurrency: () => api.get<{ currency: string }>('/settings/currency'),
  setCurrency: (currency: string) => api.put<{ success: boolean }>('/settings/currency', { currency }),
  getTheme: () => api.get<{ theme: string }>('/settings/theme'),
  setTheme: (theme: string) => api.put<{ success: boolean }>('/settings/theme', { theme }),
  getBudgets: () => api.get<{ name: string; budget: number }[]>('/settings/budgets'),
  setBudget: (category: string, amount: number) => api.put<{ success: boolean }>('/settings/budgets', { category, amount }),
  getPaymentMethods: () => api.get<{ id: number; name: string; type: string; is_default: boolean }[]>('/settings/payment-methods'),
  addPaymentMethod: (data: { name: string; type?: string; is_default?: boolean }) =>
    api.post<{ id: number }>('/settings/payment-methods', data),
  deletePaymentMethod: (id: number) => api.delete<{ success: boolean }>(`/settings/payment-methods/${id}`),
}
