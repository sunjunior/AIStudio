import client from './client'
import type { EvaluationRecord, EvaluationListResponse, EvaluationCreatePayload, LogResponse } from '../types'

export async function listEvaluations(status?: string): Promise<EvaluationListResponse> {
  const params: Record<string, string> = {}
  if (status) params.status = status
  const { data } = await client.get<EvaluationListResponse>('/evaluation', { params })
  return data
}

export async function getEvaluation(id: number): Promise<EvaluationRecord> {
  const { data } = await client.get<EvaluationRecord>(`/evaluation/${id}`)
  return data
}

export async function createEvaluation(payload: EvaluationCreatePayload): Promise<EvaluationRecord> {
  const { data } = await client.post<EvaluationRecord>('/evaluation', payload)
  return data
}

export async function deleteEvaluation(id: number): Promise<void> {
  await client.delete(`/evaluation/${id}`)
}

export async function getEvaluationLogs(id: number): Promise<LogResponse> {
  const { data } = await client.get<LogResponse>(`/evaluation/${id}/logs`)
  return data
}
