import { useAuth } from '../store/auth'
import { useTheme } from '../store/theme'
import { Moon, Sun, Bell, LogOut, User } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const { user, logout } = useAuth()
  const { dark, toggle } = useTheme()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-white/80 px-6 backdrop-blur-md dark:bg-gray-900/80">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-medium text-gray-500 dark:text-gray-400">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </h1>
      </div>

      <div className="flex items-center gap-2">
        <button onClick={toggle} className="btn-ghost btn-sm rounded-full p-2">
          {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <button className="btn-ghost btn-sm relative rounded-full p-2">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
        </button>

        <div className="relative ml-2">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-2 rounded-lg p-1.5 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/20 dark:text-brand-400">
              <User className="h-4 w-4" />
            </div>
            <div className="hidden text-left sm:block">
              <div className="text-sm font-medium">{user?.name}</div>
              <div className="text-[10px] text-gray-500 dark:text-gray-400 capitalize">{user?.role}</div>
            </div>
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 top-full z-50 mt-2 w-48 rounded-xl border bg-white py-1.5 shadow-lg dark:bg-gray-900">
                <div className="border-b px-4 py-2.5">
                  <div className="text-sm font-medium">{user?.name}</div>
                  <div className="text-xs text-gray-500">{user?.role === 'admin' ? 'Administrator' : 'Staff Member'}</div>
                </div>
                <button
                  onClick={logout}
                  className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
