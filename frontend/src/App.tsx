import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import type { UserRole } from '@/types'
import DashboardLayout from '@/components/layout/DashboardLayout'
import LandingPage from '@/pages/LandingPage'
import LoginPage from '@/pages/LoginPage'
import ForgotPasswordPage from '@/pages/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/ResetPasswordPage'
import DirectoryPage from '@/pages/DirectoryPage'
import ProfilePage from '@/pages/ProfilePage'
import DashboardPage from '@/pages/DashboardPage'
import InfluencersPage from '@/pages/InfluencersPage'
import InfluencerDetailPage from '@/pages/InfluencerDetailPage'
import CampaignsPage from '@/pages/CampaignsPage'
import CampaignDetailPage from '@/pages/CampaignDetailPage'
import ClientsPage from '@/pages/ClientsPage'
import ContractsPage from '@/pages/ContractsPage'
import PaymentsPage from '@/pages/PaymentsPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import AIInsightsPage from '@/pages/AIInsightsPage'
import AdminPage from '@/pages/AdminPage'
import MyInfluencerProfilePage from '@/pages/MyInfluencerProfilePage'
import NotFoundPage from '@/pages/NotFoundPage'

/** Redirects to /login if not authenticated. */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

/**
 * Role-gated route. Requires authentication AND the user's role to be in
 * the `roles` allowlist. Unauthorized → redirected to /app/dashboard.
 */
function RoleRoute({ roles, children }: { roles: UserRole[]; children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!roles.includes((user?.role ?? 'client') as UserRole)) {
    return <Navigate to="/app/dashboard" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* ── Public routes ─────────────────────────────────── */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/directory" element={<DirectoryPage />} />

      {/* ── Protected app shell ───────────────────────────── */}
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/app/dashboard" replace />} />

        {/* All authenticated roles */}
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="campaigns" element={<CampaignsPage />} />
        <Route path="campaigns/:id" element={<CampaignDetailPage />} />
        <Route path="contracts" element={<ContractsPage />} />
        <Route path="payments" element={<PaymentsPage />} />

        {/* Admin + Manager only */}
        <Route
          path="influencers"
          element={<RoleRoute roles={['admin', 'manager']}><InfluencersPage /></RoleRoute>}
        />
        <Route
          path="influencers/:id"
          element={<RoleRoute roles={['admin', 'manager']}><InfluencerDetailPage /></RoleRoute>}
        />
        <Route
          path="clients"
          element={<RoleRoute roles={['admin', 'manager']}><ClientsPage /></RoleRoute>}
        />
        <Route
          path="analytics"
          element={<RoleRoute roles={['admin', 'manager']}><AnalyticsPage /></RoleRoute>}
        />
        <Route
          path="ai-insights"
          element={<RoleRoute roles={['admin', 'manager']}><AIInsightsPage /></RoleRoute>}
        />

        {/* Admin only */}
        <Route
          path="admin/*"
          element={<RoleRoute roles={['admin']}><AdminPage /></RoleRoute>}
        />

        {/* Influencer only */}
        <Route
          path="my-profile"
          element={<RoleRoute roles={['influencer']}><MyInfluencerProfilePage /></RoleRoute>}
        />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
