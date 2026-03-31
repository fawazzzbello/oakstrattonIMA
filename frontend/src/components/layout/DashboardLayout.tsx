import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Sparkles, Megaphone, Users, Building2, FileText,
  CreditCard, BarChart3, Shield, LogOut, Bell, Search, Menu, X,
} from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useLogout } from '@/hooks/useAuth'
import { cn } from '@/utils/cn'

interface NavItem {
  to: string
  icon: React.ElementType
  label: string
}

interface NavGroup {
  title: string
  items: NavItem[]
  adminOnly?: boolean
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: 'MAIN',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    ],
  },
  {
    title: 'AI FEATURES',
    items: [
      { to: '/ai-insights', icon: Sparkles, label: 'AI Insights' },
    ],
  },
  {
    title: 'MANAGEMENT',
    items: [
      { to: '/campaigns', icon: Megaphone, label: 'Campaigns' },
      { to: '/influencers', icon: Users, label: 'Influencers' },
      { to: '/clients', icon: Building2, label: 'Clients' },
    ],
  },
  {
    title: 'OPERATIONS',
    items: [
      { to: '/contracts', icon: FileText, label: 'Contracts' },
      { to: '/payments', icon: CreditCard, label: 'Payments' },
      { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    ],
  },
  {
    title: 'ADMIN',
    adminOnly: true,
    items: [
      { to: '/admin', icon: Shield, label: 'Platform Admin' },
    ],
  },
]

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/ai-insights': 'AI Insights',
  '/campaigns': 'Campaigns',
  '/influencers': 'Influencers',
  '/clients': 'Clients',
  '/contracts': 'Contracts',
  '/payments': 'Payments',
  '/analytics': 'Analytics',
  '/admin': 'Platform Admin',
}

export default function DashboardLayout() {
  const { user } = useAuthStore()
  const logout = useLogout()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const currentTitle = Object.entries(PAGE_TITLES).find(
    ([path]) => location.pathname.startsWith(path)
  )?.[1] ?? 'Dashboard'

  const isAdmin = user?.role === 'admin'

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 h-16 border-b border-border/40">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-sm shrink-0">
          O
        </div>
        <span className="gradient-text font-heading font-bold text-lg truncate">
          OakstrattonIMA
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto">
        {NAV_GROUPS.map((group) => {
          if (group.adminOnly && !isAdmin) return null
          return (
            <div key={group.title}>
              <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60">
                {group.title}
              </p>
              <div className="space-y-0.5">
                {group.items.map(({ to, icon: Icon, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={() => setMobileOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                        isActive
                          ? 'border-l-2 border-primary bg-primary/10 text-foreground'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted/30',
                      )
                    }
                  >
                    <Icon size={18} className="shrink-0" />
                    <span>{label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          )
        })}
      </nav>

      {/* User section */}
      <div className="px-4 py-4 border-t border-border/40">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm shrink-0">
            {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-foreground">{user?.full_name}</p>
            <span className="status-badge bg-violet-400/10 text-violet-400 text-[10px] mt-0.5">
              {user?.role}
            </span>
          </div>
          <button
            onClick={logout}
            className="p-1.5 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-destructive transition-colors duration-200"
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-[280px] shrink-0 flex-col bg-[#070814] border-r border-border/40 h-full">
        {sidebarContent}
      </aside>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar drawer */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-[280px] bg-[#070814] border-r border-border/40 transform transition-transform duration-300 lg:hidden',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <button
          onClick={() => setMobileOpen(false)}
          className="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-muted/50 text-muted-foreground"
        >
          <X size={18} />
        </button>
        {sidebarContent}
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-16 shrink-0 border-b border-border/40 bg-card/50 backdrop-blur-sm flex items-center px-4 sm:px-6 gap-4">
          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-muted/50 text-muted-foreground"
          >
            <Menu size={20} />
          </button>

          {/* Page title */}
          <h2 className="text-lg font-heading font-semibold text-foreground hidden sm:block">
            {currentTitle}
          </h2>

          <div className="flex-1" />

          {/* Search */}
          <div className="hidden md:flex items-center gap-2 bg-muted/40 border border-border/40 rounded-lg px-3 py-1.5 w-64">
            <Search size={16} className="text-muted-foreground shrink-0" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none w-full"
            />
          </div>

          {/* Notification bell */}
          <button className="relative p-2 rounded-lg hover:bg-muted/50 text-muted-foreground transition-colors duration-200">
            <Bell size={20} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-destructive rounded-full" />
          </button>

          {/* User avatar (mobile) */}
          <div className="flex items-center gap-2 sm:hidden">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm">
              {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto aurora-bg">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
