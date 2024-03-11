SELECT
  title,
  YEAR
FROM
  movies
WHERE
  title LIKE 'Harry Potter%'
ORDER BY
  YEAR ASC;