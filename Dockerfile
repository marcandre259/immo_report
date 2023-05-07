FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml ./
RUN conda env create -f environment.yml 

SHELL ["conda", "run", "-n", "immo_report", "/bin/bash", "-c"]

COPY . .