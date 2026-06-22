# Yoga Courses

## Getting Started
 
Clone the repository:
 
```bash
git clone https://github.com/GFTSA1/YogaMain.git
```
or 
```bash
git clone https://github.com/GFTSA1/YogaMain.git .
```

Copy the environment file and fill in the required values:
 
```bash
cp .env.example .env
```

Then fill in the required values in `.env` (ask the backend team for credentials):
 
| Variable                    | Description                              |
|-----------------------------|------------------------------------------|
| `DATABASE_URL`              | PostgreSQL connection string             |
| `AWS_ACCESS_KEY_ID`         | AWS access key                           |
| `AWS_SECRET_ACCESS_KEY`     | AWS secret key                           |
| `AWS_BUCKET_NAME`           | S3 bucket name for file storage          |
| `CLOUDFRONT_DOMAIN`         | CloudFront distribution domain           |
| `CLOUDFRONT_KEY_ID`         | CloudFront key pair ID                   |
| `CLOUDFRONT_PRIVATE_KEY_PATH` | Path to CloudFront private key (default: `./keys/private_key.pem`) |
| `REDIS_URL`                 | Redis connection string (default: `redis://localhost:6379/0`) |
| `JWT_SECRET`                | Secret key for JWT token signing         |
| `GOOGLE_CLIENT_ID`          | Google OAuth client ID                   |
 


## Running the Application
 
```bash
docker compose up --build
```
 
The API will be available at `http://localhost:8000`.
 
Interactive API docs (Swagger UI) are at `http://localhost:8000/docs`.
 
## Stopping the Application
 
```bash
docker compose down
```
