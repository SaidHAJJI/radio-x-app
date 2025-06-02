# Application Web pour Lecture d'Images Radio X

## Testing

To run the tests, ensure the application containers are running (e.g., via `docker-compose up -d`).

### Backend Tests

1. Open a shell in the running backend container:
   ```bash
   docker-compose exec backend bash
   ```
2. Once inside the container, run pytest:
   ```bash
   pytest
   ```

### Frontend Tests

1. Open a shell in the running frontend container:
   ```bash
   docker-compose exec frontend sh
   ```
2. Once inside the container, run the test script (this will be added in a subsequent step):
   ```bash
   npm test
   ```
