-- CREATE INDEX IF NOT EXISTS user_email_idx ON "user"(email);
-- CREATE INDEX IF NOT EXISTS user_created_at_idx ON "user"(created_at);
--  
-- depends: 

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL, 
    created_at TIMESTAMP DEFAULT NOW(),
    recipes_per_week INTEGER DEFAULT 1,
    serving INTEGER DEFAULT 1,
    send_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recipe (
    id TEXT PRIMARY KEY, 
    canonical_url TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    instructions TEXT NOT NULL, 
    title TEXT NOT NULL,
    total_time INTEGER NOT NULL,
    yields INTEGER
);

CREATE TABLE ingredient (
    recipe_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    unit TEXT,
    quantity FLOAT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    PRIMARY KEY (recipe_id, name),
    FOREIGN KEY(recipe_id) REFERENCES recipe(id)
);


CREATE TABLE leaflet_entry (
    id SERIAL PRIMARY KEY,
    leaflet_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    recipe_id TEXT,
    user_id INTEGER,
    FOREIGN KEY(recipe_id) REFERENCES recipe(id),
    FOREIGN KEY(user_id) REFERENCES "user"(id)
);
