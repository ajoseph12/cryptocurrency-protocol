from P2P_connections import PeerComm
import sqlite3
from sqlite3 import Error

class PeerCommTracker(PeerComm):



    def return_all_active_peers(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT IP,Port FROM Peers WHERE LastUpdated > datetime('now','-10 minutes') LIMIT 20;")

        rows = cur.fetchall()
        list_of_peers = []
        for row in rows:
            list_of_peers.append(row)
            return list_of_peers

    def create_connection(self, db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return None