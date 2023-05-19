import sqlite3


def add_book(cur, command):
    if len(command) != 4:
        print("Wrong amount of arguments, only (title, author, publish_year) is needed")
        return 0
    cur.executemany("INSERT INTO books (title, author, publish_year) VALUES (?, ?, ?);", command[1:])
    con.commit()
    return 1


def list_books(cur):
    for row in cur.execute("""SELECT * FROM books;"""):
        print(row)
    return 1


def add_reader(cur, command):
    if len(command) != 2:
        print("Wrong amount of arguments, only (name) is needed")
        return 0
    cur.executemany("INSERT INTO readers (name) VALUES (?);", command[1:])
    con.commit()
    return 1


def list_readers(cur):
    for row in cur.execute("""SELECT * FROM readers;"""):
        print(row)
    return 1


def give_book(cur, command):
    if len(command) != 3:
        print("Wrong amount of arguments, only (book_id, reader_id) is needed")
        return 0
    for row in cur.execute(f"""SELECT * FROM books WHERE book_id={command[1]} and returning_date is NULL;"""):
        print("This book is already taken, try another book")
        return 0
    cur.executemany(
        "INSERT INTO records (reader_id, book_id, taking_date, returning_date) VALUES (?, ?, date(\"now\"), ?);",
        [(command[1], command[2], None)])
    con.commit()


def take_book(cur, command):
    if len(command) != 3:
        print("Wrong amount of arguments, only (book_id, reader_id) is needed")
        return 0
    flag = 0
    for row in cur.execute(f"""SELECT * FROM books WHERE book_id={command[1]} and returning_date is NULL;"""):
        flag = 1
        break
    if not flag:
        print("This book was not taken, try another one")
        return 0
    cur.execute(
        f"UPDATE records SET returning_date = date(\"now\") where book_id={command[1]} and returning_date is NULL;")
    con.commit()
    return 1


def list_taken_books(cur):
    for row in cur.execute("""
                        SELECT
                            records.book_id, books.title
                        FROM records
                        INNER JOIN (
                            SELECT * FROM books
                            ) books
                        on records.book_id = books.id
                        WHERE records.returning_date is null
                        ORDER BY records.book_id;
                        """):
        print(row)
    return 1


def setup(cur):
    cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                author TEXT,
                title TEXT,
                publish_year INTEGER);
            """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS readers (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT);
            """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS records (
                reader_id INTEGER,
                book_id INTEGER,
                taking_date TIMESTAMP,
                returning_date TIMESTAMP,
                FOREIGN KEY (reader_id) REFERENCES readers (id),
                FOREIGN KEY (book_id) REFERENCES books (id));
            """)


def main():
    # connecting to database
    bd_path = input("Enter the database file if exists, otherwise RAM memory will be used:") or ":memory:"
    con = sqlite3.connect(bd_path)
    cur = con.cursor()
    setup(cur)

    # list the available commands
    help_info = """
List of commands:
    add_book title author publish_year - adds a book to database
    add_reader name                    - adds a reader to database
    list_books                         - lists all the books
    list_taken_books                   - lists all the books that are currently taken
    list_readers                       - lists all the readers
    give_book book_id reader_id   - gives book to a reader
    take_book book_id reader_id   - takes book from a reader
    quit                               - stops execution
    help                               - have a look at this text again
    """
    print(help_info)
    # line parser
    line = input(">")
    while True:
        command = line.split()
        if command[0] == "quit":
            break
        if command[0] == "help":
            print(help_info)
        elif command[0] == "add_book":
            add_book(cur, command)
        elif command[0] == "add_reader":
            add_reader(cur, command)
        elif command[0] == "list_books":
            list_books(cur)
        elif command[0] == "list_taken_books":
            list_taken_books(cur)
        elif command[0] == "list_readers":
            list_readers(cur)
        elif command[0] == "give_book":
            give_book(cur, command)
        elif command[0] == "take_book":
            take_book(cur, command)
        else:
            print("Unrecognized command, please try again")
        line = input(">")
    print("goodbye...")
    return 0


if __name__ == "__main__":
    main()
