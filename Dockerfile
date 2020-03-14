FROM centos:8
     
LABEL amparo pascual

ENV FLASK_APP "main.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG "true"
   
RUN yum update -y
RUN yum --enablerepo=extras install -y epel-release && yum clean all
RUN yum install -y python3 python3-devel python3-pip mariadb-devel gcc gcc-c++ glibcdevel make
RUN mkdir /app

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

COPY . /app
    
CMD flask run --host=0.0.0.0