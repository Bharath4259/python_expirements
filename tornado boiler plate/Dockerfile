FROM continuumio/anaconda3:latest

ENV APP_HOME /test-me

WORKDIR $APP_HOME
COPY . ./

RUN apt-get update
RUN apt install -y curl nodejs npm
RUN apt-get install -y g++ gcc libpq-dev python3-dev libsm6 libxrender1 libfontconfig1 unixodbc-dev git
RUN curl https://npmjs.org/install.sh | sh
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -

RUN apt update && apt -y install yarn
RUN pip install -r requirements.txt

EXPOSE 9999
CMD ["python", "app.py"]

