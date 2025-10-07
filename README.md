# FilmLearn Backend

A Django REST API MVP for FilmLearn, an application that processes subtitle uploads, extracts words, assigns CEFR levels, stores word data, and generates PDF flashcards for language learning.

## Overview

This project implements a backend using Django and Django REST Framework (DRF) to handle subtitle uploads (.srt/.vtt files), process them to extract words with frequencies, assign Common European Framework of Reference (CEFR) levels using a local lexicon, and export filtered word lists as PDFs. Heavy processing is offloaded to Celery tasks with RabbitMQ as the broker.

### Key Features
- **Subtitle Upload & Processing**: Upload SRT/VTT files via REST API, which triggers asynchronous processing.
- **Word Extraction & Analysis**: Tokenize, normalize, and count word frequencies, then assign CEFR levels.
- **CEFR Mapping**: Use a local, deterministic CEFR lexicon for word classification.
- **PDF Flashcards**: Generate downloadable PDFs with word details, CEFR levels, and examples.
- **Authentication**: Email-based auth with django-allauth, including basic social OAuth stubs.
- **OpenAPI Documentation**: API docs via drf-spectacular/Swagger.
- **Celery Integration**: Asynchronous tasks for processing (extract words, assign CEFR, PDF generation, Anki sync stub).
- **Testing**: Comprehensive unit and integration tests using Django's unittest framework.
- **Docker Support**: Run locally with docker-compose (includes Postgres, RabbitMQ, Redis optional, NGINX optional).
- **CI/CD**: Pipeline for linting, testing, and building with GitHub Actions.

The MVP is built following TDD principles, prioritizing testable, correct code ready for production.

## Tech Stack
- **Python**: 3.11
- **Django**: 5.x
- **Django REST Framework**: For API building and serialization
- **Celery**: 5.x with RabbitMQ broker and optional Redis result backend
- **Databases**: SQLite (dev default), Postgres (prod/staging)
- **PDF Generation**: reportlab or weasyprint
- **Authentication**: django-allauth
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Linting/Formatting**: ruff/flake8, black
- **Testing**: Django unittest (`django.test.TestCase`, `SimpleTestCase`), coverage tool
- **Containerization**: Docker, docker-compose, optional Kubernetes
- **Dev Server**: gunicorn, NGINX reverse proxy

## Project Structure
- `filmlearn/`: Main Django project directory
  - `settings.py`: Project settings (env-driven via django-environ)
  - `urls.py`: URL patterns (add API routes under `/api/`)
  - `__init__.py`, `asgi.py`, `wsgi.py`: Standard Django files
- `manage.py`: Django management CLI
- Apps (to be implemented):
  - `users/` - User profiles, auth (models: UserProfile with CEFR level)
  - `content/` - Upload handling (models: SubtitleUpload)
  - `nlp/` - Tokenization, CEFR mapping (models: ExtractedWord; tasks: token processing)
  - `export/` - PDF generation (models: Flashcard; tasks: PDF gen, Anki push stub)
- `tests/`: Unit and integration tests
- `requirements.txt`: Python dependencies
- `.gitignore`, `.github/` (includes copilot instructions)
- `docker-compose.yml`: Dev environment (services: web, db, rabbitmq, celery, celery-beat)
- `Dockerfile`: For containerizing the app

All changes follow TDD: write tests first, implement small, testable functions, and use mocks for external services.

## Development Guidelines

### Key Files & Architecture
- **`.github/copilot-instructions.md`** - Detailed development instructions for AI agents
- **`project_prompt.md`** - Authoritative spec for features, endpoints, tests, and stack choices
- **`filmlearn/settings.py`** - Project settings (modify cautiously; follow environment-based patterns)
- **`filmlearn/urls.py`** - URL configuration (add API routes under `/api/`)

### Architecture & Data Flow
Upload processing follows this pattern:
1. POST `/api/subtitles/` stores `SubtitleUpload` and enqueues `extract_words_from_subtitle.delay()`
2. Celery worker processes the file (tokenizes, normalizes, counts frequencies)
3. Words are stored as `ExtractedWord` rows with CEFR mapping via local lexicon
4. PDF generation via POST `/api/subtitles/{id}/export-pdf/` enqueues `generate_pdf` task

**Celery Tasks**: `extract_words_from_subtitle`, `assign_cefr`, `generate_pdf`, `push_to_anki` (stub)

### Project Conventions
- **TDD-first**: Write tests before implementation. Tests should be deterministic; seed lexicon data or mock external services
- **Pure Functions**: Tokenization and CEFR mapping should be small, pure functions for easy unit testing
- **Celery Tasks**: Must be idempotent with retry and exponential backoff
- **Storage**: Use `MEDIA_ROOT/subtitles/` for dev; abstract for S3 compatibility later

## Prerequisites
- Python 3.11
- Docker and docker-compose (for full environment)
- PostgreSQL, RabbitMQ, Redis clients (if not using docker-compose)
- AnkiConnect (optional for Anki sync feature)

## Installation & Setup

