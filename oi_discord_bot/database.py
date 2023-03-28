import hashlib
import random
import sqlite3

import emojis

DB_NAME = "oi.db"


class OIDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(DB_NAME)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS schema_version (version INT NOT NULL)"
        )
        db_version = self.cursor.execute(
            "SELECT version FROM schema_version"
        ).fetchall()
        if len(db_version) == 0:
            db_version = 0
        else:
            db_version = db_version[0][0]
        if db_version < 1:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS oi (id TEXT NOT NULL, messagecount INT NOT NULL)"
            )
        if db_version < 2:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS cumcry (id TEXT NOT NULL, emoji TEXT NOT NULL, cumcount INT NOT NULL, crycount INT NOT NULL)"
            )
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS confessions (confession TEXT NOT NULL)"
            )
        if db_version < 3:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS wyr (question TEXT NOT NULL)"
            )
        if db_version < 4:
            self.cursor.execute("ALTER TABLE confessions ADD COLUMN hash TEXT")
            self.cursor.execute("ALTER TABLE wyr ADD COLUMN hash TEXT")
        if db_version < 5:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS later_deletion (member_id TEXT NOT NULL, remove_time TEXT NOT NULL)"
            )
        if db_version < 6:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS cumtime (id TEXT NOT NULL, datetime TEXT NOT NULL)"
            )
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS crytime (id TEXT NOT NULL, datetime TEXT NOT NULL)"
            )
        LATEST_VERSION = 6
        if db_version == 0:
            self.cursor.execute(
                "INSERT INTO schema_version VALUES (?)", (LATEST_VERSION,)
            )
        else:
            self.cursor.execute(
                "UPDATE schema_version SET version = ?", (LATEST_VERSION,)
            )
        self.connection.commit()

    def update_message_count(self, id):
        self.cursor.execute("SELECT * FROM oi WHERE id = ?", (id,))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute("INSERT INTO oi VALUES (?, 1)", (id,))
        else:
            self.cursor.execute(
                "UPDATE oi SET messagecount = messagecount + 1 WHERE id = ?", (id,)
            )
        self.connection.commit()

    def get_hi_leaderboard(self):
        self.cursor.execute("SELECT * FROM oi ORDER BY messagecount DESC")
        return self.cursor.fetchall()

    def get_cum_leaderboard(self):
        self.cursor.execute(
            "SELECT id, emoji, cumcount, crycount FROM cumcry ORDER BY cumcount DESC"
        )
        return self.cursor.fetchall()

    def get_cry_leaderboard(self):
        self.cursor.execute(
            "SELECT id, emoji, cumcount, crycount FROM cumcry ORDER BY crycount DESC"
        )
        return self.cursor.fetchall()

    def get_aggregated_cumcry_leaderboard(self):
        self.cursor.execute(
            "SELECT id, emoji, cumcount + crycount FROM cumcry ORDER BY cumcount + crycount DESC, cumcount DESC"
        )
        return self.cursor.fetchall()

    def increment_cumcry_count(self, id, action):
        self.cursor.execute("SELECT * FROM cumcry WHERE id = ?", (id,))
        if len(self.cursor.fetchall()) == 0:
            # choose random emoji from 'Animals & Nature' category
            cat = [*emojis.db.get_emojis_by_category("Animals & Nature")]
            e = random.choice(cat)
            # check if anyone else has same emoji
            self.cursor.execute("SELECT * FROM cumcry WHERE emoji = ?", (e.aliases[0],))
            # repeat until we find one that no one else has
            while len(self.cursor.fetchall()) > 0:
                e = random.choice(cat)
                self.cursor.execute(
                    "SELECT * FROM cumcry WHERE emoji = ?", (e.aliases[0],)
                )
            # create entry for user with their unique emoji
            self.cursor.execute(
                "INSERT INTO cumcry VALUES (?, ?, 0, 0)", (id, e.aliases[0])
            )
        # update counts
        if action == "cum":
            self.cursor.execute(
                "UPDATE cumcry SET cumcount = cumcount + 1 WHERE id = ?", (id,)
            )
        elif action == "cry":
            self.cursor.execute(
                "UPDATE cumcry SET crycount = crycount + 1 WHERE id = ?", (id,)
            )
        self.connection.commit()

    def clear_cumcry_counts(self):
        self.cursor.execute("DELETE FROM cumcry")
        self.connection.commit()

    def store_confession(self, confession):
        confession = confession[len("confess ") :]
        gen_hash = hashlib.sha1(confession.encode("utf-8")).hexdigest()
        h = (
            "Here is the hash for your confession: `"
            + gen_hash
            + '`. If you want to delete your confession, send the following message: "unconfess <hash>" and if deleted '
            "the oi_discord_bot will react with the trash can emoji."
        )
        self.cursor.execute(
            "INSERT INTO confessions VALUES (?, ?)", (confession, gen_hash)
        )
        self.connection.commit()
        return h

    def store_wyr(self, wyr):
        wyr = wyr[len("wyr ") :]
        h = hashlib.sha1(wyr.encode("utf-8")).hexdigest()
        self.cursor.execute("INSERT INTO wyr VALUES (?, ?)", (wyr, h))
        self.connection.commit()
        return h

    def get_random_confession(self):
        self.cursor.execute(
            "SELECT rowid, * FROM confessions ORDER BY RANDOM() LIMIT 1"
        )
        table = self.cursor.fetchall()
        rowid = -1
        confession = ""
        if len(table) > 0:
            rowid = table[0][0]
            confession = table[0][1]
        return rowid, confession

    def get_random_wyr(self):
        self.cursor.execute("SELECT rowid, * FROM wyr ORDER BY RANDOM() LIMIT 1")
        table = self.cursor.fetchall()
        rowid = -1
        wyr = ""
        if len(table) > 0:
            rowid = table[0][0]
            wyr = table[0][1]
        return rowid, wyr

    def delete_confession(self, rowid):
        self.cursor.execute("DELETE FROM confessions WHERE rowid = ?", (rowid,))
        self.connection.commit()

    def delete_confession_by_hash(self, h):
        self.cursor.execute("DELETE FROM confessions WHERE hash = ?", (h,))
        num_rows = self.cursor.rowcount
        self.connection.commit()
        return num_rows

    def delete_wyr(self, rowid):
        self.cursor.execute("DELETE FROM wyr WHERE rowid = ?", (rowid,))
        self.connection.commit()

    def delete_wyr_by_hash(self, h):
        self.cursor.execute("DELETE FROM wyr WHERE hash = ?", (h,))
        self.connection.commit()

    def create_later_delete_job(self, member_id, remove_time):
        self.cursor.execute(
            "INSERT INTO later_deletion VALUES (?, ?)",
            (
                member_id,
                remove_time,
            ),
        )
        self.connection.commit()

    def delete_later_delete_job(self, member_id, remove_time):
        self.cursor.execute(
            "DELETE FROM later_deletion WHERE member_id = ? AND remove_time = ?",
            (
                member_id,
                remove_time,
            ),
        )
        self.connection.commit()

    def get_all_later_deletion_jobs(self):
        self.cursor.execute("SELECT member_id, remove_time FROM later_deletion")
        entries = self.cursor.fetchall()
        return entries

    def get_all_cumcry_entries(self):
        self.cursor.execute("SELECT * FROM cumcry")
        entries = self.cursor.fetchall()
        return entries

    def update_cumcry_entry(self, id, num_cum, num_cry):
        self.cursor.execute(
            "UPDATE cumcry SET cumcount = ?, crycount = ? WHERE id = ?",
            (num_cum, num_cry, id),
        )
        self.connection.commit()

    def insert_cum_date_entry(self, member_id, date):
        self.cursor.execute("INSERT INTO cumtime VALUES (?, ?)", (member_id, date))
        self.connection.commit()

    def insert_cry_date_entry(self, member_id, date):
        self.cursor.execute("INSERT INTO crytime VALUES (?, ?)", (member_id, date))
        self.connection.commit()

    def count_cum_date_entries_by_id(self, member_id):
        self.cursor.execute(
            "SELECT COUNT(*) FROM cumtime WHERE id = ?", (member_id,)
        )
        return self.cursor.fetchone()[0]

    def count_cry_date_entries_by_id(self, member_id):
        self.cursor.execute(
            "SELECT COUNT(*) FROM crytime WHERE id = ?", (member_id,)
        )
        return self.cursor.fetchone()[0]
