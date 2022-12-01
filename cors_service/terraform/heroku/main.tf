terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
  }
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

resource "heroku_domain" "top_domain" {
  for_each = toset(var.host_domains)
  app_id = heroku_app.cors_hunter.id
  hostname = each.key
}

resource "heroku_domain" "wild_sub_domain" {
  for_each = toset(var.host_domains)
  app_id = heroku_app.cors_hunter.id
  hostname = "*.${each.key}"
}