export const API_CONFIG = {
  baseUrl: 'http://localhost:8000',
  endpoints: {
    tasks: '/api/tasks',
    runTask: (taskId: string) => `/api/tasks/${taskId}/run`,
    uploadFile: '/api/tasks',
    deleteFile: (filePath: string) => `/api/files/${filePath}`,
  }
}

export type ApiError = {
  error: string
  message?: string
  details?: unknown
} 