# Event Posting App (EPA)

[![Last Commit](https://img.shields.io/github/last-commit/NateMartes/epa)](https://github.com/NateMartes/epa/commits)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
[![AWS](https://custom-icon-badges.demolab.com/badge/AWS-%23FF9900.svg?logo=aws&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#)
[![Go](https://img.shields.io/badge/Go-%2300ADD8.svg?&logo=go&logoColor=white)](#)
[![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?logo=mongodb&logoColor=white)](#)
[![Redis](https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](#)
[![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=fff)](#)

Safety is important and as technology gets more sophisticated, so should our ability to stay safe. Our project EPA, the Event Posting App, will be a mobile application that allows users to post about safety concerns in local areas to ensure that users know what is going on in their community. Users can subscribe to categories and specific tags within those categories and be notified as soon as an event occurs.

## Table of Contents
- [Useful Commands](#useful-commands)
- [System Architecture](#system-architecture)
  - [System Architecture Choices](#system-architecture-choices)
- [Quick Start](#quick-start)
- [The Client](#the-client)
- [The API](#the-api)
  - [Adding Endpoints](#adding-endpoints)
- [The Database](#the-database)
  - [Configuration Syntax](#configuration-syntax)
- [User Timeline Caching](#user-timeline-caching)
  - [Connecting to the Cahce](#connecting-to-the-cahce)
- [The Post Queue](#the-post-queue)
- [The Notifier, The Post Ingestor, and The User Cache Loader](#the-notifier-the-post-ingestor-and-the-user-cache-loader)
- [Deployments and Environments](#deployments-and-environments)
  - [Terraform](#terraform)
- [Technical Resources](#technical-resources)
  - [Frameworks & Languages](#frameworks--languages)
  - [Infrastructure & Tools](#infrastructure--tools)
  - [Databases & Messaging](#databases--messaging)

## Useful Commands

Set environment variables from `.env`:
```bash
export $(grep -v '^#' .env | xargs)
```

Unset environment variables from `.env`:
```bash
unset $(grep -v '^#' .env | sed -E 's/(.*)=.*/\1/' | xargs)
```

Using .env file for `docker`:
```bash
docker compose --env-file /path/to/.env <more commands here>
```

Run AWS Lambda function locally:
```bash
sudo sam build && sudo sam local invoke
```

## System Architecture

The overview of EPA can appear as such:

![EPA System Architecture](./system_diagram/event-posting-app.png "EPA System Architecture")

### System Architecture Choices

Some chocies we want to highlight are the following:
- **Contract First API**: The main EPA API uses a Contract First approach, so that we can always serve a client apporiately.
- **Cache Aside Pattern**: The application focuses on a Cache Aside Pattern, meaning we cache posts for users for that access is faster. We include 2 caching layers, a client side and a server side.

## Quick Start
If you have Docker installed, then you can use the `docker compose` plugin for starting services:
```bash
docker compose up
```

Some microservices (like the cache_loader, notify_service) operate using AWS Serverless Application Model (see below)

## The Client
The Client uses React Native Expo to build an application for web and moblie. You can start the application
using npm

```bash
npm install && npm start
```

This by default will generate a QR code for use on [Expo Go](https://expo.dev/go). If you would like to simulate a moblie device on your machine, you can use [Android Studio](https://developer.android.com/studio). Make Sure an Android Device Emulator is running with Expo Go installed and then run:

```bash
npm start --android
```

*Note*: Development is tested for web and moblie (specfically Android). We do not test for Apple devices but since Expo can complie to apple devices, it is expected to work.

## The API

The EPA API uses a Contract-First approach, meaning endpoints are auto generated from an OpenAPI spec using the `openapi-generator-cli` tool:

Installing the tool uses `npm`:
```bash
npm install -g @openapitools/openapi-generator-cli
```

Then you can generate the API endpoints like such:
```bash
openapi-generator-cli generate \
-i openapi.yaml \
-g python-fastapi \
-o . \ --additional-properties=packageName=epa_api,fastapiImplementationPackage=api_implementation
```

The service methods (the actual logic of the API) is stored within the `./api/src/epa_api/api_implementation` directory.

### Adding Endpoints
When adding endpoints, update the `openapi.yml` file with the new endpoint information and run the previous command. Then add the new method to the `./api/src/epa_api/api_implementation/` directory. The function that the API will call **MUST** be defined by the `operationId`

Example:
```yaml
paths:
  /status:
    get:
      operationId: get_status # HERE: function should be called `get_status`
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Status"
          description: API is healthy
      summary: Check API health
```

Then you can add the code in the `./api/src/epa_api/api_implementation/` directory:
```python
from epa_api.apis.default_api_base import BaseDefaultApi
from epa_api.models.status import Status

class EpaAPIImplementation(BaseDefaultApi):
    async def get_status(self) -> Status:
        return Status(status="healthy", version="1.0.0")
```

## The Database
The database uses MongoDB for storing information such as `users`, `posts`, `session_tokens`, `categories`, and more.
The database is initialized using a Python script and the `config.json` file found within the `./database` directory.
The database `docker-compose.yml` file includes a database initializer to add the defined collections.
The default database is called `epa_database`. This cannot be configured

### Configuration Syntax

The configuration file uses JSON format syntax to define needed database collections.
Some fields can be included to add indexes to MongoDB collections:
```json
{
  "collections": [
    {
      "name": "users",
      "indexes": [
        {"field": "user_id", "unique": true},
        {"field": "google_id", "unique": true}
      ]
    },
    {
      "name": "session_tokens",
      "indexes": [
        {"field": "session_token", "expireAfterSeconds": 604800},
      ]
    },
  ]
```

- The `unqiue` field says that in this collection index, this field will always be unqiue.
- The `expireAfterSeconds` field sats that in this collection index, this field will expire in some amount of time in seconds.

## User Timeline Caching
To ensure a user can see a post very quickly, we preform caching on post and store them into a Redis database.
The provider for this service is Upstash. You can locally test this database using the `docker-compose.yml` file in the
`./user_timeline_post_cache` directory to simulate Upstash.

### Connecting to the Cahce
In both cases, local or production, you can use a redis client to connect to the redis database.
Example in Go:
```go
func connectToRedis() *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:     "epa-redis:6379",
		Password: "",
		DB:       0,
	})
}
```

## The Post Queue
The post queue uses Kafka to store posts for later consumers to pick up (e.g post_ingestor, cache_loader).
You can use `docker-compose` to spin up a local Kafka instance.

The defined Kafka topics include:
- `new_posts`

The defined Kafka consumer groups include:
- `post_ingestor_consumer`
- `cache_loader_consumer`
- `notify_service_consumer`

More Kafka topics can be added to the local instance by updating the `init.sh` script:
```bash
/opt/kafka/bin/kafka-topics.sh --create --topic my-topic --bootstrap-server epa_kakfa_broker:9092
```

## The Notifier, The Post Ingestor, and The User Cache Loader
These services are grouped together as they are all very similar.
They run as AWS Lamdba functions and are triggered via Kafka Events.
They all also use AWS SAM to be tested and deployed into the cloud.
The only difference lies in that the post ingestor is written in Python, while the others are in Go.
They can all be tested by executing:
```bash
sam build && sam local invoke
```
You may need to use `sudo` if Docker premissions require it.

The flow of the Lamdba functions are:
- **The Notifier**: On Kafka event, for each record, for each user that pertains to this record, send them a moblie notification
- **The Cache Loader**: On Kafka event, for each record, for each user that pertains to this record, update their cache line with that post
- **The Post Ingestor**: On Kafka event, for each record, insert the record into the global database


## Deployments and Environments
EPA has 2 main environments for running Github Actions:
- `Development`: Used for pull requests to test code before merging
- `Production`: Used for pushes to `main` to update cloud production resources

### Terraform
Terraform is primarly used for deploying resources into the cloud. The process for writing a Terraform Github Action for deployment is:
1. Run a terraform plan setup in the pull request
2. Run a terraform apply in a push to `main`

You can use [this](https://developer.hashicorp.com/terraform/tutorials/automation/github-actions) document to ensure your workflows follows
good standards.

## Technical Resources

### Frameworks & Languages

* [FastAPI](https://fastapi.tiangolo.com/) - Modern, high-performance web framework for Python.
* [Go (Golang)](https://go.dev/) - Statically typed, compiled language for efficient cloud services.
* [Python](https://www.python.org/) - Primary language for the API and Ingestor.

### Infrastructure & Tools

* [AWS Lambda](https://aws.amazon.com/lambda/) - Serverless compute for event-driven tasks.
* [AWS SAM (Serverless Application Model)](https://aws.amazon.com/serverless/sam/) - Toolkit for building serverless applications.
* [Docker](https://www.docker.com/) - Containerization for local development.
* [OpenAPI Generator](https://openapi-generator.tech/) - Tool for generating API clients and server stubs.
* [Terraform](https://developer.hashicorp.com/terraform) - Used for deploying resources into the cloud.

### Databases & Messaging

* [MongoDB](https://www.mongodb.com/) - NoSQL document database for primary storage.
* [Redis](https://redis.io/) - In-memory data structure store used as a cache.
* [Upstash](https://upstash.com/) - Serverless Redis provider used in production.
* [Apache Kafka](https://kafka.apache.org/) - Distributed event streaming platform.

---