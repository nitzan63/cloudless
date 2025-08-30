'use client'

import { useAuth } from '@/contexts/auth-context'
import { redirect } from 'next/navigation'
import { ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredType?: 'provider' | 'submitter'
}

export default function ProtectedRoute({ children, requiredType }: ProtectedRouteProps) {
  const { isAuthenticated, user, loading } = useAuth()

  // Show loading while checking auth
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    redirect('/login')
  }

  // Check user type if required
  if (requiredType && user?.type !== requiredType) {
    redirect('/profile')
  }

  // User is authenticated and has correct type (if required)
  return <>{children}</>
}
