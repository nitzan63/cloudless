"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Play, Trash2, Eye, Clock, CheckCircle, XCircle, Loader2, AlertCircle, Plus, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { toast } from "@/hooks/use-toast"
import { type Task } from "@/lib/tasks"
import { apiClient } from "@/lib/api-client"
import Link from "next/link"

interface TaskListProps {
  initialTasks: Task[]
}

export default function TaskList({ initialTasks }: TaskListProps) {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [runningTaskIds, setRunningTaskIds] = useState<Set<string>>(new Set())
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)

  const handleRunTask = async (taskId: string) => {
    try {
      setRunningTaskIds((prev) => new Set(prev).add(taskId))

      await apiClient.runTask(taskId)

      // Refresh the tasks list
      const updatedTasks = await apiClient.getTasks()
      setTasks(updatedTasks)

      toast({
        title: "Success",
        description: "Task executed successfully",
      })
    } catch (error) {
      console.error("Error running task:", error)

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to execute task",
        variant: "destructive",
      })
    } finally {
      setRunningTaskIds((prev) => {
        const updated = new Set(prev)
        updated.delete(taskId)
        return updated
      })
    }
  }

  const handleDeleteTask = async (taskId: string) => {
    try {
      await apiClient.deleteTask(taskId)

      // Remove the task from the UI
      setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId))

      toast({
        title: "Success",
        description: "Task deleted successfully",
      })
    } catch (error) {
      console.error("Error deleting task:", error)

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to delete task",
        variant: "destructive",
      })
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Pending
          </Badge>
        )
      case "running":
        return (
          <Badge variant="secondary" className="flex items-center gap-1">
            <Loader2 className="h-3 w-3 animate-spin" /> Running
          </Badge>
        )
      case "completed":
        return (
          <Badge variant="success" className="flex items-center gap-1 bg-green-100 text-green-800">
            <CheckCircle className="h-3 w-3" /> Completed
          </Badge>
        )
      case "failed":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="h-3 w-3" /> Failed
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            <AlertCircle className="h-3 w-3" /> Unknown
          </Badge>
        )
    }
  }

  return (
    <div className="space-y-6">
      {tasks.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-10">
            <div className="text-center space-y-2">
              <h3 className="text-xl font-medium">No tasks found</h3>
              <p className="text-muted-foreground">Create a new task to get started</p>
              <Button asChild className="mt-4">
                <Link href="/tasks/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Task
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {tasks.map((task) => (
            <Card key={task.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <CardTitle className="truncate" title={task.main_file_name}>
                    {task.main_file_name}
                  </CardTitle>
                  {getStatusBadge(task.status)}
                </div>
                <CardDescription className="line-clamp-2">
                  {task.description || "No description provided"}
                </CardDescription>
              </CardHeader>

              <CardContent className="pb-2">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created:</span>
                    <span>{formatDate(task.creation_time)}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created By:</span>
                    <span>{task.created_by}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Workers:</span>
                    <span>{task.requested_workers_amount}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Script Path:</span>
                    <span className="truncate max-w-[200px]" title={task.script_path}>
                      {task.script_path}
                    </span>
                  </div>
                </div>
              </CardContent>

              <CardFooter className="flex justify-between pt-3">
                <div className="flex space-x-2">
                  {task.results_path ? (
                    <Button asChild variant="outline" size="sm">
                      <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/tasks/${task.id}/results`}>
                        <Download className="h-4 w-4 mr-1" />
                        Download Results
                      </a>
                    </Button>
                  ) : null}
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
