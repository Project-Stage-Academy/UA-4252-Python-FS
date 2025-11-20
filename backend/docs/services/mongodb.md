# MongoDB & Mongo Express Setup

This project includes local MongoDB and Mongo Express services.  
Both containers are bound to **localhost** and require authentication to prevent external access.

Ports are restricted:

- **MongoDB**: `127.0.0.1:27017`:`27017`
- **Mongo Express**: `127.0.0.1:8081`:`8081`

This ensures MongoDB and Mongo Express are accessible **only from the local machine**.

## Environment Variables

Defined in `backend/.env` (see `.env.template`):

```
MONGO_DB_NAME=...
MONGO_INITDB_ROOT_USERNAME=...
MONGO_INITDB_ROOT_PASSWORD=...
MONGO_HOST=...
MONGO_PORT=...
ME_CONFIG_MONGODB_ADMINUSERNAME=...
ME_CONFIG_MONGODB_ADMINPASSWORD=...
ME_CONFIG_BASICAUTH_USERNAME=...
ME_CONFIG_BASICAUTH_PASSWORD=...
```

### MongoDB Authentication

- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`

When these variables are provided, the MongoDB automatically creates a root user.
This user has full access and is required to connect to MongoDB.

### Mongo Express Authentication

- `ME_CONFIG_MONGODB_ADMINUSERNAME`
- `ME_CONFIG_MONGODB_ADMINPASSWORD`

These variables must match the MongoDB root credentials above.
Mongo Express uses them to authenticate against the MongoDB server.

### Mongo Express Basic Auth

- `ME_CONFIG_BASICAUTH_USERNAME`
- `ME_CONFIG_BASICAUTH_PASSWORD`

These variables login to the Mongo Express web UI.
This is separate from MongoDB authentication and protects the dashboard.

### Backend Variables

- `MONGO_DB_NAME`
- `MONGO_HOST`
- `MONGO_PORT`

Used by the backend to construct the MongoDB connection string.

