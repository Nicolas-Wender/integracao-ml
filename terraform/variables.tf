variable "project_id" {
  description = "ID do projeto GCP"
  type        = string
}

variable "region" {
  description = "Região do GCP"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Nome do serviço Cloud Run Job"
  type        = string
}

variable "container_image" {
  description = "URL da imagem Docker"
  type        = string
}

variable "env_vars" {
  description = "Mapa de variáveis de ambiente para o container"
  type        = map(string)
  default     = {}
}

variable "env_var_account_service_google" {
  description = "Variável de ambiente ACCOUNT_SERVICE_GOOGLE"
  type        = string
  default     = ""
}
