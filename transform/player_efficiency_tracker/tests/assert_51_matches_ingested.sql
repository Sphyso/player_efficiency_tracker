-- fails if the number of matches in dim_matches isn't exactly 51
select count(*) as match_count
from {{ ref('dim_matches') }}
having count(*) != 51