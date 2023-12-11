# # Configure the Azure provider
# terraform {
#   required_providers {
#     azurerm = {
#       source  = "hashicorp/azurerm"
#       version = "~> 3.0.0"
#     }
#   }
#   required_version = ">= 0.14.9"
# }

# provider "azurerm" {
#   features {}
# }

# # Create the resource group
# resource "azurerm_resource_group" "rg" {
#   name     = "definal-rg"
#   location = "eastus"
# }

# # Create the Linux App Service Plan
# resource "azurerm_app_service_plan" "appserviceplan" {
#   name                = "definal-asp"
#   location            = azurerm_resource_group.rg.location
#   resource_group_name = azurerm_resource_group.rg.name

#   sku {
#     tier = "Standard"
#     size = "S1"
#   }

#   kind = "Linux"
#   reserved = true
# }

# # Create the web app, pass in the App Service Plan ID
# resource "azurerm_app_service" "webapp" {
#   name                = "NBAStatsDashboard"
#   location            = azurerm_resource_group.rg.location
#   resource_group_name = azurerm_resource_group.rg.name
#   app_service_plan_id = azurerm_app_service_plan.appserviceplan.id
#   https_only          = true

#   site_config {
#     always_on        = true
#     linux_fx_version = "DOCKER|shawir/nbastats:final"
#   }

#   app_settings = {
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#     "WEBSITES_PORT"                       = "50505"
#     "DOCKER_REGISTRY_SERVER_URL"          = "https://index.docker.io/v1"
#   }
# }

# Configure the Azure provider
terraform {
    required_providers {
        azurerm = {
            source  = "hashicorp/azurerm"
            version = "~> 3.0.0"
        }
    }
    required_version = ">= 0.14.9"
}

provider "azurerm" {
    features {}
}

# Create a new resource group
resource "azurerm_resource_group" "rg_final" {
  name     = "DEFinal"  # Change this to a unique name
  location = "Japan East"
}

# Create the Linux App Service Plan
resource "azurerm_app_service_plan" "appserviceplan" {
  name                = "FinalDataEngineering2023OsamaAhmed"
  location            = azurerm_resource_group.rg_final.location
  resource_group_name = azurerm_resource_group.rg_final.name

  sku {
    tier = "PremiumV3"
    size = "P1v3"
  }

  kind     = "Linux"
  reserved = true
}

# Create the web app, pass in the App Service Plan ID
resource "azurerm_app_service" "webapp" {
  name                = "NBAStatsDash"  # Change this to a unique name
  location            = azurerm_resource_group.rg_final.location
  resource_group_name = azurerm_resource_group.rg_final.name
  app_service_plan_id = azurerm_app_service_plan.appserviceplan.id
  https_only          = true

  site_config {
    always_on        = true
    linux_fx_version = "DOCKER|shawir/nbadash:final"
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "WEBSITES_PORT"                       = "8080"
    "DOCKER_REGISTRY_SERVER_URL"          = "https://index.docker.io/v1"
  }
}


# # Create the resource group
# resource "azurerm_resource_group" "rg" {
#     name     = "DE"
#     location = "Japan East"
# }

# # Create the Linux App Service Plan
# resource "azurerm_app_service_plan" "appserviceplan" {
#     name                = "FallDataEngineering2023OsamaAhmed"
#     location            = azurerm_resource_group.rg.location
#     resource_group_name = azurerm_resource_group.rg.name

#     sku {
#         tier = "PremiumV3"
#         size = "P1v3"
#     }

#     kind     = "Linux"
#     reserved = true
# }

# # Create the web app, pass in the App Service Plan ID
# resource "azurerm_app_service" "webapp" {
#   name                = "NBAStatsDash"  # Change this to a unique name
#   location            = azurerm_resource_group.rg.location
#   resource_group_name = azurerm_resource_group.rg.name
#   app_service_plan_id = azurerm_app_service_plan.appserviceplan.id
#   https_only          = true

#   site_config {
#     always_on        = true
#     linux_fx_version = "DOCKER|shawir/nbastats:final"
#   }

#   app_settings = {
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#     "WEBSITES_PORT"                       = "8080"
#     "DOCKER_REGISTRY_SERVER_URL"          = "https://index.docker.io/v1"
#   }
# }