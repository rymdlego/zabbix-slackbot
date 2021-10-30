FROM python:3.9-alpine as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV USER=slack
ENV UID=12345
ENV GID=23456

FROM base AS python-deps

# Install pipenv
RUN pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
WORKDIR /home/$USER
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "$(pwd)" \
    --uid "$UID" \
    "$USER"

USER $USER

# Install application into container
COPY zabbix-slackbot/. .

# Run the application
ENTRYPOINT ["python"]
CMD ["zabbixbot.py"]
