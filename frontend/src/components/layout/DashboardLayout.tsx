import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, Megaphone, Building2, FileText,
  CreditCard, BarChart3, Bell, LogOut, Menu, X, ChevronDown,
} from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useLogout } from '@/hooks/useAuth'
import { cn } from '@/utils/cn'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/influencers', icon: Users, label: 'Influencers' },
  { to: '/campaigns', icon: Megaphone, label: 'Campaigns' },
  { to: '/clients', icon: Building2, label: 'Clients' },
  { to: '/contracts', icon: FileText, label: 'Contracts' },
  { to: '/payments', icon: CreditCard, label: 'Payments' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
]

export default function DashboardLayout() {
  const { user } = useAuthStore()
  const logout = useLogout()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside
        className={cn(
          'flex flex-col bg-card border-r border-border transition-all duration-300',
          sidebarOpen ? 'w-64' : 'w-16',
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
              O
            </div>
            {sidebarOpen && (
              <span className="font-semibold text-sm truncate">OakstrattonIMA</span>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="ml-auto p-1 rounded hover:bg-muted"
          >
            {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )
              }
            >
              <Icon size={18} className="shrink-0" />
              {sidebarOpen && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="p-3 border-t border-border">
          <div className={cn('flex items-center gap-3', !sidebarOpen && 'justify-center')}>
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm shrink-0">
              {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
              </div>
            )}
            {sidebarOpen && (
              <button
                onClick={logout}
                className="p-1 rounded hover:bg-muted text-muted-foreground hover:text-destructive"
                title="Sign out"
              >
                <LogOut size={16} />
              </button>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-16 border-b border-border bg-card flex items-center justify-end px-6 gap-4">
          <button className="relative p-2 rounded-lg hover:bg-muted text-muted-foreground">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
          </button>
          <div className="flex items-center gap-2 text-sm">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm">
              {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <span className="font-medium">{user?.full_name}</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
