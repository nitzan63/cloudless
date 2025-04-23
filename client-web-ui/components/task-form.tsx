"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Rocket, Loader2, FileText, Upload, X, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "@/hooks/use-toast"
import CodeEditor from "@/components/code-editor"
import { apiClient } from "@/lib/api-client"
import ResourceRequirements from "./resource-requirements"

export default function TaskForm() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [taskName, setTaskName] = useState("")
  const [taskDescription, setTaskDescription] = useState("")
  const [pythonCode, setPythonCode] = useState(
    "# Enter your Python code here\n\ndef process_data():\n    # Your data processing logic\n    print('Processing data...')\n    \n    # Example: process some data\n    data = [1, 2, 3, 4, 5]\n    result = sum(data)\n    \n    print(f'Result: {result}')\n    return result\n\nif __name__ == '__main__':\n    process_data()",
  )
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedDataset, setSelectedDataset] = useState<File | null>(null)
  const [uploadedFilePath, setUploadedFilePath] = useState<string | null>(null)
  const [specs, setSpecs] = useState({
    cpuCores: 4,
    memoryGB: 8,
    storageGB: 20,
  })

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)

    if (file) {
      // Auto-fill task name from filename if not already set
      if (!taskName) {
        setTaskName(file.name.replace(/\.(py|ipynb)$/, ""))
      }

      // Read file content to display in editor
      const reader = new FileReader()
      reader.onload = async (event) => {
        if (event.target?.result) {
          if (file.name.endsWith('.ipynb')) {
            try {
              // Parse the notebook JSON
              const notebook = JSON.parse(event.target.result as string)
              // Extract code cells and combine them
              const code = notebook.cells
                .filter((cell: any) => cell.cell_type === 'code')
                .map((cell: any) => cell.source.join(''))
                .join('\n\n')
              setPythonCode(code)
            } catch (error) {
              console.error('Error parsing notebook:', error)
              toast({
                title: "Error",
                description: "Failed to parse Jupyter notebook. Please try again.",
                variant: "destructive",
              })
            }
          } else {
            setPythonCode(event.target.result as string)
          }
        }
      }
      reader.readAsText(file)
    }
  }

  const handleDatasetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedDataset(file)
    // Reset the uploaded file path when a new file is selected
    setUploadedFilePath(null)
  }

  const handleUploadDataset = async () => {
    if (!selectedDataset) {
      toast({
        title: "Error",
        description: "Please select a dataset file first",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    try {
      const result = await apiClient.uploadFile(selectedDataset)
      if (result.status === 'success' && result.file_path) {
        setUploadedFilePath(result.file_path)
        toast({
          title: "Success",
          description: "Dataset uploaded successfully",
        })
      } else {
        throw new Error(result.message || 'Upload failed')
      }
    } catch (error) {
      console.error('Error uploading dataset:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to upload dataset",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveDataset = async () => {
    if (!uploadedFilePath) return

    setIsUploading(true)
    try {
      await apiClient.deleteFile(uploadedFilePath)
      setSelectedDataset(null)
      setUploadedFilePath(null)
      toast({
        title: "Success",
        description: "Dataset removed successfully",
      })
    } catch (error) {
      console.error('Error removing dataset:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to remove dataset",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!taskName) {
      toast({
        title: "Error",
        description: "Please provide a task name",
        variant: "destructive",
      })
      return
    }

    if (!pythonCode.trim()) {
      toast({
        title: "Error",
        description: "Please provide Python code for the task",
        variant: "destructive",
      })
      return
    }

    if (!uploadedFilePath) {
      toast({
        title: "Error",
        description: "Please upload your dataset first",
        variant: "destructive",
      })
      return
    }

    try {
      setIsLoading(true)

      await apiClient.createTask({
        name: taskName,
        description: taskDescription,
        code: pythonCode,
        datasetRef: uploadedFilePath,
        specs,
      })

      toast({
        title: "Success",
        description: "Task created successfully",
      })

      router.push("/tasks")
      router.refresh()
    } catch (error) {
      console.error("Error creating task:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create task. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div className="w-[30rem] border-r bg-background p-6 space-y-6 overflow-y-auto">
        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="basic">Basic Info</TabsTrigger>
            <TabsTrigger value="resources">Resources</TabsTrigger>
          </TabsList>
          
          <TabsContent value="basic" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="task-name">Task Name</Label>
                <Input
                  id="task-name"
                  placeholder="Enter task name"
                  value={taskName}
                  onChange={(e) => setTaskName(e.target.value)}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="task-description">Description</Label>
                <Textarea
                  id="task-description"
                  placeholder="Describe what this task does"
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="python-file">Python Code</Label>
                <Input id="python-file" type="file" accept=".py,.ipynb" onChange={handleFileChange} />
                {selectedFile && (
                  <p className="text-sm text-muted-foreground">
                    Selected: {selectedFile.name}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="dataset-file">Dataset</Label>
                <div className="flex gap-2">
                  <Input 
                    id="dataset-file" 
                    type="file" 
                    accept=".csv,.json,.txt" 
                    onChange={handleDatasetChange}
                    disabled={isUploading || !!uploadedFilePath}
                  />
                  {selectedDataset && !uploadedFilePath && (
                    <Button
                      type="button"
                      size="icon"
                      onClick={handleUploadDataset}
                      disabled={isUploading}
                    >
                      {isUploading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Upload className="h-4 w-4" />
                      )}
                    </Button>
                  )}
                  {uploadedFilePath && (
                    <Button
                      type="button"
                      size="icon"
                      variant="destructive"
                      onClick={handleRemoveDataset}
                      disabled={isUploading}
                    >
                      {isUploading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <X className="h-4 w-4" />
                      )}
                    </Button>
                  )}
                </div>
                {selectedDataset && (
                  <p className="text-sm text-muted-foreground flex items-center gap-2">
                    {selectedDataset.name}
                    {uploadedFilePath && <Check className="h-4 w-4 text-green-500" />}
                  </p>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="resources">
            <ResourceRequirements onSpecsChange={setSpecs} />
          </TabsContent>
        </Tabs>

        <Button type="submit" className="w-full" disabled={isLoading || isUploading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Launching Task...
            </>
          ) : (
            <>
              <Rocket className="mr-2 h-4 w-4" />
              Launch Task
            </>
          )}
        </Button>
      </div>

      {/* Main Content - Code Editor */}
      <div className="flex-1 p-6">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Submit New Task</CardTitle>
            <CardDescription>Write or paste your Python code here</CardDescription>
          </CardHeader>
          <CardContent className="h-[calc(100%-8rem)]">
            <CodeEditor value={pythonCode} onChange={setPythonCode} language="python" />
          </CardContent>
        </Card>
      </div>
    </form>
  )
}
