package main

import (
	"fmt"
	"context"
	"runtime"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func chunk_records(k int, records []events.KafkaRecord) [][]events.KafkaRecord {
	
	output := [][]events.KafkaRecord{}
	
	chunk := []events.KafkaRecord{}
	chunkSize := -1
	for _, record := range records {
		if chunkSize + 1 == k {
			chunkSize = -1
			output = append(output, chunk)
			chunk = []events.KafkaRecord{}
		} else {
			chunkSize++
			chunk = append(chunk, record)
		}
	}
	
	if chunkSize + 1 == k && chunkSize != -1 {
		output = append(output, chunk)
	}
	
	return output
}

func process_records(records []events.KafkaRecord) {
	cores := runtime.NumCPU()
	recordsGrouped := chunk_records(cores, records)
	fmt.Println(recordsGrouped)
}

func handler(ctx context.Context, event events.KafkaEvent) error {
	
	for _, records := range event.Records {
		process_records(records)
	}
	
	return nil
}

func main() {
	lambda.Start(handler)
}
