# Containerized API image:

FROM debian:latest

LABEL Author="Eli Harper"


RUN apt update -y && apt upgrade -y ; \
    apt install python3 python3-venv python3-pip -y ;

RUN pip3 install --upgrade pip

RUN mkdir /app

WORKDIR /app/

# Add the program files and their supporting env info:
COPY ["./__init__.py", "./Consumer/", "./pb/", "./Producer/", "./cmf/", "./protos/" , "./log/", "./requirements.txt", "/app/"]

RUN ls -la /app

# Start the virtualenv:
RUN cd /app && pip3 install -r ./requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
# Add this section to the previous line if running on the PME:

RUN ls -la /app ; pwd

EXPOSE 5001

RUN cd /app
# Run the program:

CMD [ "python3", "-m", "Consumer.gRPC.grpc_server" ]