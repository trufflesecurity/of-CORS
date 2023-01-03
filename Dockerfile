FROM alpine
RUN apk add --update curl bash nodejs npm python3 git make py3-pip
RUN curl https://cli-assets.heroku.com/install.sh | sh
RUN wget https://releases.hashicorp.com/terraform/1.3.6/terraform_1.3.6_linux_amd64.zip
RUN unzip terraform_1.3.6_linux_amd64.zip && rm terraform_1.3.6_linux_amd64.zip
RUN mv terraform /usr/bin/terraform
RUN cp `which python3` /usr/bin/python
RUN git clone https://github.com/trufflesecurity/of-CORS
WORKDIR /of-CORS
RUN pip install -r requirements.txt
WORKDIR /of-CORS-main/terraform 
RUN terraform init
WORKDIR /of-CORS-main
RUN alias python=python3
COPY start.sh .
RUN chmod +x ./start.sh
CMD ["./start.sh"]
