"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Plus, RefreshCw } from "lucide-react"
import TaskList from "@/components/task-list"
import { type Task } from "@/lib/tasks"
import { apiClient } from "@/lib/api-client"
import { toast } from "@/hooks/use-toast"

export default function TasksClient() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchTasks = async () => {
    try {
      const response = await apiClient.getTasks()
      console.log('Fetched tasks:', response)
      setTasks(response)
    } catch (error) {
      console.error("Error fetching tasks:", error)
      toast({
        title: "Error",
        description: "Failed to fetch tasks",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchTasks()
  }, [])

  if (isLoading) {
    return <div className="py-10 text-center">Loading tasks...</div>
  }

  return (
    <div className="flex flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tasks Dashboard</h1>
          <p className="text-muted-foreground">View and manage your Python data processing tasks</p>
        </div>
        <Button 
          onClick={() => {
            setIsRefreshing(true)
            fetchTasks()
          }}
          disabled={isRefreshing}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <TaskList initialTasks={tasks} />
    </div>
  )
}
