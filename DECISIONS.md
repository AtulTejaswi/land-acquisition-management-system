# DECISIONS.md — Architectural Decisions

## D1: Geometry Storage
**Decision:** Store GeoJSON as TEXT/JSONB in the database rather than using PostGIS GEOMETRY type directly in SQLAlchemy models.
**Rationale:** Simplifies the ORM layer while PostGIS can still be used via raw SQL for spatial queries. For the hackathon demo, this avoids complex GeoAlchemy2 type mapping issues while keeping the GIS features working.

## D2: Role-Based Routing
**Decision:** Single React app with client-side role-based routing using React Router v6.
**Rationale:** Avoids the complexity of separate SPAs per role. The JWT token carries the role claim, and the frontend redirects to the appropriate route prefix on login.

## D3: Auth Context over Redux
**Decision:** Use React Context (AuthContext) for auth state management instead of Redux.
**Rationale:** Per spec requirement ("lightweight auth/user context (no Redux)"). Auth state is simple (user + token) and doesn't need Redux's middleware complexity.

## D4: Mock AI Services
**Decision:** Implement AI modules as rule-based algorithms, not real ML.
**Rationale:** Per spec requirement for 48-hour hackathon. Algorithms use deterministic formulas from milestone data, objection counts, and circle rates. Clearly labeled as "AI Insights • Beta" in UI.

## D5: Single Backend Port
**Decision:** Backend serves both API and static files on port 8000.
**Rationale:** Simplifies Docker Compose setup and proxy configuration. Frontend dev server proxies /api and /uploads to backend.

## D6: Seed Data Approach
**Decision:** Python seed script with Faker-derived realistic Indian data rather than SQL fixtures.
**Rationale:** Allows generating 60+ parcels with proper UUID relationships and realistic coordinates. Seeded data includes 5 fully-progressed projects with complete audit trails for demo purposes.

## D7: File Storage
**Decision:** Local /uploads volume for hackathon, abstracted behind StorageService interface.
**Rationale:** Per spec: "abstracted behind a StorageService interface so it could swap to S3 later." Simple file I/O now, S3-ready architecture.
