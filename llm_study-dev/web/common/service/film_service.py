import enum
from common.database.call_commector import get_connector

########################################################
# 비지니스 영역
########################################################
class SQLs(enum.Enum):
  select_actor_by_title = (enum.auto(), """
    select
      f1.title
      , count(f2.actor_id) as actor_cnt
    from film f1
    left join film_actor f2 
      on f1.film_id = f2.film_id
    group by f1.film_id
    ;
  """, "영화별 배우 수 조회")


def excution_by_sql(sql_enum=SQLs.select_actor_by_title.name):
  conn = get_connector()
  sql = SQLs[sql_enum].value[1]
  df_data = conn.query(sql, ttl="10m")
  title_data = SQLs[sql_enum].value[2]
  return df_data, title_data

