# Flask_API_Store

Python, Flask, Marshmallow, Docker, Redis

# Factory pattern
Used in Flask app construction.

# Marshmallow schemas
Used to maintain the relationship between Items and Stores nested and requirements to exist.


# Run instructions
 #### docker commands
1. we will create the image of the API
    ```docker
    docker build -t flask-api .
    ```
2. Run a Redis container
    ```docker
    docker run -d --name redis-container -p 6379:6379 redis
    ```
3. Run the API container
    ```docker
    docker run -dp 5000:5000 --network host flask-api
    ```