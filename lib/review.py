from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be 2000 or later")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Summary cannot be empty")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        if value <= 0:
            raise ValueError("Employee ID must be a positive integer")
        if not Employee.find_by_id(value):
            raise ValueError("Employee with this ID does not exist")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id:
            sql = """
                UPDATE reviews 
                SET year = ?, summary = ?, employee_id = ? 
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        else:
            sql = """
                INSERT INTO reviews (year, summary, employee_id) 
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid

        Review.all[self.id] = self
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """
        Return a Review instance having the attribute values from the table row.
        Check the dictionary for an existing instance using the row's primary key.
        """
        id, year, summary, employee_id = row
        review = cls.all.get(id)
        if review is None:
            review = cls(year=year, summary=summary, employee_id=employee_id, id=id)
            cls.all[id] = review
        else:
            # Update the existing instance with the new values
            review.year = year
            review.summary = summary
            review.employee_id = employee_id
        return review

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        self.save()

    def delete(self):
        if self.id:
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()

            del Review.all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()

        return [cls.instance_from_db(row) for row in rows]