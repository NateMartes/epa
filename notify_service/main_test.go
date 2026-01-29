package main

import (
	"testing"
	"github.com/aws/aws-lambda-go/events"
)

func TestHandler(t *testing.T) {
	testCases := []struct {
		name          string
		request       events.APIGatewayProxyRequest
		expectedBody  string
		expectedError error
	}{
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
		})
	}
}
