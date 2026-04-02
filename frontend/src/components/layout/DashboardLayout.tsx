import { Outlet, NavLink, Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Sparkles, Megaphone, Users, Building2, FileText,
  CreditCard, BarChart3, Shield, LogOut, Bell, Search, Menu, X,
  UserCircle, UserCheck,
} from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useLogout } from '@/hooks/useAuth'
import { cn } from '@/utils/cn'
import type { UserRole } from '@/types'

interface NavItem {
  to: string
  icon: React.ElementType
  label: string
  roles?: UserRole[]  // if set, only these roles see this item; undefined = all roles
}

interface NavGroup {
  title: string
  items: NavItem[]
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: 'MAIN',
    items: [
      { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    ],
  },
  {
    title: 'AI FEATURES',
    items: [
      { to: '/app/ai-insights', icon: Sparkles, label: 'AI Insights', roles: ['admin', 'manager'] },
    ],
  },
  {
    title: 'MANAGEMENT',
    items: [
      { to: '/app/campaigns', icon: Megaphone, label: 'Campaigns' },
      { to: '/app/influencers', icon: Users, label: 'Influencers', roles: ['admin', 'manager'] },
      { to: '/app/clients', icon: Building2, label: 'Clients', roles: ['admin', 'manager'] },
    ],
  },
  {
    title: 'OPERATIONS',
    items: [
      { to: '/app/contracts', icon: FileText, label: 'Contracts' },
      { to: '/app/payments', icon: CreditCard, label: 'Payments' },
      { to: '/app/analytics', icon: BarChart3, label: 'Analytics', roles: ['admin', 'manager'] },
    ],
  },
  {
    title: 'MY WORKSPACE',
    items: [
      { to: '/app/my-profile', icon: UserCheck, label: 'My Profile', roles: ['influencer'] },
    ],
  },
  {
    title: 'ADMIN',
    items: [
      { to: '/app/admin', icon: Shield, label: 'Platform Admin', roles: ['admin'] },
    ],
  },
]

const PAGE_TITLES: Record<string, string> = {
  '/app/dashboard': 'Dashboard',
  '/app/ai-insights': 'AI Insights',
  '/app/campaigns': 'Campaigns',
  '/app/influencers': 'Influencers',
  '/app/clients': 'Clients',
  '/app/contracts': 'Contracts',
  '/app/payments': 'Payments',
  '/app/analytics': 'Analytics',
  '/app/admin': 'Platform Admin',
  '/app/my-profile': 'My Profile',
  '/app/profile': 'Account Settings',
}

const ROLE_BADGE_COLORS: Record<UserRole, string> = {
  admin: 'bg-rose-400/15 text-rose-400',
  manager: 'bg-violet-400/15 text-violet-400',
  client: 'bg-cyan-400/15 text-cyan-400',
  influencer: 'bg-emerald-400/15 text-emerald-400',
}

export default function DashboardLayout() {
  const { user } = useAuthStore()
  const logout = useLogout()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const role = (user?.role ?? 'client') as UserRole

  const currentTitle = Object.entries(PAGE_TITLES).find(
    ([path]) => location.pathname.startsWith(path)
  )?.[1] ?? 'Dashboard'

  // Filter a group's items to only those the current role can see
  const visibleItems = (items: NavItem[]) =>
    items.filter((item) => !item.roles || item.roles.includes(role))

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
          const items = visibleItems(group.items)
          if (items.length === 0) return null
          return (
            <div key={group.title}>
              <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60">
                {group.title}
              </p>
              <div className="space-y-0.5">
                {items.map(({ to, icon: Icon, label }) => (
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
      <div className="px-4 py-4 border-t border-border/40 space-y-2">
        <Link
          to="/app/profile"
          onClick={() => setMobileOpen(false)}
          className="flex items-center gap-3 w-full rounded-lg px-2 py-1.5 hover:bg-muted/30 transition-colors group"
        >
          <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-sm shrink-0 group-hover:bg-primary/30 transition-colors">
            {user?.full_name?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-foreground">{user?.full_name}</p>
            <span className={cn('inline-block text-[10px] px-1.5 py-0.5 rounded-full font-medium mt-0.5', ROLE_BADGE_COLORS[role])}>
              {role}
            </span>
          </div>
          <UserCircle size={15} className="text-muted-foreground shrink-0" />
        </Link>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/5 transition-colors duration-200"
        >
          <LogOut size={15} />
          Sign out
        </button>
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
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-muted/50 text-muted-foreground"
          >
            <Menu size={20} />
          </button>

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
