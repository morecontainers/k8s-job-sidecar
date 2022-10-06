FROM		alpine:3.16
RUN		apk add --no-cache python3 py3-requests
WORKDIR 	/app
COPY		app.py ./
ENTRYPOINT 	["python3","-u","app.py"]
