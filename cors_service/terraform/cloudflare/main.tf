terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.0"
    }
  }
}

resource "cloudflare_zone" "zone" {
  zone = var.zone
}

resource "cloudflare_record" "root_domain" {
  zone_id = cloudflare_zone.zone.id
  name = "@"
  value = var.root_cname_target
  type = "CNAME"
  proxied = true
}

resource "cloudflare_record" "wildcard_domain" {
  zone_id = cloudflare_zone.zone.id
  name = "*"
  value = var.wildcard_cname_target
  type = "CNAME"
  proxied = true
}
