export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002',
  endpoints: {
    tasks: '/tasks',
    runTask: (taskId: string) => `/tasks/${taskId}/run`,
    uploadFile: '/tasks',
    deleteFile: (filePath: string) => `/files/${filePath}`,
  }
}

export type ApiError = {
  error: string
  message?: string
  details?: unknown
} 