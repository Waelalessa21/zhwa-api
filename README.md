# zhwa-api

## Deploy to Railway

1) Push this repo to GitHub.

2) Create a new project on Railway and select this repo.

3) Railway will detect Python. Ensure the following:
- Service uses the provided `Procfile` (process type `web`).
- `PORT` is provided by Railway automatically.

4) Configure environment variables in Railway → Variables:
- `DATABASE_URL` (recommended: PostgreSQL from Railway, e.g. `postgresql://USER:PASSWORD@HOST:PORT/DB`)
- `SECRET_KEY` (strong random string)
- `ALGORITHM` (default `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (optional)
- `UPLOAD_DIR` (defaults to `uploads`)
- `MAX_FILE_SIZE` (optional)
- `ALLOWED_IMAGE_TYPES` (optional)

5) Database
- Add a Railway PostgreSQL plugin and copy its `DATABASE_URL` into the service variables.
- The app uses SQLAlchemy with `DATABASE_URL` automatically.

6) Static uploads
- Files in `uploads/` are stored on ephemeral filesystem. For production, use a persistent store (e.g., S3) and update code to save there.

7) Build and deploy
- Railway will install from `requirements.txt` and start with `uvicorn app.main:app --host 0.0.0.0 --port ${PORT}`.

Health endpoints: `/` and `/health`.
