import { v4 as uuidv4 } from "uuid"

export interface TaskSpecs {
  cpuCores: number
  memoryGB: number
  storageGB: number
}

export interface Task {
  id: string
  name?: string
  description?: string
  code?: string
  datasetRef?: string
  specs?: TaskSpecs
  status: "pending" | "running" | "completed" | "failed" | "submitted"
  createdAt?: string
  completedAt?: string
  creation_time?: string
  created_by?: string
  requested_workers_amount?: number
  script_path?: string
  main_file_name?: string
  cost?: number // Credits spent on this task
  duration?: number // Task duration in milliseconds
  executors?: string[] // List of executor IPs
}

// In a real application, this would be stored in a database
// For this demo, we'll use localStorage
const STORAGE_KEY = "python-task-manager-tasks"

// Helper to get tasks from localStorage
export const getTasks = (): Task[] => {
  if (typeof window === "undefined") {
    return []
  }

  const tasksJson = localStorage.getItem(STORAGE_KEY)
  return tasksJson ? JSON.parse(tasksJson) : []
}

// Helper to save tasks to localStorage
const saveTasks = (tasks: Task[]): void => {
  if (typeof window === "undefined") {
    return
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks))
}

// Create a new task
export const createTask = (taskData: {
  name: string
  description: string
  code: string
  datasetRef: string
  specs: TaskSpecs
}): Task => {
  // Create a new task object
  const newTask: Task = {
    id: uuidv4(),
    name: taskData.name,
    description: taskData.description,
    code: taskData.code,
    datasetRef: taskData.datasetRef,
    specs: taskData.specs,
    status: "pending",
    createdAt: new Date().toISOString(),
  }

  // Get existing tasks and add the new one
  const tasks = getTasks()
  tasks.push(newTask)

  // Save the updated tasks
  saveTasks(tasks)

  return newTask
}

// Run a task
export const runTask = (taskId: string): Promise<void> => {
  // Get existing tasks
  const tasks = getTasks()

  // Find the task to run
  const taskIndex = tasks.findIndex((task) => task.id === taskId)

  if (taskIndex === -1) {
    throw new Error("Task not found")
  }

  // Update the task status to running
  tasks[taskIndex].status = "running"
  saveTasks(tasks)

  // In a real application, we would send the Python code to a server for execution
  // For this demo, we'll simulate execution with a delay
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Get the tasks again (they might have changed)
      const updatedTasks = getTasks()
      const updatedTaskIndex = updatedTasks.findIndex((task) => task.id === taskId)

      if (updatedTaskIndex === -1) {
        reject(new Error("Task not found"))
        return
      }

      // Simulate success (90% of the time) or failure (10% of the time)
      const success = Math.random() > 0.1

      // Update the task status
      updatedTasks[updatedTaskIndex].status = success ? "completed" : "failed"
      updatedTasks[updatedTaskIndex].completedAt = new Date().toISOString()

      // Save the updated tasks
      saveTasks(updatedTasks)

      if (success) {
        resolve()
      } else {
        reject(new Error("Task execution failed"))
      }
    }, 2000) // Simulate a 2-second execution time
  })
}

// Delete a task
export const deleteTask = (taskId: string): void => {
  // Get existing tasks
  const tasks = getTasks()

  // Filter out the task to delete
  const updatedTasks = tasks.filter((task) => task.id !== taskId)

  // Save the updated tasks
  saveTasks(updatedTasks)
}
