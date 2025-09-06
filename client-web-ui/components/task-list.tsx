"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Eye, Clock, CheckCircle, XCircle, Loader2, AlertCircle, Plus, Coins } from "lucide-react"
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
import { useAuth } from "@/contexts/auth-context"
import Link from "next/link"

interface TaskListProps {
  initialTasks: Task[]
}

export default function TaskList({ initialTasks }: TaskListProps) {
  const router = useRouter()
  const { refreshCredits } = useAuth()
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [taskLogs, setTaskLogs] = useState<any>(null)
  const [loadingLogs, setLoadingLogs] = useState(false)
  const [completionPopup, setCompletionPopup] = useState<{
    show: boolean
    task: Task | null
  }>({ show: false, task: null })


  const handleRefreshTasks = async () => {
    try {
      const updatedTasks = await apiClient.getTasks()
      setTasks(updatedTasks)
      toast({
        title: "Success",
        description: "Tasks refreshed successfully",
      })
    } catch (error) {
      console.error("Error refreshing tasks:", error)
      toast({
        title: "Error",
        description: "Failed to refresh tasks",
        variant: "destructive",
      })
    }
  }

  const handleViewLogs = async (task: Task) => {
    try {
      setLoadingLogs(true)
      setSelectedTask(task)
      const logsData = await apiClient.getTaskLogs(task.id)
      setTaskLogs(logsData)
    } catch (error) {
      console.error("Error fetching logs:", error)
      toast({
        title: "Error",
        description: "Failed to fetch task logs",
        variant: "destructive",
      })
      setTaskLogs(null)
    } finally {
      setLoadingLogs(false)
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A"
    try {
      return new Date(dateString).toLocaleString()
    } catch (error) {
      return "Invalid Date"
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Pending
          </Badge>
        )
      case "submitted":
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="h-3 w-3" /> Submitted
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

  // Check for completed tasks and show popup
  useEffect(() => {
    const checkForCompletedTasks = async () => {
      for (const task of tasks) {
        if (task.status === 'completed' && task.cost !== undefined) {
          const hasShownPopup = localStorage.getItem(`task_completed_${task.id}`)
          if (!hasShownPopup) {
            // Refresh credits before showing popup
            await refreshCredits()
            setCompletionPopup({ show: true, task })
            localStorage.setItem(`task_completed_${task.id}`, 'true')
            break // Only show one popup at a time
          }
        }
      }
    }

    checkForCompletedTasks()
  }, [tasks, refreshCredits])

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Tasks Dashboard</h2>
          <p className="text-muted-foreground">View and manage your Python data processing tasks</p>
        </div>
        <Button onClick={handleRefreshTasks} variant="outline">
          <Loader2 className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

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
                                  <CardTitle className="truncate" title={task.main_file_name || task.name || "Unnamed Task"}>
                  {task.main_file_name || task.name || "Unnamed Task"}
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
                    <span>{formatDate(task.creation_time || task.createdAt || "")}</span>
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
                    <span className="text-muted-foreground">File:</span>
                    <span className="truncate max-w-[200px]" title={task.main_file_name}>
                      {task.main_file_name}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cost:</span>
                    <span className="font-medium">
                      {task.status === 'completed' && task.cost !== undefined 
                        ? `${task.cost} credits`
                        : task.status === 'failed' 
                        ? 'No charge'
                        : 'Not available yet'
                      }
                    </span>
                  </div>
                </div>
              </CardContent>

              <CardFooter className="flex justify-between pt-3">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm" onClick={() => handleViewLogs(task)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View Logs
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>Logs for {selectedTask?.main_file_name}</DialogTitle>
                      <DialogDescription>Task ID: {selectedTask?.id}</DialogDescription>
                    </DialogHeader>
                    <div className="mt-4 space-y-4">
                      {loadingLogs ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin mr-2" />
                          <span>Loading logs...</span>
                        </div>
                      ) : taskLogs?.logs ? (
                        <div className="space-y-2">
                          <h4 className="font-medium">Execution Logs</h4>
                          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
                            <pre className="whitespace-pre-wrap">
                              {JSON.stringify(taskLogs.logs, null, 2)}
                            </pre>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <p className="text-muted-foreground">No logs available for this task</p>
                          <p className="text-sm text-muted-foreground mt-2">
                            {taskLogs?.message || "Logs may not be available yet or the task hasn't been executed."}
                          </p>
                        </div>
                      )}
                    </div>
                  </DialogContent>
                </Dialog>

              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Completion Popup */}
      {completionPopup.show && completionPopup.task && (
        <Dialog open={completionPopup.show} onOpenChange={(open) => setCompletionPopup({ show: open, task: null })}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                Task Completed!
              </DialogTitle>
              <DialogDescription>
                Your task has been successfully completed.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="p-4 bg-muted/50 rounded-lg">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Task:</span>
                    <span className="font-medium">{completionPopup.task.main_file_name || completionPopup.task.name || "Unnamed Task"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Cost:</span>
                    <span className="font-medium text-green-600 flex items-center gap-1">
                      <Coins className="h-4 w-4" />
                      {completionPopup.task.cost} credits
                    </span>
                  </div>
                  {completionPopup.task.duration && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Duration:</span>
                      <span className="font-medium">{Math.ceil(completionPopup.task.duration / 1000)} seconds</span>
                    </div>
                  )}
                  {completionPopup.task.executors && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Executors:</span>
                      <span className="font-medium">{completionPopup.task.executors.length}</span>
                    </div>
                  )}
                </div>
              </div>
              <Button 
                onClick={() => setCompletionPopup({ show: false, task: null })}
                className="w-full"
              >
                Close
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
