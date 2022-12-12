output "domain_map" {
  value = {
    for k, domain in heroku_domain.top_domain : k => [
      domain.cname,
      heroku_domain.wild_sub_domain[k].cname,
    ]
  }
  description = "A mapping of zones to the DNS records that must be configured to correctly route traffic to the Heroku application."
}