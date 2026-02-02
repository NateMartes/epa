package main

import (
	"sync"
	"context"
	"runtime"
	"time"
	"log"
	"encoding/base64"
	"encoding/json"
	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"github.com/redis/go-redis/v9"
)

// A User in the MongoDB database. We only include the fields we need
type User struct {
	Id string `bson:"user_id,omitempty"`
	Subscribed []string `bson:"subscribed,omitempty"`
}

// A Post that would come from the Kafka queue
type Post struct {
	PostId int `json:"post_id,omitempty"`
	Title string `json:"title,omitempty"`
	CategoryName string `json:"category_name,omitempty"`
	CategorySlug string `json:"category_slug,omitempty"`
}

/*
 * The chunk function takes a list of type T and splits them into k chunks.
 * If the length of the list is less than k, then k will just be the length of the list
 * 
 * Args:
 * 	k (int): Number of chunks
 * 	slice ([]T): A list of lists, each of type T.
 * 
 * Returns:
 *  ([][]T): The chunked list
 */
func chunk[T any](k int, slice []T) [][]T {
	if k < 0 {
		return [][]T{}
	}
	
	if len(slice) < k {
		k = len(slice)
	}
	
	var output [][]T
	for _ = range k {
		output = append(output, []T{})
	}
	
	currChunk := -1
	for _, item := range slice {
		currChunk = currChunk + 1 % k
		output[currChunk] = append(output[currChunk], item)
	}
	
	return output
}

/*
 * The connectToMongoDB function connects to a MongoDB instance, using the environment
 * variables known to the program
 * 
 * Returns:
 * 	(*mongo.Client, error): The MongoDB client, an error if an error occurs
 */
func connectToMongoDB() (*mongo.Client, error) {
	uri := "mongodb://test:test@epa-db:27017/"
	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI(uri).SetServerAPIOptions(serverAPI)
	return mongo.Connect(opts)
}

/*
 * The getUserCollection function takes a MongoDB client and gets the
 * user collection from the MongoDB collection.
 * 
 * Args:
 * 	client (*mongo.Client): The MongoDB database client
 * 
 * Returns:
 * 	*mongo.Collection: The user collection on the MongoDB instance
 */
func getUserCollection(client *mongo.Client) *mongo.Collection {
	
	epaDb := "epa_database"
	db := client.Database(epaDb)
	epaUsersCollection := "users"
	return db.Collection(epaUsersCollection)
}

/*
 * The getUsers function gets users from the user collection, accepting a filter.
 * 
 * Args:
 * 	collection (*mongo.Collection): The collection containing users
 * 	filter (any): A filter for the query to get users from the collection
 */
func getUsers(collection *mongo.Collection, filter any) *mongo.Cursor {
	
	searchCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	res, err := collection.Find(searchCtx, filter)
	if err != nil {
		panic(err)
	}
	return res
}

/*
 * The getUsersWithSubscriptions function gets users from the user collection that are
 * subscribed to a post category.
 * 
 * Returns:
 * 	*mongo.Cursor: A cursor pointing to the users
 */
func getUsersWithSubscriptions() *mongo.Cursor {
	
	// Connect to MongoDB database
	client, err := connectToMongoDB()
	if err != nil {
		panic(err)
	}
	
	// Disconnect when done
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    	defer cancel()
		if err = client.Disconnect(ctx); err != nil {
			panic(err)
		}
	}()
	
	// Get user collection in database
	users_collection := getUserCollection(client)
	
	// Get all users who have subscriptions
	return getUsers(users_collection, bson.D{{
	    Key: "subscribed", 
	    Value: bson.D{{Key: "$exists", Value: true}},
	}})
}

/*
 * The mongoCursorToSlice function takes a mongo.Cursor object and coverts it
 * into a slice of some type T. Each item in the resulting slice is an item in the MongoDB cursor
 * 
 * Args:
 * 	cursor (*mongo.Cursor): The cursor to convert into a slice
 * 
 * Returns:
 * 	[]T: The resulting slice
 */
