from __init__ import cur, conn 

cur.execute("DELETE FROM Photo")
cur.execute("DELETE FROM Trip")
cur.execute("DELETE FROM TripUser")
cur.execute("DELETE FROM TripLocation")
conn.commit()
