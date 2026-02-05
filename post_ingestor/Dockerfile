FROM public.ecr.aws/docker/library/python:3.11-slim as build-image

WORKDIR /src

# Install OS-level build dependencies for confluent-kafka
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into a folder we can copy into the Lambda image
COPY requirements.txt ./
RUN pip install -r requirements.txt -t /src/python

COPY main.py ./

FROM public.ecr.aws/lambda/python:3.11
# Copy dependencies + function code into Lambda task root
COPY --from=build-image /src/python ${LAMBDA_TASK_ROOT}/
COPY --from=build-image /src/main.py ${LAMBDA_TASK_ROOT}/
# Lambda handler
CMD ["main.lambda_handler"]
