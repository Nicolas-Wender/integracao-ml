terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "" # será definido via -backend-config
    prefix = "state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_v2_job" "worker" {
  name     = var.service_name
  location = var.region

  template {
    parallelism    = "1"        // Número de execuções em paralelo
    task_count     = "1"        // Número total de tarefas

    template {
      max_retries = "0"          // Número de novas tentativas por tarefa com falha
      timeout     = "3600s"      // Tempo limite da tarefa (ex: "3600s" para 1h)

      containers {
        image = var.container_image
        resources {
          limits = {
            cpu    = "1"                 
            memory = "1Gi"            
          }
        }
        env {
          name  = "ACCOUNT_SERVICE_GOOGLE"
          value = var.env_var_account_service_google
        }
        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }
}
