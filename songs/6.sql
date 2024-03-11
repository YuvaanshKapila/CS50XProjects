SELECT s. name FROM songs s
JOIN artists a on s.artist_id = a.id
WHERE a.name = 'Post Malone';