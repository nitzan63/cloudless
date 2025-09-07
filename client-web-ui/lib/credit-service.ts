import { apiClient } from './api-client'

export interface CreditTransaction {
  id: string
  userId: string
  amount: number
  type: 'earn' | 'spend'
  description: string
  timestamp: string
}

export interface CreditBalance {
  userId: string
  credits: number
  lastUpdated: string
}

export class CreditService {
  // Spend credits on a task
  static async spendCredits(userId: string, amount: number, taskId: string): Promise<CreditBalance> {
    const response = await fetch(`http://localhost:8002/credits/spend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId,
        amount,
        taskId,
        description: `Spent ${amount} credits on task ${taskId}`
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to spend credits')
    }

    return response.json()
  }

  // Earn credits from processing a job
  static async earnCredits(userId: string, amount: number, jobId: string): Promise<CreditBalance> {
    const response = await fetch(`http://localhost:8002/credits/earn`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId,
        amount,
        jobId,
        description: `Earned ${amount} credits from processing job ${jobId}`
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to earn credits')
    }

    return response.json()
  }

  // Get user's credit balance
  static async getCreditBalance(userId: string): Promise<CreditBalance> {
    const response = await fetch(`http://localhost:8002/credits/balance/${userId}`)
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to get credit balance')
    }

    return response.json()
  }

  // Get user's credit transaction history
  static async getTransactionHistory(userId: string): Promise<CreditTransaction[]> {
    const response = await fetch(`http://localhost:8002/credits/transactions/${userId}`)
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Failed to get transaction history')
    }

    return response.json()
  }
}
