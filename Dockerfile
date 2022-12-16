FROM alpine:latest

# Install dependencies

RUN apk add --update curl bash nodejs npm python3 git make py3-pip
RUN curl https://cli-assets.heroku.com/install.sh | sh
RUN wget https://releases.hashicorp.com/terraform/1.3.6/terraform_1.3.6_linux_amd64.zip
RUN unzip terraform_1.3.6_linux_amd64.zip && rm terraform_1.3.6_linux_amd64.zip
RUN mv terraform /usr/bin/terraform

# Copy over the code and install the remaining dependencies

RUN mkdir -p /of-cors
COPY terraform/package.tar.gz /of-cors
RUN cd /of-cors && tar -xvf package.tar.gz
WORKDIR "/of-cors"
RUN pip install -r requirements.txt
RUN cd terraform && terraform init

# Set the start script

CMD ["./files/start.sh"]
