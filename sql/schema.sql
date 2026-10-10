CREATE TABLE IF NOT EXISTS public.events (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ,
    event_type TEXT NOT NULL,
    username TEXT,
    source_ip INET,
    destination_ip INET,
    port INTEGER,
    raw_message TEXT,
    source TEXT DEFAULT 'api',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
