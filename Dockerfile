from alpine
run apk add --update curl bash nodejs npm python3 git make py3-pip
run curl https://cli-assets.heroku.com/install.sh | sh
RUN wget https://releases.hashicorp.com/terraform/1.3.6/terraform_1.3.6_linux_amd64.zip
RUN unzip terraform_1.3.6_linux_amd64.zip && rm terraform_1.3.6_linux_amd64.zip
RUN mv terraform /usr/bin/terraform
RUN cp `which python3` /usr/bin/python
copy of-CORS-main.zip .
run unzip of-CORS-main.zip
workdir /of-CORS-main
run pip install -r requirements.txt
workdir /of-CORS-main/terraform 
run terraform init
workdir /of-CORS-main
run alias python=python3
copy start.sh .
cmd ["./start.sh"]
