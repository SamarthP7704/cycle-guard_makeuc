-- CycleGuard AI Database Schema for Supabase (PostgreSQL)

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('dropoff', 'pickup')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    person_embedding JSONB NOT NULL,
    person_bbox JSONB NOT NULL,
    cycle_bbox JSONB,
    image_path TEXT,
    match_result JSONB,
    alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on event_type for faster queries
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);

-- Create index on timestamp for faster sorting
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);

-- Create index on event_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_events_event_id ON events(event_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (optional, for Supabase)
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations" ON events
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Example query to get recent dropoff events
-- SELECT * FROM events 
-- WHERE event_type = 'dropoff' 
-- ORDER BY timestamp DESC 
-- LIMIT 10;

-- Example query to get events with match results
-- SELECT * FROM events 
-- WHERE event_type = 'pickup' 
-- AND match_result->>'is_same_person' = 'false'
-- ORDER BY timestamp DESC;

