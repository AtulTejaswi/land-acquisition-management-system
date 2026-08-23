-- NLAMS Schema Reference (PostgreSQL + PostGIS)
-- This file is for reference only; actual migrations are managed by Alembic

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Helper: updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- States
CREATE TABLE states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    region VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Districts
CREATE TABLE districts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_id UUID REFERENCES states(id) NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(state_id, name)
);

-- Villages
CREATE TABLE villages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id UUID REFERENCES districts(id) NOT NULL,
    tehsil VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Roles
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id UUID REFERENCES roles(id) NOT NULL,
    state_id UUID REFERENCES states(id),
    district_id UUID REFERENCES districts(id),
    agency_name VARCHAR(200),
    is_active BOOLEAN DEFAULT true NOT NULL,
    last_login_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_state ON users(state_id);
CREATE INDEX idx_users_district ON users(district_id);
CREATE INDEX idx_districts_state ON districts(state_id);
CREATE INDEX idx_villages_district ON villages(district_id);

-- Ministries
CREATE TABLE ministries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) NOT NULL
);

-- Project Categories
CREATE TABLE project_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    ministry_id UUID REFERENCES ministries(id) NOT NULL,
    category_id UUID REFERENCES project_categories(id) NOT NULL,
    implementing_agency_id UUID REFERENCES users(id),
    state_id UUID REFERENCES states(id) NOT NULL,
    district_id UUID REFERENCES districts(id),
    description TEXT,
    dpr_document_id UUID,
    estimated_budget NUMERIC(18,2),
    estimated_land_required_hectares NUMERIC(12,3),
    priority VARCHAR(20) DEFAULT 'medium' NOT NULL,
    current_stage VARCHAR(50) DEFAULT 'project_proposal' NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL,
    start_date TIMESTAMPTZ,
    target_completion_date TIMESTAMPTZ,
    created_by UUID REFERENCES users(id) NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_projects_state_district_status ON projects(state_id, district_id, status);
CREATE INDEX idx_projects_ministry ON projects(ministry_id);
CREATE INDEX idx_projects_category ON projects(category_id);
CREATE INDEX idx_projects_agency ON projects(implementing_agency_id);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_name_ft ON projects USING GIN(name gin_trgm_ops);

-- Land Parcels
CREATE TABLE land_parcels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    survey_number VARCHAR(50) NOT NULL,
    village_id UUID REFERENCES villages(id) NOT NULL,
    district_id UUID REFERENCES districts(id) NOT NULL,
    state_id UUID REFERENCES states(id) NOT NULL,
    area_hectares NUMERIC(12,4),
    geom GEOMETRY(Polygon, 4326),
    land_type VARCHAR(30) DEFAULT 'agricultural' NOT NULL,
    ownership_status VARCHAR(20) DEFAULT 'private' NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_parcels_project ON land_parcels(project_id);
CREATE INDEX idx_parcels_village ON land_parcels(village_id);
CREATE INDEX idx_parcels_district ON land_parcels(district_id);
CREATE INDEX idx_parcels_state ON land_parcels(state_id);
CREATE INDEX idx_parcels_geom ON land_parcels USING GIST(geom);

-- Full-text search indexes
CREATE INDEX idx_land_owners_name_ft ON land_owners USING GIN(full_name gin_trgm_ops);
