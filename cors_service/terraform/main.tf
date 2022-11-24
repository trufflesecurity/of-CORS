terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
  }
}

variable "heroku_app_name" {
  description = "Name to assign to the Heroku app"
}

resource "heroku_app" "cors_hunter" {
  name = var.heroku_app_name
  region = "us"

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

output "cors_hunter_url" {
  value = "https://${heroku_app.cors_hunter.name}.herokuapp.com"
}
