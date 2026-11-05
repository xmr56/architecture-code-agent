-- Space Fractions persisted entities (PostgreSQL 14+).

CREATE TABLE IF NOT EXISTS questions (
  id SERIAL PRIMARY KEY,
  category TEXT NOT NULL DEFAULT 'fractions',
  prompt TEXT NOT NULL,
  options TEXT[] NOT NULL DEFAULT '{}',
  answer TEXT NOT NULL, -- reduced fraction string "a/b" or whole number
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS games (
  id SERIAL PRIMARY KEY,
  state TEXT NOT NULL DEFAULT 'Playing'
    CHECK (state IN ('Playing', 'Paused', 'GameOver')),
  game_state JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_games_state ON games (state);
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions (category);
