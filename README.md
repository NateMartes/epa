# Event Posting App (EPA)

---
## The EPA API

The EPA API uses a Contract-First approach, meaning endpoints are auto generated from an OpenAPI spec using the `openapi-generator-cli` tool:

Installing the tool uses `npm`:
```bash
npm install -g @openapitools/openapi-generator-cli
```

Then you can generate the API endpoints like such:
```bash
openapi-generator-cli generate \
-i openapi.yml \
-g python-fastapi \
-o ./api \ --additional-properties=packageName=epa_api,fastapiImplementationPackage=api_implementation
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

---
## The Database
The database uses MongoDB to store a `users` collection and `posts` collection.
The database is initialized using a Python script and the `config.json` file found within the `./database` directory.
You can spin up the database using `docker compose`. The initializer will add the needed collections from the `config.json` file.

---
## User Timeline Caching
To ensure a user can see a post very quickly, we preform caching on post and store them into a Redis database.
The provider for this service is Upstash. You can locally test this database using the `docker-compose.yml` file in the
`./user_timeline_post_cache` directory to simulate Upstash.

---
## The Post Queue

---
## The Notifier

---
## The Post Ingestor

___
## The User Cache Loader

---
## The EPA Moblie App