terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "streamguard" {
  name     = "streamguard-rg"
  location = "germanywestcentral"
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "random_password" "pg_admin" {
  length           = 20
  special          = true
  override_special = "_%@"
}

resource "azurerm_postgresql_flexible_server" "streamguard" {
  timeouts {
    create = "10m"
  }
  lifecycle {
    ignore_changes = [zone]
  }
  name                   = "streamguard-pg-${random_string.suffix.result}"
  resource_group_name    = azurerm_resource_group.streamguard.name
  location               = "italynorth"
  version                = "16"
  administrator_login    = "streamguard"
  administrator_password = random_password.pg_admin.result
  storage_mb             = 32768
  sku_name               = "GP_Standard_D2s_v3"
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_my_ip" {
  name             = "allow-my-computer"
  server_id        = azurerm_postgresql_flexible_server.streamguard.id
  start_ip_address = var.my_ip
  end_ip_address   = var.my_ip
}

resource "azurerm_postgresql_flexible_server_database" "streamguard_db" {
  name      = "streamguard"
  server_id = azurerm_postgresql_flexible_server.streamguard.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

resource "azurerm_container_registry" "streamguard" {
  name                = "streamguardacr${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.streamguard.name
  location            = "italynorth"
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_kubernetes_cluster" "streamguard" {
  name                = "streamguard-aks"
  resource_group_name = azurerm_resource_group.streamguard.name
  location            = "italynorth"
  dns_prefix          = "streamguardaks"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                    = azurerm_kubernetes_cluster.streamguard.kubelet_identity[0].object_id
  role_definition_name            = "AcrPull"
  scope                           = azurerm_container_registry.streamguard.id
  skip_service_principal_aad_check = true
}