### set the base image to Ubuntu
FROM ubuntu:16.04

### File author / maintainer
MAINTAINER Jihoon Kim "j5kim@ucsd.edu"

### change a working directory to /opt
WORKDIR /opt

### update the repository source list and install dependent packages
RUN apt-get update -y                                            && \
    apt-get install -y git                                       && \
    git clone https://github.com/jihoonkim/DataMed-Admixture.git && \
    bash /opt/DataMed-Admixture/provision/install_iadmix.sh      && \
    bash /opt/DataMed-Admixture/provision/install_R.sh  

### change a working directory to /opt/ancestry
WORKDIR /opt/ancestry
