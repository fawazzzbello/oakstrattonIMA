import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import type { User, TokenResponse } from '@/types'

/** Returns the post-login redirect path based on user role. */
function roleRedirect(role: string): string {
  if (role === 'influencer') return '/app/my-profile'
  return '/app/dashboard'
}

export function useRegister() {
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (data: { email: string; password: string; full_name: string }) => {
      const { data: tokens } = await api.post<TokenResponse>('/auth/register', data)
      return { tokens, email: data.email }
    },
    onSuccess: async ({ tokens }) => {
      try {
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)
        const { data: user } = await api.get<User>('/auth/me')
        setAuth(user, tokens.access_token, tokens.refresh_token)
        navigate(roleRedirect(user.role))
      } catch {
        setAuth(
          { id: 0, email: '', full_name: '', role: 'client' } as User,
          tokens.access_token,
          tokens.refresh_token,
        )
        navigate('/app/dashboard')
      }
    },
  })
}

export function useLogin() {
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const { data } = await api.post<TokenResponse>('/auth/login', credentials)
      return data
    },
    onSuccess: async (tokens) => {
      try {
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)
        const { data: user } = await api.get<User>('/auth/me')
        setAuth(user, tokens.access_token, tokens.refresh_token)
        navigate(roleRedirect(user.role))
      } catch {
        setAuth(
          { id: 0, email: '', full_name: '', role: 'client' } as User,
          tokens.access_token,
          tokens.refresh_token,
        )
        navigate('/app/dashboard')
      }
    },
  })
}

export function useLogout() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()

  return () => {
    logout()
    navigate('/login')
  }
}

export function useCurrentUser() {
  const { isAuthenticated } = useAuthStore()

  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const { data } = await api.get<User>('/auth/me')
      return data
    },
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 10,
  })
}
