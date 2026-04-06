package main

import (
	"sync"
	"context"
	"runtime"
	"time"
	"log"
	"os"
	"fmt"
	"errors"
	"strings"
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

// A list of posts, commonly used for user caches
type PostList struct {
	Posts []Post `json:"posts,omitempty"`
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
	hostname := os.Getenv("EPA_MONGODB_HOSTNAME")
	port := os.Getenv("EPA_MONGODB_PORT")
	username := os.Getenv("EPA_MONGODB_USERNAME")
	password := os.Getenv("EPA_MONGODB_PASSWORD")
	if hostname == "" || port == "" || username == "" || password == "" {
		return nil, errors.New("Not all MongoDB environment variables set or are empty")
	}
	
	uri := fmt.Sprintf("mongodb://%s:%s@%s:%s/", username, password, hostname, port)
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
	dbName := os.Getenv("EPA_MONGODB_DATABASE_NAME")
	if dbName == "" {
		panic("Environment variable EPA_MONGODB_DATABASE_NAME not set or is empty")
	}
	db := client.Database(dbName)
	userCollection := os.Getenv("EPA_MONGODB_USER_COLLECTION")
	if userCollection == "" {
		panic("Environment variable EPA_MONGODB_USER_COLLECTION not set or is empty")
	}
	return db.Collection(userCollection)
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
 * The getFromBase64 takes a base64 encoded strings and returns an object of type Tas.
 * 
 * Args:
 * 	base64String (string): A base64 encoded string
 * 
 * Returns:
 * 	(T, error): The resulting object, an error if an error occured 
 */
func getFromBase64[T any](base64String string) (T, error) {
	
	// Define a buffer to place the decoded base64 string
	buf := make([]byte, base64.StdEncoding.DecodedLen(len(base64String)))
	bytesWritten, err := base64.StdEncoding.Decode(buf, []byte(base64String))
	decodedRecord := buf[:bytesWritten]
	if err != nil {
		var val T
		return val, err
	}
	
	// Parse the string into the Post struct
	var val T
	if err := json.Unmarshal(decodedRecord, &val); err != nil {
		return val, err
	}
	
	return val, nil
}

/*
 * The connectToRedis connects to a known redis instance
 * 
 * Returns:
 * 	*redis.Client: The connection to the redis server
 */
func connectToRedis() *redis.Client {
	hostname := os.Getenv("EPA_REDIS_HOSTNAME")
	port := os.Getenv("EPA_REDIS_PORT")
	password := os.Getenv("EPA_REDIS_PASSWORD")
	if hostname == "" || port == "" || password == "" {
		panic("Environment variables for Redis not all set or are empty")
	}
	return redis.NewClient(&redis.Options{
		Addr:     hostname + ":" + port,
		Password: password,
		DB:       0,
	})
}

/*
 * The getUserCacheLineValue gets a cache line in a redis server using
 * a user id as the key.
 * 
 * Args:
 * 	userId (string): A user id
 * 	rdb (*redis.Client): A connection to a redis instance
 * 
 * Returns:
 * 	(string, error): The value of the cache line as a string, an error if an error occured
 */
func getUserCacheLineValue(userId string, rdb *redis.Client) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	return rdb.Get(ctx, userId).Result()
}

/*
 * The setUserCacheLineValue sets a cache line in a redis server using
 * a user id as the key.
 * 
 * Args:
 * 	userId (string): A user id
 * 	val (string): The new value of the cache line
 * 	exprAt (time.Duration): The time to live of the cache line
 * 	rdb (*redis.Client): A connection to a redis instance
 * 
 * Returns:
 * 	(string, error): The value of the cache line as a string, an error if an error occured
 */
func setUserCacheLineValue(userId string, val string, exprAt time.Duration, rdb *redis.Client) (error) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	return rdb.Set(ctx, userId, val, exprAt).Err()
}

/*
 * The updateCacheLine function takes a user's cache line and adds a
 * post struct to it in JSON format. This may either set the cache line of a
 * user to just the new post, or append the post to the cache line.
 * 
 * Args:
 * 	userId (string): The user id
 * 	post (Post): The post to add to the cache line
 * 	rdb (*redis.Client): A connection to a redis instance
 * 
 * Returns:
 * 	error: If an error occured
 */
// NEW SIGNATURE: accept authorId
func updateCacheLine(userId string, authorId string, post Post, rdb *redis.Client) error {
    valString, err := getUserCacheLineValue(userId, rdb)
    if err == redis.Nil {
        valString = "{\"posts\": []}"
    } else if err != nil {
        return err
    }
    
    var val PostList
    err = json.Unmarshal([]byte(valString), &val)
    if err != nil {
        return err
    }
    
    //Skip if user is the author of the post
    if userId != authorId {
        val.Posts = append(val.Posts, post)
        jsonEncoded, err := json.Marshal(val)
        if err != nil {
            return err
        }
        return setUserCacheLineValue(userId, string(jsonEncoded), time.Hour, rdb)
    }
    return nil  //Skip caching for author's own feed
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
        // Decode Kafka key to get author's userId
        authorIdBytes, err := base64.StdEncoding.DecodeString(record.Key)
        if err != nil {
            log.Printf("Failed to decode Kafka key: %v", err)
            continue
        }
        authorId := string(authorIdBytes)
        
        post, err := getFromBase64[Post](record.Value)
        if err != nil {
            log.Printf("Failed to decode post: %v", err)
            continue
        }
        
        for _, user := range *users {
            for _, userCategorySlug := range user.Subscribed {
                if userCategorySlug == post.CategorySlug {
                    //Pass authorId to updateCacheLine
                    if err := updateCacheLine(user.Id, authorId, post, rdb); err != nil {
                        log.Printf("Failed to update cache for user %s: %v", user.Id, err)
                    }
                }
            }
        }
    }
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
	
	expectedTopic := os.Getenv("EPA_KAFKA_TOPIC_CACHELOADER_NAME")
	if expectedTopic == "" {
		return errors.New("Environment variable EPA_KAFKA_TOPIC_CACHELOADER_NAME not set or empty")
	}
	for topicParition, records := range event.Records {
		if strings.Contains(topicParition, expectedTopic) {
			process_records(records)
		}
	}
	
	return nil
}

func main() {
	lambda.Start(handler)
}
