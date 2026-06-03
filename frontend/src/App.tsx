import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './store/auth'
import { ThemeProvider } from './store/theme'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/Login'
import { RegisterPage } from './pages/Register'
import { DashboardPage } from './pages/Dashboard'
import { ExpensesPage } from './pages/Expenses'
import { CategoriesPage } from './pages/Categories'
import { StaffPage } from './pages/Staff'
import { RecurringPage } from './pages/Recurring'
import { GamificationPage } from './pages/Gamification'
import { AnalyticsPage } from './pages/Analytics'
import { InsightsPage } from './pages/Insights'
import { SettingsPage } from './pages/Settings'

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={<Layout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/expenses" element={<ExpensesPage />} />
              <Route path="/categories" element={<CategoriesPage />} />
              <Route path="/staff" element={<StaffPage />} />
              <Route path="/recurring" element={<RecurringPage />} />
              <Route path="/gamification" element={<GamificationPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/insights" element={<InsightsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
