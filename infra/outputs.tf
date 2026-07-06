output "pg_host" {
  value = azurerm_postgresql_flexible_server.streamguard.fqdn
}

output "pg_admin_password" {
  value     = random_password.pg_admin.result
  sensitive = true
}

output "acr_login_server" {
  value = azurerm_container_registry.streamguard.login_server
}