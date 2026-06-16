export type ModelSource = 'huggingface' | 'local' | 'uploaded'
export type ModelType = 'llm' | 'embedding' | 'peft_checkpoint'
export type ModelStatus = 'downloading' | 'ready' | 'error'

export interface Model {
  id: number
  name: string
  source: ModelSource
  source_path: string
  model_type: ModelType
  base_model_id: number | null
  status: ModelStatus
  local_path: string
  description: string
  created_at: string
  updated_at: string
}

export interface ModelListResponse {
  models: Model[]
  total: number
}

export interface ModelCreatePayload {
  name: string
  source: ModelSource
  source_path: string
  model_type: ModelType
  base_model_id?: number | null
  description?: string
}

export type TrainingMethod = 'lora' | 'qlora'
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface TrainingTask {
  id: number
  model_id: number
  method: TrainingMethod
  config: Record<string, any>
  status: TaskStatus
  pid: number | null
  log_path: string
  output_model_id: number | null
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface TrainingListResponse {
  tasks: TrainingTask[]
  total: number
}

export interface TrainingConfig {
  method: TrainingMethod
  learning_rate: number
  num_epochs: number
  batch_size: number
  lora_r: number
  lora_alpha: number
  max_length: number
  dataset_path: string
  output_name: string
}

export interface TrainingCreatePayload {
  model_id: number
  config: TrainingConfig
}

export type EvalType = 'perplexity' | 'benchmark' | 'custom'
export type EvalStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface EvaluationRecord {
  id: number
  model_id: number
  eval_type: EvalType
  dataset: string
  metrics: Record<string, any> | null
  status: EvalStatus
  log_path: string
  error_message: string | null
  created_at: string
}

export interface EvaluationListResponse {
  records: EvaluationRecord[]
  total: number
}

export interface EvaluationCreatePayload {
  model_id: number
  eval_type: EvalType
  dataset: string
}

export type ServiceType = 'api' | 'export'
export type ServiceStatus = 'running' | 'stopped' | 'failed'

export interface PublishedService {
  id: number
  model_id: number
  service_type: ServiceType
  endpoint: string | null
  export_path: string | null
  config: Record<string, any>
  status: ServiceStatus
  pid: number | null
  error_message: string | null
  created_at: string
  stopped_at: string | null
}

export interface PublishListResponse {
  services: PublishedService[]
  total: number
}

export interface PublishCreatePayload {
  model_id: number
  service_type: ServiceType
  config: Record<string, any>
}

export interface LogResponse {
  logs: string
}
