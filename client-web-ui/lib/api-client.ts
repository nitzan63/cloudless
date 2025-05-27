import { API_CONFIG, type ApiError } from './api-config'
import type { Task, TaskSpecs } from './tasks'

export type UploadResult = {
  status: 'success' | 'error'
  file_path?: string
  public_url?: string
  message?: string
}

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_CONFIG.baseUrl
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.message || 'An error occurred')
    }
    return response.json()
  }

  async uploadFile(file: File, taskName: string): Promise<UploadResult> {
    if (!taskName) {
      throw new Error('Task name is required')
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('created_by', 'admin')  // Default value
    formData.append('requested_workers_amount', '1')  // Default value
    formData.append('status', 'submitted')  // Default value
    formData.append('name', taskName)  // Add task name

    const response = await fetch(`${this.baseUrl}${API_CONFIG.endpoints.uploadFile}`, {
      method: 'POST',
      body: formData,
    })
    const result = await this.handleResponse<any>(response)
    return {
      status: 'success',
      file_path: result.task?.file_path || '',
      message: result.message
    }
  }

  async deleteFile(filePath: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.endpoints.deleteFile(filePath)}`,
      {
        method: 'DELETE',
      }
    )
    return this.handleResponse<void>(response)
  }

  async createTask(taskData: {
    name: string
    description: string
    code: string
    datasetRef: string
    specs: TaskSpecs
  }): Promise<Task> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.endpoints.tasks}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
    })
    return this.handleResponse<Task>(response)
  }

  async getTasks(): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.endpoints.tasks}`)
    return this.handleResponse<Task[]>(response)
  }

  async runTask(taskId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.endpoints.runTask(taskId)}`,
      {
        method: 'POST',
      }
    )
    return this.handleResponse<void>(response)
  }

  async deleteTask(taskId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.endpoints.tasks}/${taskId}`,
      {
        method: 'DELETE',
      }
    )
    return this.handleResponse<void>(response)
  }
}

export const apiClient = new ApiClient() 