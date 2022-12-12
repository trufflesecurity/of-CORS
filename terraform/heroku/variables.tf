variable "heroku_app_name" {
  type = string
  description = "Name to assign to the Heroku app"
}

variable "host_domains" {
  type = list(string)
  description = "The list of host domains that need to be configured"
}