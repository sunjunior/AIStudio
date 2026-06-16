import client from './client'
import type { Model, ModelListResponse, ModelCreatePayload } from '../types'

export async function listModels(modelType?: string, status?: string): Promise<ModelListResponse> {
  const params: Record<string, string> = {}
  if (modelType) params.model_type = modelType
  if (status) params.status = status
  const { data } = await client.get<ModelListResponse>('/models', { params })
  return data
}

export async function getModel(id: number): Promise<Model> {
  const { data } = await client.get<Model>(`/models/${id}`)
  return data
}

export async function createModel(payload: ModelCreatePayload): Promise<Model> {
  const { data } = await client.post<Model>('/models', payload)
  return data
}

export async function deleteModel(id: number): Promise<void> {
  await client.delete(`/models/${id}`)
}

export async function downloadModel(id: number): Promise<{ status: string }> {
  const { data } = await client.post<{ status: string }>(`/models/${id}/download`)
  return data
}
