"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Plus, Cloud, X } from "lucide-react"

export default function Navbar() {
  return (
    <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
      <div className="flex h-16 items-center px-6">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1">
            <Cloud className="h-6 w-6 text-indigo-400" />
            <X className="h-4 w-4 text-indigo-400" />
          </div>
          <Link href="/" className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-indigo-600 bg-clip-text text-transparent">
            Cloudless
          </Link>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <Button asChild variant="outline" className="border-slate-800 hover:bg-slate-800 hover:text-white">
            <Link href="/" className="flex items-center">
              <Plus className="mr-2 h-4 w-4" />
              New Task
            </Link>
          </Button>
          <Button asChild className="bg-indigo-600 hover:bg-indigo-700">
            <Link href="/tasks">View Tasks</Link>
          </Button>
        </div>
      </div>
    </nav>
  )
} 