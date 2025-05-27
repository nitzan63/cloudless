"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Rocket, Loader2, FileText, Upload, X, Check, HelpCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { toast } from "@/hooks/use-toast"
import CodeEditor from "@/components/code-editor"
import { apiClient } from "@/lib/api-client"
import ResourceRequirements from "./resource-requirements"

export default function TaskForm() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [validationStatus, setValidationStatus] = useState<'unvalidated' | 'valid' | 'invalid'>('unvalidated')
  const [validationErrors, setValidationErrors] = useState<string[]>([])
  const [taskName, setTaskName] = useState("")
  const [taskDescription, setTaskDescription] = useState("")
  const [pythonCode, setPythonCode] = useState(
    "# Enter your Python code here\n\ndef process_data():\n    # Your data processing logic\n    print('Processing data...')\n    \n    # Example: process some data\n    data = [1, 2, 3, 4, 5]\n    result = sum(data)\n    \n    print(f'Result: {result}')\n    return result\n\nif __name__ == '__main__':\n    process_data()",
  )
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [datasetUrl, setDatasetUrl] = useState("")
  const [uploadedFilePath, setUploadedFilePath] = useState<string | null>(null)
  const [specs, setSpecs] = useState({
    cpuCores: 4,
    memoryGB: 8,
    storageGB: 20,
  })

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setSelectedFile(file)
    // Reset validation status when new file is uploaded
    setValidationStatus('unvalidated')
    setValidationErrors([])

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
    const url = e.target.value
    setDatasetUrl(url)
    // Reset validation status when URL changes
    setValidationStatus('unvalidated')
    setValidationErrors([])
  }

  const handleUploadDataset = async () => {
    if (!datasetUrl) {
      toast({
        title: "Error",
        description: "Please enter a dataset URL",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    try {
      // Here we'll just store the URL directly
      setUploadedFilePath(datasetUrl)
      toast({
        title: "Success",
        description: "Dataset URL saved successfully",
      })
    } catch (error) {
      console.error('Error saving dataset URL:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save dataset URL",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemoveDataset = () => {
    setDatasetUrl("")
    setUploadedFilePath(null)
    toast({
      title: "Success",
      description: "Dataset URL removed successfully",
    })
  }

  const handleValidateTask = async () => {
    if (!pythonCode.trim()) {
      toast({
        title: "Error",
        description: "Please provide Python code for the task",
        variant: "destructive",
      })
      return
    }

    // Validate task name
    if (!taskName) {
      setValidationStatus('invalid')
      setValidationErrors(["Please enter a task name"])
      return
    }

    // Check for valid task name format
    const taskNameRegex = /^[a-zA-Z0-9_-]+$/
    if (!taskNameRegex.test(taskName)) {
      setValidationStatus('invalid')
      setValidationErrors(["Task name must contain only English letters, numbers, underscore (_), and hyphen (-). No spaces allowed."])
      return
    }

    if (!datasetUrl) {
      setValidationStatus('invalid')
      setValidationErrors(["Please enter a CSV URL"])
      return
    }

    // Validate CSV URL format
    try {
      const url = new URL(datasetUrl)
      if (!url.pathname.toLowerCase().endsWith('.csv')) {
        setValidationStatus('invalid')
        setValidationErrors(["URL must point to a CSV file"])
        return
      }
    } catch (error) {
      setValidationStatus('invalid')
      setValidationErrors(["Please enter a valid URL"])
      return
    }

    setIsValidating(true)
    setValidationErrors([])
    try {
      // Check for model.pkl saving
      const hasModelSave = (
        pythonCode.includes('model.pkl') && 
        (
          // Check for different ways of saving
          (pythonCode.includes('pickle.dump') && pythonCode.includes('open("model.pkl"')) ||
          (pythonCode.includes('joblib.dump') && pythonCode.includes('open("model.pkl"')) ||
          (pythonCode.includes('torch.save') && pythonCode.includes('"model.pkl"')) ||
          (pythonCode.includes('save_model') && pythonCode.includes('"model.pkl"'))
        ) &&
        // Ensure it's saved in the working directory (not in a subdirectory)
        !pythonCode.includes('os.path.join') &&
        !pythonCode.includes('Path("model.pkl"') &&
        !pythonCode.includes('pathlib.Path("model.pkl"')
      )

      // Check for optional metrics.json saving
      const hasMetricsSave = (
        pythonCode.includes('metrics.json') && 
        (
          (pythonCode.includes('json.dump') && pythonCode.includes('open("metrics.json"')) ||
          (pythonCode.includes('json.dumps') && pythonCode.includes('open("metrics.json"'))
        ) &&
        // Ensure it's saved in the working directory
        !pythonCode.includes('os.path.join') &&
        !pythonCode.includes('Path("metrics.json"') &&
        !pythonCode.includes('pathlib.Path("metrics.json"')
      )

      // Check for URL argument handling
      const hasUrlArg = (
        // Check for argparse
        (pythonCode.includes('argparse.ArgumentParser') && 
         pythonCode.includes('add_argument') && 
         pythonCode.includes('parse_args')) ||
        // Check for sys.argv
        (pythonCode.includes('sys.argv') && 
         pythonCode.includes('len(sys.argv)') && 
         pythonCode.includes('sys.argv[1]'))
      )

      // Validate requirements
      const errors: string[] = []

      if (!hasUrlArg) {
        errors.push("Script must accept exactly one URL argument (using argparse or sys.argv)")
      }

      if (!hasModelSave) {
        errors.push("Script must save model.pkl in the working directory")
      }

      // Check for multiple arguments
      const hasMultipleArgs = (
        (pythonCode.includes('argparse.ArgumentParser') && 
         (pythonCode.match(/add_argument\(/g) || []).length > 1) ||
        (pythonCode.includes('sys.argv') && 
         pythonCode.includes('len(sys.argv)') && 
         !(pythonCode.includes('len(sys.argv) == 2') || 
           pythonCode.includes('len(sys.argv) < 2') ||
           pythonCode.includes('len(sys.argv) != 2')))
      )

      if (hasMultipleArgs) {
        errors.push("Script must accept only one argument (the URL)")
      }

      if (errors.length > 0) {
        setValidationStatus('invalid')
        setValidationErrors(errors)
        return
      }

      setValidationStatus('valid')
      setValidationErrors([])
      toast({
        title: "Success",
        description: `Task validation successful! The script meets all requirements.${
          hasMetricsSave ? ' (Includes metrics.json saving)' : ''
        }`,
      })
    } catch (error) {
      console.error("Validation error:", error)
      setValidationStatus('invalid')
      setValidationErrors([error instanceof Error ? error.message : "Failed to validate task"])
    } finally {
      setIsValidating(false)
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

  const handleTaskNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value
    setTaskName(newName)
    // Reset validation status when task name changes
    setValidationStatus('unvalidated')
    setValidationErrors([])
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
                <Input id="python-file" type="file" accept=".py,.ipynb" onChange={handleFileChange} />
                {selectedFile && (
                  <p className="text-sm text-muted-foreground">
                    Selected: {selectedFile.name}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="dataset-url">Dataset URL</Label>
                <div className="flex gap-2">
                  <Input 
                    id="dataset-url" 
                    type="url" 
                    placeholder="Enter public CSV URL"
                    value={datasetUrl}
                    onChange={handleDatasetChange}
                  />
                  {!uploadedFilePath ? (
                    <Button 
                      type="button" 
                      onClick={handleUploadDataset}
                      disabled={isUploading || !datasetUrl}
                    >
                      {isUploading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Upload className="mr-2 h-4 w-4" />
                      )}
                      Save URL
                    </Button>
                  ) : (
                    <Button 
                      type="button" 
                      variant="destructive"
                      onClick={handleRemoveDataset}
                      disabled={isUploading}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Remove
                    </Button>
                  )}
                </div>
                {uploadedFilePath && (
                  <p className="text-sm text-muted-foreground flex items-center">
                    <Check className="mr-2 h-4 w-4 text-green-500" />
                    URL saved: {uploadedFilePath}
                  </p>
                )}
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
              disabled={isValidating || isUploading}
            >
              {isValidating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Validating...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  Validate Task
                </>
              )}
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
            >
              <HelpCircle className="h-4 w-4" />
              How to Submit a Task?
            </button>
          </div>
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
              value={pythonCode} 
              onChange={(newCode) => {
                setPythonCode(newCode)
                // Reset validation status when code is edited
                setValidationStatus('unvalidated')
                setValidationErrors([])
              }} 
              language="python" 
            />
          </CardContent>
        </Card>
      </div>
    </form>
  )
}
