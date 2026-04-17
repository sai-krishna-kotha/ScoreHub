# Multi-Sport Live Scoring & Tournament Platform

A backend system for managing tournaments and tracking live sports matches in real time. The platform supports multiple sports (currently Cricket and Football), role-based access control, and event-driven scoring with WebSocket-based live updates.


## Overview

This project combines tournament management (similar to CricHeroes) with real-time score consumption (similar to Cricbuzz/Crex). It allows users to create tournaments, manage teams and players, and update live match events with immediate propagation to connected clients.

The system is designed with extensibility and scalability in mind, using an event-driven architecture and modular sport-specific logic.


## Features

### Tournament Management
- Create and manage tournaments
- Multi-sport support (Cricket, Football)
- Configurable tournament settings

### Team & Player Management
- Create teams within tournaments
- Add players using email-based onboarding
- Automatic user creation for new players
- Prevent duplicate player assignments per tournament

### Role-Based Access Control (RBAC)
- Roles scoped per tournament:
  - Organizer
  - Admin
  - Scorer
  - Viewer
- Secure access to operations:
  - Organizer/Admin: manage teams, players, matches
  - Scorer: update live match events
  - Viewer: read-only access

### Match Management
- Create matches between teams
- Match lifecycle:
  - Scheduled → Live → Completed
- Enforced validation for team and tournament consistency

### Event-Driven Scoring Engine
- Store match actions as events instead of static scores
- Dynamically compute scores from event history
- Supports replay and future analytics

### Real-Time Updates
- WebSocket-based communication
- Match-specific channels for broadcasting score updates
- Low-latency live score propagation to clients

### Modular Sport Architecture
- Separate scoring engines per sport
  - CricketEngine
  - FootballEngine
- Easily extendable to new sports without schema changes


## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Real-Time Communication**: WebSockets
- **Validation**: Pydantic


## Architecture

### High-Level Flow


    Client → FastAPI API → PostgreSQL
                    ↓
                Event Engine
                    ↓
            WebSocket Broadcast
                    ↓
                  Clients


### Core Design Principles

- Event-driven architecture for scoring
- Per-tournament RBAC for access control
- Modular sport plugins for extensibility
- Stateless authentication using JWT
- Separation of concerns (models, schemas, APIs, services)


## Database Design (Simplified)

### Users
- id
- email (unique)
- password (nullable for invited users)
- name
- is_active

### Tournaments
- id
- name
- sport_id
- organizer_id
- configuration fields

### Teams
- id
- name
- tournament_id

### TeamPlayers
- id
- user_id
- team_id
- tournament_id
- unique(user_id, tournament_id)

### Matches
- id
- tournament_id
- team_a_id
- team_b_id
- status

### MatchEvents
- id
- match_id
- event_type
- payload (JSON)
- timestamp

### TournamentRoles
- user_id
- tournament_id
- role
- unique(user_id, tournament_id)


## API Overview

### Authentication
- `POST /auth/signup`
- `POST /auth/login`

### Tournaments
- `POST /tournaments/`
- `GET /tournaments/`

### Teams
- `POST /teams/`

### Player Onboarding
- `POST /players/add-by-email`

### Matches
- `POST /matches/`
- `PUT /matches/{id}/start`
- `PUT /matches/{id}/complete`

### Events (Scoring)
- `POST /events/`
- `GET /events/{match_id}/score`

### Roles
- `POST /roles/assign`

### WebSocket
- `ws://localhost:8000/ws/{match_id}`


## Real-Time Flow

1. Scorer sends event via API (`POST /events`)
2. Event stored in database
3. Score recalculated using sport-specific engine
4. Updated score broadcast via WebSocket
5. Clients receive updates instantly


## Player Onboarding Design

- Players are identified by email
- If user exists:
  - directly mapped to team
- If user does not exist:
  - system creates an inactive user
  - assigns to team
- User can activate account later

This ensures identity consistency while maintaining a smooth onboarding experience.


## Security

- JWT-based authentication
- All modifying endpoints are protected
- RBAC enforced per tournament
- Database constraints ensure data integrity


## Future Improvements

- Full RBAC with permission mapping
- Email invitation and account activation flow
- Caching and snapshotting for score computation
- Notifications and alerts
- Player statistics and leaderboards
- Frontend dashboard (React)


## Getting Started

### 1. Clone Repository

```
git clone &lt;your-repo-url&gt;

cd &lt;project-folder%gt;
```

### 2. Setup Environment

```
python -m venv venv
```
```
venv\Scripts\activate # Windows
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Database

Update connection string in:

app/core/config.py

### 5. Run Server
```
uvicorn app.main:app --reload
```
