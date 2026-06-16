import client from './client'
import type { PublishedService, PublishListResponse, PublishCreatePayload } from '../types'

export async function listServices(): Promise<PublishListResponse> {
  const { data } = await client.get<PublishListResponse>('/publishing')
  return data
}

export async function getService(id: number): Promise<PublishedService> {
  const { data } = await client.get<PublishedService>(`/publishing/${id}`)
  return data
}

export async function createService(payload: PublishCreatePayload): Promise<PublishedService> {
  const { data } = await client.post<PublishedService>('/publishing', payload)
  return data
}

export async function stopService(id: number): Promise<void> {
  await client.post(`/publishing/${id}/stop`)
}

export async function deleteService(id: number): Promise<void> {
  await client.delete(`/publishing/${id}`)
}
