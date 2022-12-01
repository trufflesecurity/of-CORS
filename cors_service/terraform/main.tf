terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.0"
    }
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

module "heroku" {
  source = "./heroku"
  heroku_app_name = var.heroku_app_name
  host_domains = var.host_domains
}

module "cloudflare" {
  for_each = module.heroku.domain_map
  source = "./cloudflare"
  zone = each.key
  root_cname_target = each.value[0]
  wildcard_cname_target = each.value[1]
}