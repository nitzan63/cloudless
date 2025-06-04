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
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: "mock-task-1",
      creation_time: new Date().toISOString(),
      created_by: "admin",
      requested_workers_amount: 2,
      script_path: "/uploads/mock_script.py",
      main_file_name: "mock_script.py",
      status: "submitted",
      batch_job_id: null,
      logs: "2024-03-20 10:00:00 - Task started\n2024-03-20 10:00:01 - Processing data\n2024-03-20 10:00:02 - Task completed successfully"
    },
    {
      id: "mock-task-2",
      creation_time: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      created_by: "admin",
      requested_workers_amount: 1,
      script_path: "/uploads/another_script.py",
      main_file_name: "another_script.py",
      status: "completed",
      batch_job_id: 123,
      logs: "2024-03-20 09:00:00 - Task started\n2024-03-20 09:00:30 - Data processing complete\n2024-03-20 09:00:31 - Results saved\n2024-03-20 09:00:32 - Task completed successfully"
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchTasks = async () => {
    // For now, we'll just use the mock data
    setIsRefreshing(false)
  }

  useEffect(() => {
    // No need to fetch since we're using mock data
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