func mongoCursorToSlice[T any](cursor *mongo.Cursor) []T {
	// Close the cursor when finised
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    	defer cancel()
     	if err := cursor.Close(ctx); err != nil {
      		panic(err)
      	}
	}()
	
	cursorCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	var output []T
	for cursor.Next(cursorCtx) {
		var current T
		if err := cursor.Decode(&current); err != nil {
			log.Fatal(err)
		}
		output = append(output, current)
	}
	
	if err := cursor.Err(); err != nil {
		log.Fatal(err)
	}
	
	return output
}

/*
 * The getPostFromBase64 takes a base64 encoded strings and returns a Post object.
 * 
 * Args:
 * 	base64String (string): A base64 encoded string
 * 
 * Returns:
 * 	(Post, error): The resulting post, an error if an error occured 
 */
func getPostFromBase64(base64String string) (Post, error) {
	
	// Define a buffer to place the decoded base64 string
	buf := make([]byte, base64.StdEncoding.DecodedLen(len(base64String)))
	bytesWritten, err := base64.StdEncoding.Decode(buf, []byte(base64String))
	decodedRecord := buf[:bytesWritten]
	if err != nil {
		return Post{}, err
	}
	
	// Parse the string into the Post struct
	var post Post
	if err := json.Unmarshal(decodedRecord, &post); err != nil {
		return Post{}, err
	}
	
	return post, nil
}

func connectToRedis() *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:     "0.0.0.0:6379",
		Password: "", // no password
		DB:       0,  // use default DB
		Protocol: 2,
	})
}

func updateCacheLine(userId string, post Post, rdb *redis.Client) error {
	
	// Get user cache line if it exists, if not, cache line is []
	// append post to cache line
	// insert update
	return nil
}

/*
 * The UpdateUserCacheLines takes a list of records, and a list of users, and updates user cache lines
 * in a serverless Redis cache. This method assumes that the users list is not conflicting with
 * any other Go routines.
 * 
 * Args:
 * 	records ([]events.KafkaRecord): A list of records to possibly insert into user cache lines
 * 	users (*[]User): A list of users that may have their cache lines update
 * 	wg (*sync.WaitGroup): A Waitgroup this fucntion is apart of
 */
func updateUserCacheLines(records []events.KafkaRecord, users *[]User, wg *sync.WaitGroup) {
	defer wg.Done()

	rdb := connectToRedis()
	for _, record := range records {

		post, err := getPostFromBase64(record.Value)
		if err != nil {
			log.Fatal(err)
			continue
		}
		log.Println(post)
		
		for _, user := range *users {
			for _, userCategoryName := range user.Subscribed {
				if userCategoryName == post.CategoryName {
					err := updateCacheLine(user.Id, post, rdb)
					if err != nil { log.Fatal(err) }
				}
			}
		}
	}
	
	// Connect to Redis cache
	// For each user:
	// If the the user is subscribed to our record, add post to user cache line
}

/*
 * The process_records function takes a list of Kakfka records and processes them,
 * adding them into user caches as needed.
 * 
 * Args:
 * 	records ([]events.KafkaRecord): A list of records to process
 */
func process_records(records []events.KafkaRecord) {
	
	// We split the users into K groups, where K is the number of cores
	cores := runtime.NumCPU()
	users := mongoCursorToSlice[User](getUsersWithSubscriptions())
	usersChunked := chunk(cores, users)

	// Then we process each chunk with the list of records from Kafka.
	// We could give each record to the entire list of users, but that would be more inefficent
	// and we would also have to handled for collisions between threads and user cache line accesses
	var wg sync.WaitGroup
	for i := range usersChunked {
		wg.Add(1)
		go updateUserCacheLines(records, &usersChunked[i], &wg)
	}
	wg.Wait()
}

func handler(ctx context.Context, event events.KafkaEvent) error {
	
	expectedRecord := "cache_loader_consumer-0"
	for topicParition, records := range event.Records {
		if topicParition == expectedRecord {
			process_records(records)
		}
	}
	
	return nil
}

func main() {
	lambda.Start(handler)
}
