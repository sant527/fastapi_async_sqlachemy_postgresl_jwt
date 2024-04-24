FROM python:3.12.3-bookworm as base

###########################################
# set environment variables
###########################################
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

###########################################
# install packages
###########################################
RUN : \
	&& apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y \
		--no-install-recommends \
		sudo \
		vim \
		tree \
		curl \
		wget \
		telnet \
		dnsutils \
		iproute2 \
		net-tools \
		default-mysql-client default-libmysqlclient-dev \
		postgresql-client \
		git \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/list/* \
	&& :

# dnsutils \ # for dig and nslookup
# iproute2 \ # for ip addr,ss command
# net-tools \ # for netstat -nr (show route table), netstat -ai (show network interfaces)

############################################
# create group and user
############################################

ARG UNAME=simha
ARG UID=1000
ARG GID=1000


RUN cat /etc/passwd

# create group
RUN groupadd -g $GID $UNAME

# create a user with userid 1000 and gid 100
RUN useradd -u $UID -g $GID -m -s /bin/bash $UNAME
# -m creates home directory

# change permissions of /home/simha to 1000:100
RUN chown $UID:$GID /home/simha

###########################################
# add sudo
###########################################

RUN cat /etc/sudoers
RUN echo "$UNAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN cat /etc/sudoers

###########################################
# change working dir and user
###########################################

USER $UNAME
RUN mkdir -p /home/$UNAME/direct
RUN mkdir -p /home/$UNAME/direct/debugxyz
RUN mkdir -p /home/$UNAME/direct/jupyter
RUN mkdir -p /home/$UNAME/.jupyter
RUN mkdir -p /home/$UNAME/.local/share/jupyter/kernels
RUN mkdir -p /home/$UNAME/app
WORKDIR /home/$UNAME/direct

RUN pwd


#############################################
# install pipenv
############################################
ENV PIPENV_VENV_IN_PROJECT=1

# ENV PIPENV_VENV_IN_PROJECT=1 is important: it causes the resuling virtual environment to be created as /app/.venv. Without this the environment gets created somewhere surprising, such as /root/.local/share/virtualenvs/app-4PlAip0Q - which makes it much harder to write automation scripts later on.

RUN pip install pipenv

# https://stackoverflow.com/a/76145132 (How to configure different dockerfile for development and production)
# https://stackoverflow.com/questions/51253987/building-a-multi-stage-dockerfile-with-target-flag-builds-all-stages-instead-o


#############################################
# install poetry
############################################

RUN pip install poetry


# https://stackoverflow.com/a/76145132 (How to configure different dockerfile for development and production)
# https://stackoverflow.com/questions/51253987/building-a-multi-stage-dockerfile-with-target-flag-builds-all-stages-instead-o

ENV PATH "$PATH:/home/simha/.local/bin"


FROM base as prod

RUN pip install --no-cache-dir pipenv

# ###########################################
# # Create virtualenv and Install requirements
# ###########################################
# COPY --chown=$UID:$GID requirements.txt .
# RUN python -m venv venv
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install --upgrade pip
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install snoop
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install cheap_repr
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install ipython
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install notebook
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install jupyter
# RUN . /home/$UNAME/direct/venv/bin/activate && pip install --no-cache-dir -r requirements.txt


############################################
# Application related
############################################

WORKDIR /home/$UNAME/app

# Install application into container
COPY --chown=$UID:$GID . .

# production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


# Create docker image as below
# docker build --platform linux/amd64 -t python_3_12_3_bookworm:latest --file Dockerfile .


# how to run a container with the current folder files
# hostfolder="$(pwd)"
# dockerfolder="/home/simha/app"
# docker run --rm -it \
#   --workdir ${dockerfolder} \
#   -v ${hostfolder}:${dockerfolder} \
#   --entrypoint='' \
#   --net="host" \
#   python_3_12_3_bookworm:latest /bin/bash


# docker run --rm -it --entrypoint='' --net="host" python_3_12_3_bookworm:latest /bin/bash


# How to Find My DNS Server IP Address in Linux
# grep "nameserver" /etc/resolv.conf
# dig git.txtbox.in

# see route table
# netstat -rn
# ip route