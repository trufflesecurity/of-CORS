terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.0"
    }
  }
}

variable "heroku_app_name" {
  description = "Name to assign to the Heroku app"
}

variable "cloudflare_api_token" {
  description = "API token to use for communication with Cloudflare"
}

variable "host_domains" {
  type = list(string)
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

resource "heroku_app" "cors_hunter" {
  name = var.heroku_app_name
  region = "us"
  acm = false

  config_vars = {
    "PROD" = "1"
  }
}

resource "heroku_addon" "cors_hunter_db" {
  app_id = heroku_app.cors_hunter.id
  plan = "heroku-postgresql:mini"
}

resource "heroku_build" "cors_hunter" {
  app_id = heroku_app.cors_hunter.id
  buildpacks = ["https://github.com/heroku/heroku-buildpack-python"]
  source {
    path = "package.tar.gz"
  }
}

resource "heroku_formation" "cors_hunter" {
  app_id = heroku_app.cors_hunter.id
  type = "web"
  quantity = 1
  size = "hobby"
  depends_on = [heroku_build.cors_hunter]
}

resource "heroku_domain" "this" {
  for_each = toset(var.host_domains)
  app_id = heroku_app.cors_hunter.id
  hostname = each.key
}

resource "cloudflare_zone" "this" {
  for_each = toset(var.host_domains)
  zone = each.key
}

resource "cloudflare_record" "this" {
  for_each = zipmap([for zone in cloudflare_zone.this: zone.id], [for domain in heroku_domain.this: domain.cname])
  zone_id = each.key
  name = "*"
  value = each.value
  type = "CNAME"
  proxied = false
}

output "cors_hunter_url" {
  value = "https://${heroku_app.cors_hunter.name}.herokuapp.com"
}
