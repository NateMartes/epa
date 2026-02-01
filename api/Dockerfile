FROM python:3.11 AS test_runner

RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH

COPY . .
RUN /venv/bin/pip install -r requirements.txt
RUN /venv/bin/pip install --no-cache-dir .

RUN /venv/bin/pip install pytest

RUN /venv/bin/pytest tests

FROM python:3.11-slim AS service
WORKDIR /root/app/site-packages
COPY --from=test_runner /venv /venv
ENV PATH=/venv/bin:$PATH
