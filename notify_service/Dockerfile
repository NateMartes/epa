FROM golang:1.25.6-alpine3.23

WORKDIR /cache_loader
COPY go.mod .
RUN go mod tidy

COPY main.go .

CMD ["go", "run", "main.go"]

