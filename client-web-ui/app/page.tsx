import type { Metadata } from "next"
import TaskForm from "@/components/task-form"

export const metadata: Metadata = {
  title: "Submit New Task - Cloudless",
  description: "Submit a new Python data processing task to the distributed compute network",
}

export default function HomePage() {
  return (
    <div className="h-[calc(100vh-4rem)]">
      <TaskForm />
    </div>
  )
}
