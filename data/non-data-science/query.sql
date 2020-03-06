
SELECT projects.id, projects.name, projects.url, projects.description, projects.language, COUNT(watchers.user_id) AS stars
    FROM `ghtorrent-bq.ght_2018_04_01.projects` AS projects
    LEFT JOIN `ghtorrent-bq.ght_2018_04_01.watchers` AS watchers
    ON projects.id = watchers.repo_id
    WHERE ((forked_from IS NULL)
    AND (projects.language = 'Python')
    AND (description IS NOT NULL AND description != '')

    AND (
    (
        (
        (
            (LOWER(description) NOT LIKE '%machine learn%') AND
            (LOWER(description) NOT LIKE '%machine-learn%') AND
            (LOWER(description) NOT LIKE '%data sci%') AND
            (LOWER(description) NOT LIKE '%data-sci%') AND

            (LOWER(description) NOT LIKE '%big data%') AND
            (LOWER(description) NOT LIKE '%big-data%') AND
            (LOWER(description) NOT LIKE '%large data%') AND
            (LOWER(description) NOT LIKE '%large-data%') AND
            (LOWER(description) NOT LIKE '%data analy%') AND
            (LOWER(description) NOT LIKE '%data-analy%') AND
            (LOWER(description) NOT LIKE '%deep learn%') AND
            (LOWER(description) NOT LIKE '%deep-learn%') AND

            (LOWER(description) NOT LIKE '%data model%') AND
            (LOWER(description) NOT LIKE '%data-model%') AND

            (LOWER(description) NOT LIKE '%artificial intel%') AND
            (LOWER(description) NOT LIKE '%artificial-intel%') AND

            (LOWER(description) NOT LIKE '%mining%') AND
            (LOWER(description) NOT LIKE '%topic modelling%') AND
            (LOWER(description) NOT LIKE '%topic-modelling%') AND

            (LOWER(description) NOT LIKE '%natural language pro%') AND
            (LOWER(description) NOT LIKE '%natural-language-pro%') AND

            (LOWER(description) NOT LIKE '%nlp%') AND
            (LOWER(description) NOT LIKE '%data frame%') AND
            (LOWER(description) NOT LIKE '%data proces%') AND
            (LOWER(description) NOT LIKE '%ml%') AND

            (LOWER(description) NOT LIKE '%tensorflow%') AND
            (LOWER(description) NOT LIKE '%tensor flow%') AND
            (LOWER(description) NOT LIKE '%tensor-flow%') AND

            (LOWER(description) NOT LIKE '%theano%') AND
            (LOWER(description) NOT LIKE '%caffe%') AND
            (LOWER(description) NOT LIKE '%keras%') AND

            (LOWER(description) NOT LIKE '%scikit-learn%') AND
            (LOWER(description) NOT LIKE '%kaggle%') AND
            (LOWER(description) NOT LIKE '%spark%') AND

            (LOWER(description) NOT LIKE '%hadoop%') AND
            (LOWER(description) NOT LIKE '%mapreduce%') AND
            (LOWER(description) NOT LIKE '%hdfs%') AND

            (LOWER(description) NOT LIKE '%neural net%') AND
            (LOWER(description) NOT LIKE '%neural-net%')
        )
        )
    )
    )
    )

    GROUP BY projects.id, projects.url, projects.name, projects.description, projects.language
    HAVING stars >= 80;

