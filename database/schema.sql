-- ============================================================
-- Product Groups
-- XML:
--   <ProductGroup>TRANSPORTBETON</ProductGroup>
--   <CCG Desc="TRANSPORTBETON" Id="500000085"/>
-- ============================================================

CREATE TABLE product_groups (
    id BIGSERIAL PRIMARY KEY,

    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);


-- ============================================================
-- Commodity Groups
-- Recursive category tree
--
-- Example:
-- 62 Stoffe
-- └── 620 Beton
--     └── 620001 Lieferbeton, Ortbeton
--         └── 6200013 Beton C30/37
-- ============================================================

CREATE TABLE commodity_groups (
    id BIGSERIAL PRIMARY KEY,

    -- XML CommodityGroupID
    code TEXT NOT NULL UNIQUE,

    -- XML CommodityGroupDescription
    description TEXT,

    -- Recursive hierarchy
    parent_id BIGINT
        REFERENCES commodity_groups(id)
        ON DELETE RESTRICT,

    -- XML Xref
    source_ref TEXT,

    -- XML CostCode
    cost_code TEXT,

    -- XML UoM
    unit TEXT,

    -- XML group-level calculation values
    discount NUMERIC(12, 4),
    wastage NUMERIC(12, 4),
    estimation_factor NUMERIC(12, 4),
    regie_factor NUMERIC(12, 4),

    addition_1 TEXT,
    addition_2 TEXT,
    addition_3 TEXT,
    addition_4 TEXT,

    remarks TEXT,

    product_group_id BIGINT
        REFERENCES product_groups(id)
        ON DELETE SET NULL,

    fixed_hours BOOLEAN
);


-- ============================================================
-- Commodities
-- Actual materials / resources used for matching
-- ============================================================

CREATE TABLE commodities (
    id BIGSERIAL PRIMARY KEY,

    -- XML CommodityID
    code TEXT NOT NULL UNIQUE,

    -- XML CommodityDescription
    -- nullable because some Commodities have no description
    description TEXT,

    commodity_group_id BIGINT NOT NULL
        REFERENCES commodity_groups(id)
        ON DELETE RESTRICT,

    product_group_id BIGINT
        REFERENCES product_groups(id)
        ON DELETE SET NULL,

    -- XML Xref
    source_ref TEXT,

    -- XML UoM
    unit TEXT,

    -- Some entries contain CostCodeUoM
    cost_code TEXT,
    cost_code_unit TEXT,

    weight NUMERIC(16, 4),
    weight_unit TEXT,

    volume NUMERIC(16, 4),
    volume_unit TEXT,

    addition_1 TEXT,
    addition_2 TEXT,
    addition_3 TEXT,
    addition_4 TEXT,

    remarks TEXT,

    external_price_update BOOLEAN,
    selected BOOLEAN,
    fixed_hours BOOLEAN,

    change_date DATE,
    change_user TEXT
);


-- ============================================================
-- Commodity Prices
--
-- Current XML contains one CommodityPrice per Commodity,
-- but the database intentionally supports 1:N.
-- ============================================================

CREATE TABLE commodity_prices (
    id BIGSERIAL PRIMARY KEY,

    commodity_id BIGINT NOT NULL
        REFERENCES commodities(id)
        ON DELETE CASCADE,

    -- XML PrUnit
    unit_price NUMERIC(16, 4) NOT NULL,

    -- XML CUR
    currency TEXT NOT NULL,

    discount NUMERIC(16, 4),
    freight_costs NUMERIC(16, 4),
    miscellaneous NUMERIC(16, 4),
    wastage NUMERIC(16, 4),

    modified_date DATE,
    modified_user TEXT
);


-- ============================================================
-- Estimate Prices
--
-- Examples:
--   Typ="Estimation"
--   Typ="DWTMRate"
--
-- price_type is intentionally not an ENUM because future
-- files may contain additional types.
-- ============================================================

CREATE TABLE estimate_prices (
    id BIGSERIAL PRIMARY KEY,

    commodity_id BIGINT NOT NULL
        REFERENCES commodities(id)
        ON DELETE CASCADE,

    -- XML EstimatePrice @Typ
    price_type TEXT NOT NULL,

    factor NUMERIC(16, 4),
    price NUMERIC(16, 4) NOT NULL,
    currency TEXT NOT NULL,

    modified_date DATE,
    modified_user TEXT,

    fixed_price BOOLEAN
);


-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX idx_commodity_groups_parent_id
    ON commodity_groups(parent_id);

CREATE INDEX idx_commodity_groups_product_group_id
    ON commodity_groups(product_group_id);

CREATE INDEX idx_commodities_group_id
    ON commodities(commodity_group_id);

CREATE INDEX idx_commodities_product_group_id
    ON commodities(product_group_id);

CREATE INDEX idx_commodities_unit
    ON commodities(unit);

CREATE INDEX idx_commodities_cost_code
    ON commodities(cost_code);

CREATE INDEX idx_commodity_prices_commodity_id
    ON commodity_prices(commodity_id);

CREATE INDEX idx_estimate_prices_commodity_id
    ON estimate_prices(commodity_id);

CREATE INDEX idx_estimate_prices_price_type
    ON estimate_prices(price_type);