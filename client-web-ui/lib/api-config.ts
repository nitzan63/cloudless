export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  endpoints: {
    tasks: '/tasks',
    runTask: (taskId: string) => `/tasks/${taskId}/run`,
    uploadFile: '/api/upload',
    deleteFile: (filePath: string) => `/api/files/${filePath}`,
  }
}

export type ApiError = {
  error: string
  message?: string
  details?: unknown
} 