import hashlib
import random
import sqlite3

import emojis

DB_NAME = "oi.db"


class OIDatabase:
    def __init__(self):
        """
        If you want to make a database change:
        - Increment LATEST_VERSION
        - Make your changes and wrap them around an if db_version < <previous version> function
        """
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
        if db_version < 7:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS unlater (id TEXT NOT NULL, cmdcount INT NOT NULL)"
            )
        if db_version < 8:
            self.cursor.execute("ALTER TABLE later_deletion ADD COLUMN jobid TEXT")
        if db_version < 9:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS later_min (id TEXT NOT NULL, minutes INT NOT NULL)"
            )
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS last_latered (id TEXT NOT NULL, datetime TEXT NOT NULL)"
            )
        LATEST_VERSION = 9
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
        """
        Increment #hi msg count by 1.
        :param id: user id
        :return: None
        """
        self.cursor.execute("SELECT * FROM oi WHERE id = ?", (id,))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute("INSERT INTO oi VALUES (?, 1)", (id,))
        else:
            self.cursor.execute(
                "UPDATE oi SET messagecount = messagecount + 1 WHERE id = ?", (id,)
            )
        self.connection.commit()

    def get_hi_leaderboard(self):
        """
        Get ID, message count for users in #hi.
        :return:
        """
        self.cursor.execute("SELECT * FROM oi ORDER BY messagecount DESC")
        return self.cursor.fetchall()

    def get_cum_leaderboard(self):
        """
        Gets all id, emoji, cumcount, crycount from cumcry table, order by cumcount.
        :return:
        """
        self.cursor.execute(
            "SELECT id, emoji, cumcount, crycount FROM cumcry ORDER BY cumcount DESC"
        )
        return self.cursor.fetchall()

    def get_cry_leaderboard(self):
        """
        Gets all id, emoji, cumcount, crycount from cumcry table, order by crycount.
        :return:
        """
        self.cursor.execute(
            "SELECT id, emoji, cumcount, crycount FROM cumcry ORDER BY crycount DESC"
        )
        return self.cursor.fetchall()

    def get_aggregated_cumcry_leaderboard(self):
        """
        Gets all id, emoji, cumcount + crycount from cumcry table, order by cumcount + crycount.
        :return:
        """
        self.cursor.execute(
            "SELECT id, emoji, cumcount + crycount FROM cumcry ORDER BY cumcount + crycount DESC, cumcount DESC"
        )
        return self.cursor.fetchall()

    def increment_cumcry_count(self, id, action):
        """
        Increment cum or cry count for user by 1. If user doesn't exist, creates entry for them with random emoji.
        :param id: user id
        :param action: either "cum" or "cry"
        :return:
        """
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
        """
        Clear all cum and cry counts. Irreversible operation, do not execute.
        :return:
        """
        self.cursor.execute("DELETE FROM cumcry")
        self.connection.commit()

    def store_confession(self, confession):
        """
        Stores confession and hashed confession in database. Returns string to be sent to user.
        :param confession: confession message in the format "confession <actual confession>"
        :return: message to send to user with hash
        """
        confession = confession[len("confess ") :]
        gen_hash = hashlib.sha1(confession.encode("utf-8")).hexdigest()
        h = (
            "Here is the hash for your confession: `"
            + gen_hash
            + '`. If you want to delete your confession, send the following message: "unconfess <hash>" and if deleted '
            "the oi bot will react with the trash can emoji."
        )
        self.cursor.execute(
            "INSERT INTO confessions VALUES (?, ?)", (confession, gen_hash)
        )
        self.connection.commit()
        return h

    def store_wyr(self, wyr):
        """
        Stores wyr and hashed wyr in database. Returns hash to be sent to user.
        :param wyr: wyr message in the format "wyr <actual wyr>"
        :return: message to send to user with hash
        """
        wyr = wyr[len("wyr ") :]
        gen_hash = hashlib.sha1(wyr.encode("utf-8")).hexdigest()
        h = (
            "Here is the hash for your wyr: `"
            + gen_hash
            + '`. If you want to delete your confession, send the following message: "unwyr <hash>" and if deleted '
            "the oi bot will react with the trash can emoji."
        )
        self.cursor.execute("INSERT INTO wyr VALUES (?, ?)", (wyr, gen_hash))
        self.connection.commit()
        return h

    def get_random_confession(self):
        """
        Gets random confession.
        :return: rowid, confession
        """
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

    def get_num_confessions(self):
        """
        :return: number of entries in confessions table
        """
        self.cursor.execute("SELECT COUNT(1) FROM confessions")
        num = self.cursor.fetchall()
        return num

    def get_random_wyr(self):
        """
        Gets random wyr.
        :return: rowid, wyr
        """
        self.cursor.execute("SELECT rowid, * FROM wyr ORDER BY RANDOM() LIMIT 1")
        table = self.cursor.fetchall()
        rowid = -1
        wyr = ""
        if len(table) > 0:
            rowid = table[0][0]
            wyr = table[0][1]
        return rowid, wyr

    def get_num_wyr(self):
        """
        :return: number of entries in confessions table
        """
        self.cursor.execute("SELECT COUNT(1) FROM wyr")
        num = self.cursor.fetchall()
        return num

    def delete_confession(self, rowid):
        """
        Deletes confession by rowid. Use if rowid is knownn.
        :param rowid:
        :return:
        """
        self.cursor.execute("DELETE FROM confessions WHERE rowid = ?", (rowid,))
        self.connection.commit()

    def delete_confession_by_hash(self, h):
        """
        Deletes confession by hash.
        :param h: hash
        :return: number of rows deleted
        """
        self.cursor.execute("DELETE FROM confessions WHERE hash = ?", (h,))
        num_rows = self.cursor.rowcount
        self.connection.commit()
        return num_rows

    def delete_wyr(self, rowid):
        """
        Deletes wyr by rowid. Use if rowid is known.
        :param rowid:
        :return:
        """
        self.cursor.execute("DELETE FROM wyr WHERE rowid = ?", (rowid,))
        self.connection.commit()

    def delete_wyr_by_hash(self, h):
        """
        Deletes wyr by hash.
        :param h: hash
        :return: number of rows deleted
        """
        self.cursor.execute("DELETE FROM wyr WHERE hash = ?", (h,))
        num_rows = self.cursor.rowcount
        self.connection.commit()
        return num_rows

    def create_later_delete_job(self, member_id, remove_time, jobid):
        """
        Creates job to remove later role
        :param member_id: ID of target member
        :param remove_time: string of datetime object representing remove tim
        :param jobid: ID of apscheduler job
        :return:
        """
        self.cursor.execute(
            "INSERT INTO later_deletion (member_id, remove_time, jobid) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM later_deletion WHERE member_id = ? AND remove_time = ?);",
            (
                member_id,
                remove_time,
                jobid,
                member_id,
                remove_time,
            ),
        )
        self.connection.commit()

    def delete_later_delete_job(self, member_id, remove_time):
        """
        Deletes job to remove later role from row. Used if job is completed without restart.
        :param member_id:
        :param remove_time:
        :return:
        """
        self.cursor.execute(
            "DELETE FROM later_deletion WHERE member_id = ? AND remove_time = ?",
            (
                member_id,
                remove_time,
            ),
        )
        self.connection.commit()

    def get_all_later_deletion_jobs(self):
        """
        Gets all later deletion job entries in the db.
        :return: entries in the form of a list of tuples (member_id, remove_time)
        """
        self.cursor.execute("SELECT * FROM later_deletion")
        entries = self.cursor.fetchall()
        return entries

    def get_later_deletion_jobs_by_id(self, member_id):
        """
        Gets all later deletion job entries in the db.
        :return: entries in the form of a list of tuples (member_id, remove_time)
        """
        self.cursor.execute(
            "SELECT * FROM later_deletion where member_id = ?", (member_id,)
        )
        entries = self.cursor.fetchall()
        return entries

    def delete_later_jobs_by_id(self, user_id):
        """
        Deletes all later deletion jobs by user id.
        :param user_id: target user id
        :return:
        """
        self.cursor.execute(
            "DELETE FROM later_deletion WHERE member_id = ?", (user_id,)
        )
        self.connection.commit()

    def get_all_cumcry_entries(self):
        """
        Gets all cumcry entries in the db.
        :return: cumcry entries in the form of a list of tuples (id, emoji, cumcount, crycount)
        """
        self.cursor.execute("SELECT * FROM cumcry")
        entries = self.cursor.fetchall()
        return entries

    def update_cumcry_entry(self, id, num_cum, num_cry):
        """
        Updates cumcry entry with new cum and cry counts.
        :param id:
        :param num_cum:
        :param num_cry:
        :return:
        """
        self.cursor.execute(
            "UPDATE cumcry SET cumcount = ?, crycount = ? WHERE id = ?",
            (num_cum, num_cry, id),
        )
        self.connection.commit()

    def insert_cum_date_entry(self, member_id, date):
        """
        Inserts a new cum date entry into the db.
        :param member_id: ID of member
        :param date: datetime object or string
        :return:
        """
        self.cursor.execute("INSERT INTO cumtime VALUES (?, ?)", (member_id, date))
        self.connection.commit()

    def insert_cry_date_entry(self, member_id, date):
        """
        Inserts a new cry date entry into the db.
        :param member_id: ID of member
        :param date: datetime object or string
        :return:
        """
        self.cursor.execute("INSERT INTO crytime VALUES (?, ?)", (member_id, date))
        self.connection.commit()

    def count_cum_date_entries_by_id(self, member_id):
        """
        Counts the number of cum date entries for a given member.
        :param member_id:
        :return:
        """
        self.cursor.execute("SELECT COUNT(*) FROM cumtime WHERE id = ?", (member_id,))
        return self.cursor.fetchone()[0]

    def count_cry_date_entries_by_id(self, member_id):
        """
        Counts the number of cry date entries for a given member.
        :param member_id:
        :return:
        """
        self.cursor.execute("SELECT COUNT(*) FROM crytime WHERE id = ?", (member_id,))
        return self.cursor.fetchone()[0]

    def get_cumcry_id_emoji_pairs(self):
        """
        Gets a dictionary mapping ids to emojis.
        :return: dictionary of id->emoji pairs. Emojis are given by names, eg. "potted_plant".
        """
        self.cursor.execute("SELECT id, emoji FROM cumcry")
        return dict(self.cursor.fetchall())

    def get_cum_date_entries_by_id(self, id):
        """
        Gets all cum date entries for a given member.
        :param id: discord member id
        :return:
        """
        self.cursor.execute("SELECT datetime FROM cumtime WHERE id = ?", (id,))
        return self.cursor.fetchall()

    def get_cry_date_entries_by_id(self, id):
        """
        Gets all cry date entries for a given member.
        :param id: discord member id
        :return:
        """
        self.cursor.execute("SELECT datetime FROM crytime WHERE id = ?", (id,))
        return self.cursor.fetchall()

    def update_unlater_count(self, id):
        """
        Increment /unlater count by 1.
        :param id: user id
        :return: None
        """
        self.cursor.execute("SELECT * FROM unlater WHERE id = ?", (id,))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute("INSERT INTO unlater VALUES (?, 1)", (id,))
        else:
            self.cursor.execute(
                "UPDATE unlater SET cmdcount = cmdcount + 1 WHERE id = ?", (id,)
            )
        self.connection.commit()

    def get_unlater_leaderboard(self):
        """
        Get ID, call count for /unlater.
        :return:
        """
        self.cursor.execute("SELECT * FROM unlater ORDER BY cmdcount DESC")
        return self.cursor.fetchall()

    def insert_later_time(self, id, curr_time):
        """
        Insert into unlater table.
        :param id: user id
        :return: None
        """
        self.cursor.execute(
            "INSERT INTO last_latered VALUES (?, ?)",
            (
                id,
                curr_time,
            ),
        )
        self.connection.commit()

    def get_last_later_time(self, id):
        """
        Get last time user used /later.
        :param id: user id
        :return: Datetime string of last latered time
        """
        self.cursor.execute("SELECT last_latered FROM last_latered WHERE id = ?", (id,))
        return self.cursor.fetchone()[0]

    def remove_later_time(self, id):
        """
        Remove last latered time from table.
        :param id: user id
        :return: None
        """
        self.cursor.execute("DELETE FROM last_latered WHERE id = ?", (id,))
        self.connection.commit()

    def update_later_min_count(self, id, minutes):
        """
        Increment /unlater count by 1.
        :param id: user id
        :return: None
        """
        self.cursor.execute("SELECT * FROM later_min WHERE id = ?", (id,))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                "INSERT INTO later_min VALUES (?, ?)",
                (
                    id,
                    minutes,
                ),
            )
        else:
            self.cursor.execute(
                "UPDATE later_min SET minutes = minutes + ? WHERE id = ?",
                (
                    minutes,
                    id,
                ),
            )
        self.connection.commit()

    def get_later_min_leaderboard(self):
        """
        Get ID, call count for /unlater.
        :return:
        """
        self.cursor.execute("SELECT * FROM later_min ORDER BY minutes DESC")
        return self.cursor.fetchall()
