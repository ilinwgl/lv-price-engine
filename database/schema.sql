-- ==============================================================================
-- Database Schema
-- ==============================================================================

CREATE TABLE IF NOT EXISTS public.supplier_prices (
    id BIGSERIAL PRIMARY KEY,

    category VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    unit VARCHAR(100) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,

    supplier VARCHAR(255),
    supplier_location VARCHAR(255),

    valid_from DATE,
    valid_to DATE
);