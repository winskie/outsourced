CREATE TABLE IF NOT EXISTS liked_photos
(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT,
	author TEXT,
	photo_url TEXT,
	link TEXT,
	tags TEXT,
	user_id TEXT
);