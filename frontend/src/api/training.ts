import client from './client'
import type { TrainingTask, TrainingListResponse, TrainingCreatePayload, LogResponse } from '../types'

export async function listTrainingTasks(status?: string): Promise<TrainingListResponse> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const { data } = await client.get<TrainingListResponse>('/training', { params })
  return data
}

export async function getTrainingTask(id: number): Promise<TrainingTask> {
  const { data } = await client.get<TrainingTask>(`/training/${id}`)
  return data
}

export async function createTrainingTask(payload: TrainingCreatePayload): Promise<TrainingTask> {
  const { data } = await client.post<TrainingTask>('/training', payload)
  return data
}

export async function cancelTrainingTask(id: number): Promise<void> {
  await client.post(`/training/${id}/cancel`)
}

export async function getTrainingLogs(id: number): Promise<LogResponse> {
  const { data } = await client.get<LogResponse>(`/training/${id}/logs`)
  return data
}
