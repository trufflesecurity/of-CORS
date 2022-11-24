
## Running Things

1. [Install Terraform](https://developer.hashicorp.com/terraform/downloads)
2. [Obtain a Heroku API token](https://devcenter.heroku.com/articles/using-terraform-with-heroku#obtaining-an-authorization-token)


```bash
heroku login
heroku authorizations:create --description terraform-cors-hunter
# Need to create a variable to use with Terraform
# Email can come from heroku whoami
export HEROKU_API_KEY=ff5fdf7d-d36e-4c20-a9ce-a6f53f5e240a HEROKU_EMAIL=cegrayson3@gmail.com
```
