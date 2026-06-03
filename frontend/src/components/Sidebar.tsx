import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Receipt, Tag, Users, RefreshCw, Trophy,
  BarChart3, Sparkles, Settings, ChevronLeft, ChevronRight, Zap,
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '../lib/utils'
import { useAuth } from '../store/auth'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/expenses', icon: Receipt, label: 'Expenses' },
  { to: '/categories', icon: Tag, label: 'Categories' },
  { to: '/recurring', icon: RefreshCw, label: 'Recurring' },
  { to: '/staff', icon: Users, label: 'Staff' },
  { divider: true, label: 'Engagement' },
  { to: '/gamification', icon: Trophy, label: 'Gamification' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/insights', icon: Sparkles, label: 'AI Insights' },
  { divider: true, label: 'System' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const { user } = useAuth()

  return (
    <aside
      className={cn(
        'fixed inset-y-0 left-0 z-30 flex flex-col border-r bg-white dark:bg-gray-900 transition-all duration-300',
        collapsed ? 'w-[68px]' : 'w-[260px]'
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b px-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white shrink-0">
          <Zap className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <div className="font-bold text-sm leading-tight">Smart Expense</div>
            <div className="text-[10px] text-gray-500 dark:text-gray-400 leading-tight">Tracker</div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item, i) => {
          if ('divider' in item && item.divider) {
            return !collapsed ? (
              <div key={i} className="pt-4 pb-2 px-3">
                <span className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
                  {item.label}
                </span>
              </div>
            ) : (
              <div key={i} className="py-2">
                <div className="mx-3 border-t dark:border-gray-800" />
              </div>
            )
          }
          const Icon = item.icon!
          return (
            <NavLink
              key={item.to}
              to={item.to!}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn('sidebar-link', isActive && 'active', collapsed && 'justify-center px-0')
              }
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t p-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="btn-ghost w-full"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed && <span className="text-xs">Collapse</span>}
        </button>
      </div>
    </aside>
  )
}
