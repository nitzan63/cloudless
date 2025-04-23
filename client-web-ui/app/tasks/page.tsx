import type { Metadata } from "next"
import TasksClient from "@/components/tasks-client"

export const metadata: Metadata = {
  title: "Python Task Manager - Tasks",
  description: "View and manage your Python data processing tasks",
}

export default function TasksPage() {
  return (
    <div className="container mx-auto py-10">
      <TasksClient />
    </div>
  )
}
