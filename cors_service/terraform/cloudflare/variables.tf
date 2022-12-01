variable "zone" {
  type = string
  description = "The highest level zone (ie: domain) to create records for"
}

variable "root_cname_target" {
  type = string
  description = "The DNS CNAME record that the root domain should be mapped to in Heroku"
}

variable "wildcard_cname_target" {
  type = string
  description = "The DNS CNAME record that the wildcard domain should be mapped to in Heroku"
}
