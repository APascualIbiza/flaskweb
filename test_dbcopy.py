# import pytest
from mock import Mock
import db


def test_fetchAllHealthcheck():
    # Given
    rows = [
        {"check": "check1"},
        {"check": "check2"}
    ]
    cursor = Mock()
    cursor.fetchall.return_value = rows
    mysql = Mock()
    mysql.connection.cursor.return_value = cursor
    db.mysql = mysql

    # When
    result = db.fetchAllHealthcheck()

    # Expect
    assert result == rows

    cursor.execute.assert_called_with("SELECT * FROM healthcheck")

    cursor.close.assert_called()


def test_fetchActivity():
    # Given
    row = {"activity": "activity"}
    cursor = Mock()
    cursor.fetchone.return_value = row
    mysql = Mock()
    mysql.connection.cursor.return_value = cursor
    db.mysql = mysql

    # When
    result = db.fetchActivity(55)

    # Expect
    assert result == row

    cursor.execute.assert_called_with("SELECT * FROM app_activity WHERE activity_id = %s", [55])

    cursor.close.assert_called()


def test_insertWebappUser():
    # Given
    cursor = Mock()
    mysql = Mock()
    mysql.connection.cursor.return_value = cursor
    db.mysql = mysql

    # When
    db.insertWebappUser("fakename", "fakeemail", "fakeusername", "fakepassword")

    # Expect

    cursor.execute.assert_called_with("INSERT INTO webapp_users(name, email, username, password) VALUES(%s, %s, %s, %s)", ("fakename", "fakeemail", "fakeusername", "fakepassword"))

    mysql.connection.commit.assert_called()

    cursor.close.assert_called()