1. **Clone the Repository**:
   ```
   git clone https://github.com/your-org/filmlearn-backend.git
   cd filmlearn-backend
   ```

2. **Set Up Virtual Environment** (optional but recommended):
   ```
   python -m venv env
   env\Scripts\activate  # On Windows
   # source env/bin/activate on Unix/Mac
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root (use `.env.example` or set manually):
   - `DEBUG=True` (for dev)
   - `SECRET_KEY=secure-key-here`
   - `DATABASE_URL=sqlite:///db.sqlite3` (use Postgres URL for prod)
   - `CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//` (RabbitMQ broker)
   - `REDIS_URL=redis://localhost:6379/0` (optional Redis result backend)
   - `OPENAI_API_KEY` or other keys if using external APIs (mocks recommended in tests)

**External Dependencies**:
   - **RabbitMQ**: Celery message broker (tests should mock `.delay` calls)
   - **Redis**: Optional result backend for Celery
   - **AnkiConnect**: Optional for Anki synchronization (stub implementation)
   - **CEFR Lexicon**: Local file or DB table (deterministic fallback to 'Unknown')

4. **Database**:
   ```
   python manage.py migrate
   ```

5. **Seed or Load CEFR Lexicon**:
   - Provide a local file or DB table for CEFR mappings (deteministic fallback to 'Unknown' for unmapped words).
   - Implement a management command or fixture to seed.

## Local Development
- **Run Django Dev Server**:
  ```
  python manage.py runserver
  ```
- **Run Celery Worker** (debugging):
  ```
  celery -A filmlearn worker --loglevel=info
  # For beat (schedules): celery -A filmlearn beat --loglevel=info
  ```
- **Using Docker Compose (Full Stack)**:
  ```
  docker-compose up --build
  ```
  This launches: web, postgres, rabbitmq, celery, celery-beat, optional nginx/redis.
  Healthchecks included for rabbitmq/postgres.

- **Migrations**:
  Always apply after model changes:
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```

## Usage

### API Endpoints
The backend provides REST endpoints for uploading subtitles, querying words, and exporting PDFs. Documentation is available at `/api/schema/` (OpenAPI/Swagger UI).

- **POST /api/auth/** - User registration/login (via django-allauth email + social stubs).

- **POST /api/subtitles/** - Upload a subtitle file (.srt/.vtt, multipart).
  - Request body: `{'file': file_stream}`
  - Response: `{id, status}` (status indicates processing phase).
  - Triggers `extract_words_from_subtitle.delay(subtitle_id)` Celery task.

- **GET /api/subtitles/{id}/** - Get upload metadata, including processing status.

- **GET /api/words/?level=B1&min_freq=1&page=1** - Paginated list of extracted words, filtered by CEFR level and minimum frequency.
  - Filters available: `level=` (e.g., A1-C2 or above), `min_freq`, pagination parameters.

- **POST /api/subtitles/{id}/export-pdf/** - Request PDF export for a subtitle's words.
  - Bodiesy: `{level: 'B1', include_phonetic: true, include_examples: false}` (filters and options).
  - Returns job ID; later, GET for status/PDF URL. Enqueues `generate_pdf` task.

- **POST /api/anki-sync/** - Sync selected words to Anki via AnkiConnect (stub implementation; mock in tests).

### Example API Request
```bash
# Upload subtitle
curl -X POST http://localhost:8000/api/subtitles/ \
  -F "file=@subtitle.srt"

# Query words for B1 level
curl "http://localhost:8000/api/words/?level=B1"

# Request PDF export
curl -X POST http://localhost:8000/api/subtitles/1/export-pdf/ \
  -H "Content-Type: application/json" \
  -d '{"level": "ALL", "include_grass_phonetic": true, "include_examples": false}'
```

## Testing

This project follows TDD principles with comprehensive test coverage:

### Test Examples
```python
# Unit test for subtitle upload task enqueueing
def test_upload_subtitle_queues_task(monkeypatch, api_client, user):
    monkeypatch.setattr('nlp.tasks.extract_words_from_subtitle.delay', lambda x: True)
    resp = api_client.post('/api/subtitles/', {'file': open('tests/fixtures/example.srt','rb')}, format='multipart')
    assert resp.status_code == 201

# PDF generation test
def test_pdf_contains_correct_columns():
    # Generate PDF with small dataset
    # Assert contains: word/CEFR/sample sentence columns
    pass
```

Run tests with: `python manage.py test`

### Testing Patterns
- Unit tests for tokenization edge cases (punctuation, hyphenation, apostrophes)
- Integration tests for API endpoints and Celery task enqueueing
- Mock external services (AnkiConnect, lexicon APIs) in tests
- Seed lexicon data or use deterministic fallbacks for consistent testing

## CI/CD

CI pipeline runs linting (ruff/flake8), Django test suite with coverage, and can be implemented with:

```yaml
# Example GitHub Actions workflow
- coverage run --source='.' manage.py test
- coverage report
- coverage xml
```

Follow black formatting and ruff/flake8 linting standards. Add pre-commit hooks for code quality enforcement.
