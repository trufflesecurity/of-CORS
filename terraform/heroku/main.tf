terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
  }
}

resource "heroku_app" "of_cors" {
  name = var.heroku_app_name
  region = "us"
  acm = false

  config_vars = {
    "PROD" = "1"
  }
}

resource "heroku_addon" "of_cors_db" {
  app_id = heroku_app.of_cors.id
  plan = "heroku-postgresql:mini"
}

resource "heroku_build" "of_cors" {
  app_id = heroku_app.of_cors.id
  buildpacks = ["https://github.com/heroku/heroku-buildpack-python"]
  source {
    path = "package.tar.gz"
  }
}

resource "heroku_formation" "of_cors" {
  app_id = heroku_app.of_cors.id
  type = "web"
  quantity = 1
  size = "hobby"
  depends_on = [heroku_build.of_cors]
}

resource "heroku_domain" "top_domain" {
  for_each = toset(var.host_domains)
  app_id = heroku_app.of_cors.id
  hostname = each.key
}

resource "heroku_domain" "wild_sub_domain" {
  for_each = toset(var.host_domains)
  app_id = heroku_app.of_cors.id
  hostname = "*.${each.key}"
}