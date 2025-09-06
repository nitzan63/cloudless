"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import TaskList from "@/components/task-list"
import { type Task } from "@/lib/tasks"
import { apiClient } from "@/lib/api-client"
import { toast } from "@/hooks/use-toast"

export default function TasksClient() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const tasks = await apiClient.getTasks()
        setTasks(tasks)
      } catch (error) {
        console.error("Error fetching tasks:", error)
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch tasks",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchTasks()
  }, [])

  if (isLoading) {
    return <div className="py-10 text-center">Loading tasks...</div>
  }

  return <TaskList initialTasks={tasks} />
}
