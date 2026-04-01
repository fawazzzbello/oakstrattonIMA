import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import type { User, TokenResponse } from '@/types'

export function useRegister() {
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (data: { email: string; password: string; full_name: string }) => {
      // Register now returns tokens directly — single call, no race condition
      const { data: tokens } = await api.post<TokenResponse>('/auth/register', data)
      return { tokens, email: data.email }
    },
    onSuccess: async ({ tokens }) => {
      try {
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)
        const { data: user } = await api.get<User>('/auth/me')
        setAuth(user, tokens.access_token, tokens.refresh_token)
        navigate('/dashboard')
      } catch {
        // Token is valid but /me failed — still log in with minimal user info
        setAuth(
          { id: 0, email: '', full_name: '', role: 'client' } as User,
          tokens.access_token,
          tokens.refresh_token,
        )
        navigate('/dashboard')
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
        navigate('/dashboard')
      } catch {
        // Token is valid but /me failed — still navigate
        setAuth(
          { id: 0, email: '', full_name: '', role: 'client' } as User,
          tokens.access_token,
          tokens.refresh_token,
        )
        navigate('/dashboard')
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
