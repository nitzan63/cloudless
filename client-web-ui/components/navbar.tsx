"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Cloud, Plus, LogOut } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <nav className="border-b border-border bg-background/80 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Cloud className="h-8 w-8 text-primary" />
          <Link href="/" className="text-2xl font-bold text-foreground">
            Cloudless
          </Link>
        </div>
        
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            // Logged in: Show task management
            <>
              <Button asChild variant="outline">
                <Link href="/" className="flex items-center">
                  <Plus className="mr-2 h-4 w-4" />
                  New Task
                </Link>
              </Button>
              <Button asChild>
                <Link href="/tasks">View Tasks</Link>
              </Button>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-muted-foreground">
                  {user?.username} ({user?.type})
                </span>
                <Button variant="ghost" size="sm" onClick={logout}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </>
          ) : (
            // Not logged in: Show auth options
            <>
              <Link href="/login">
                <Button variant="ghost">Login</Button>
              </Link>
              <Link href="/register">
                <Button>Get Started</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
} 