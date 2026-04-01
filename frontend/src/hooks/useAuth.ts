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
      await api.post('/auth/register', data)
      const { data: tokens } = await api.post<TokenResponse>('/auth/login', {
        email: data.email,
        password: data.password,
      })
      return tokens
    },
    onSuccess: async (tokens) => {
      localStorage.setItem('access_token', tokens.access_token)
      const { data: user } = await api.get<User>('/auth/me')
      setAuth(user, tokens.access_token, tokens.refresh_token)
      navigate('/dashboard')
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
      localStorage.setItem('access_token', tokens.access_token)
      const { data: user } = await api.get<User>('/auth/me')
      setAuth(user, tokens.access_token, tokens.refresh_token)
      navigate('/dashboard')
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
