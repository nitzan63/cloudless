"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Rocket, Loader2, FileText, Upload, X, Check, HelpCircle, Coins } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { toast } from "@/hooks/use-toast"
import { useAuth } from "@/contexts/auth-context"
import CodeEditor from "@/components/code-editor"
import { apiClient } from "@/lib/api-client"
import { CreditService } from "@/lib/credit-service"
import ResourceRequirements from "./resource-requirements"

export default function TaskForm() {
  const router = useRouter()
  const { user, refreshCredits } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [validationStatus, setValidationStatus] = useState<'unvalidated' | 'valid' | 'invalid'>('unvalidated')
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [showGuide, setShowGuide] = useState(false)
  const [taskName, setTaskName] = useState("")
  const [taskDescription, setTaskDescription] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFilePath, setUploadedFilePath] = useState<string | null>(null)
  const [specs, setSpecs] = useState({
    cpuCores: 4,
    memoryGB: 8,
    storageGB: 20,
  })
  const [fileContent, setFileContent] = useState<string>("")
  const [datasetUrl, setDatasetUrl] = useState("")

  useEffect(() => {
    const readFile = async () => {
      if (selectedFile) {
        const content = await selectedFile.text()
        setFileContent(content)
      }
    }
    readFile()
  }, [selectedFile])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Only check if it's a Python file
    if (!file.name.endsWith('.py')) {
      setValidationStatus('invalid')
      setValidationErrors(['Please upload a Python file (.py)'])
      return
    }

    setSelectedFile(file)
    // Reset validation status when file changes
    setValidationStatus('unvalidated')
    setValidationErrors([])
  }

  const handleValidateTask = async () => {
    const errors: string[] = []

    // Check if file is uploaded
    if (!selectedFile) {
      errors.push('Please upload a Python file')
    }

    // Check if task name is provided
    if (!taskName || taskName.trim() === '') {
      errors.push('Please enter a task name')
    }

    // Check if task name contains only valid characters
    if (taskName && !/^[a-zA-Z0-9_-]+$/.test(taskName)) {
      errors.push('Task name can only contain letters, numbers, underscores (_), and hyphens (-)')
    }

    // Check if file content is not empty
    if (selectedFile && fileContent.trim() === '') {
      errors.push('Python file cannot be empty')
    }

    // Check if file content contains basic Python syntax
    if (selectedFile && fileContent.trim() !== '') {
      if (!fileContent.includes('def ') && !fileContent.includes('import ')) {
        errors.push('File should contain Python code (functions or imports)')
      }
    }

    if (errors.length > 0) {
      setValidationStatus('invalid')
      setValidationErrors(errors)
      toast({
        title: "Validation Failed",
        description: "Please fix the validation errors before proceeding.",
        variant: "destructive",
      })
      return
    }

    // All validations passed
    setValidationStatus('valid')
    setValidationErrors([])
    toast({
      title: "Validation Successful!",
      description: "Your task meets all requirements and is ready to be launched!",
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) return

    // Check if user has enough credits
    if (!user) {
      toast({
        title: "Error",
        description: "You must be logged in to submit tasks",
        variant: "destructive",
      })
      return
    }

    if ((user.credits || 0) < 1) {
      toast({
        title: "Insufficient Credits",
        description: "You need at least 1 credit to submit a task. Current balance: " + (user.credits || 0) + " credits",
        variant: "destructive",
      })
      return
    }

    try {
      const fileContent = await selectedFile.text()
      
      // First create the task
      const task = await apiClient.createTask({
        name: taskName,
        description: 'Spark task', // We can make this dynamic later
        code: fileContent,
        datasetRef: '', // We'll handle this later
        specs: {
          cpuCores: 1,
          memoryGB: 1,
          storageGB: 1,
        },
      })

      // Task submitted - credits will be charged after completion based on actual usage
      toast({
        title: "Task Submitted Successfully!",
        description: `Task "${taskName}" has been submitted. Credits will be charged after completion based on actual resource usage.`,
      })
      
      router.push("/tasks")
      router.refresh()
    } catch (error) {
      console.error('Error creating task:', error)
      toast({
        title: "Error",
        description: "Failed to create task",
        variant: "destructive",
      })
    }
  }

  const handleTaskNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value
    setTaskName(newName)
    // Reset validation status when task name changes
    setValidationStatus('unvalidated')
    setValidationErrors([])
  }

  const handleDatasetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDatasetUrl(e.target.value)
  }

  const handleUploadDataset = async () => {
    // Implementation of handleUploadDataset
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
                  placeholder="Enter task name (letters, numbers, _, - only)"
                  value={taskName}
                  onChange={handleTaskNameChange}
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
                <Input id="python-file" type="file" accept=".py" onChange={handleFileChange} />
                {selectedFile && (
                  <p className="text-sm text-muted-foreground">
                    Selected: {selectedFile.name}
                  </p>
                )}
              </div>

              <div className="space-y-2 opacity-50">
                <Label htmlFor="dataset-url" className="flex items-center gap-2">
                  Dataset URL
                  <span className="text-xs text-muted-foreground">(Currently Disabled)</span>
                </Label>
                <div className="flex gap-2">
                  <Input 
                    id="dataset-url" 
                    type="url" 
                    placeholder="Enter public CSV URL"
                    value={datasetUrl}
                    onChange={handleDatasetChange}
                    disabled
                  />
                  <Button 
                    type="button" 
                    onClick={handleUploadDataset}
                    disabled
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Save URL
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground">
                  Dataset URL functionality is currently disabled
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="resources">
            <ResourceRequirements onSpecsChange={setSpecs} />
          </TabsContent>
        </Tabs>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Button 
              type="button" 
              variant="outline" 
              className="flex-1" 
              onClick={handleValidateTask}
              disabled={isUploading}
            >
              <FileText className="mr-2 h-4 w-4" />
              Validate Task
            </Button>
            <div className="w-8 h-8 rounded-full flex items-center justify-center">
              {validationStatus === 'unvalidated' && (
                <div className="w-4 h-4 rounded-full bg-yellow-400" title="Not yet validated" />
              )}
              {validationStatus === 'valid' && (
                <div className="w-4 h-4 rounded-full bg-green-500" title="Valid" />
              )}
              {validationStatus === 'invalid' && (
                <div className="w-4 h-4 rounded-full bg-red-500" title="Invalid" />
              )}
            </div>
          </div>

          {/* Credit Cost Display */}
          {validationStatus === 'valid' && (
            <div className="mb-4 p-3 bg-muted/50 rounded-lg border border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Coins className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm font-medium text-foreground">Task Cost:</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-muted-foreground">Charged after completion based on usage</span>
                  <span className="text-xs text-muted-foreground">(Current: {user?.credits || 0})</span>
                </div>
              </div>
            </div>
          )}

          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading || isUploading || validationStatus !== 'valid'}
          >
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

          {validationErrors.length > 0 && (
            <Card className="mt-4 border-destructive/50">
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <X className="h-4 w-4 text-destructive" />
                  Validation Errors
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <ul className="space-y-2">
                  {validationErrors.map((error, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-destructive">•</span>
                      {error}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {validationStatus === 'unvalidated' && (
            <Card className="mt-4 border-yellow-200">
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <FileText className="h-4 w-4 text-yellow-500" />
                  Script Not Validated
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <p className="text-sm text-muted-foreground">
                  Please validate your script before launching the task to ensure it meets all requirements.
                </p>
              </CardContent>
            </Card>
          )}

          {validationStatus === 'valid' && (
            <Card className="mt-4 border-green-200">
              <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  Script Validated Successfully
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <p className="text-sm text-muted-foreground">
                  Your script meets all requirements and is ready to be launched!
                </p>
              </CardContent>
            </Card>
          )}

          <div className="mt-4 flex justify-center">
            <button 
              type="button" 
              className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setShowGuide(true)}
            >
              <HelpCircle className="h-4 w-4" />
              How to Submit a Task?
            </button>
          </div>

          <Dialog open={showGuide} onOpenChange={setShowGuide}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold">How to Submit a Spark Task</DialogTitle>
                <DialogDescription className="text-lg">
                  Quick guide to submit your Spark job
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6 py-4">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold">Requirements</h3>
                  <ul className="list-none space-y-3 text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Your script must use PySpark and accept a dataset URL as input</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Dataset URL must be accessible from the Spark cluster</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-blue-500">•</span>
                      <span>Task name should be descriptive (letters, numbers, _, - only)</span>
                    </li>
                  </ul>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold">Steps</h3>
                  <ol className="list-decimal pl-6 space-y-3 text-muted-foreground">
                    <li>Enter a task name</li>
                    <li>Upload your Spark script</li>
                    <li>Click "Validate Task"</li>
                    <li>Click "Launch Task" to submit</li>
                  </ol>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Main Content - Code Editor */}
      <div className="flex-1 p-6">
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Submit New Task</CardTitle>
            <CardDescription>Write or paste your Python code here</CardDescription>
          </CardHeader>
          <CardContent className="h-[calc(100%-8rem)]">
            <CodeEditor 
              value={fileContent} 
              onChange={(newCode) => {
                setFileContent(newCode)
                // Reset validation status when code is edited
                setValidationStatus('unvalidated')
              }}
              language="python"
            />
          </CardContent>
        </Card>
      </div>
    </form>
  )
}
