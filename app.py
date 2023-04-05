from flask import Flask, jsonify, request
from conn import connection
from settings import logger
import psycopg2

app = Flask(__name__)

# Online game - Design a class to manage an online game,
# including character creation, game mechanics, and player interactions.

# Query
# CREATE TABLE game(sno SERIAL PRIMARY KEY, character VARCHAR(200) NOT NULL ,
# mechanics VARCHAR(300), interactions VARCHAR(500));

# Game
#  sno | character |     mechanics     |    interactions     |     clan
# -----+-----------+-------------------+---------------------+---------------
#    1 | Naruto    | walk, jump, crawl | synergy, chat       | Leaf Village
#    2 | Hinata    | battle, run       | Call,               | Sand Village
#    3 | Akamaru   | smell, bark       | sign language,      | Water Village
#    4 | Anya      | think, attack     | hypnosis, magnetize | Forger


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as error:
            conn = kwargs.get('conn')
            if conn:
                conn.rollback()
            logger(__name__).error(f"Error occurred: {error}")
            return jsonify({"message": f"Error occurred: {error}"})
        except Exception as error:
            logger(__name__).error(f"Error occurred: {error}")
            return jsonify({"message": f"Error occurred: {error}"})
        finally:
            conn = kwargs.get("conn")
            cur = kwargs.get("cur")
            # close the database connection
            if conn:
                conn.close()
            if cur:
                cur.close()
            logger(__name__).warning("Hence account created, closing the connection")
    return wrapper


@app.route("/characters", methods=["GET", "POST"])
@handle_exceptions
def create_character():
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add new Character")

    char = request.json["char"]
    mech = request.json["mech"]
    interact = request.json["interact"]

    query = """INSERT INTO game(character, mechanics,
                        interactions) VALUES (%s, %s, %s)"""
    values = (char, mech, interact)
    cur.execute(query, values)

    conn.commit()

    logger(__name__).info(f"{char} added in the list")
    return jsonify({"message": f"{char} added in the list"}), 200

@app.route("/", methods=["GET"], endpoint='show_all_characters')  # READ the cart list
@handle_exceptions
def show_all_characters():
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display all characters in the list")

    show_query = "SELECT * FROM game;"
    cur.execute(show_query)
    data = cur.fetchall()
    # Log the details into logger file
    logger(__name__).info("Displayed list of all Characters in the list")
    return jsonify({"message": data}), 200


@app.route("/details/<string:character>", methods=["GET"], endpoint='show_character_details')  # READ the cart list
@handle_exceptions
def show_character_details(character):
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display character's details ")

    show_query = "SELECT * FROM game WHERE character = %s;"
    cur.execute(show_query, (character,))
    data = cur.fetchone()
    # Log the details into logger file
    logger(__name__).info("Displayed Character's details")
    return jsonify({"message": data}), 200


@app.route("/characters/clan/<int:sno>", methods=["PUT"], endpoint='adding_clan')
@handle_exceptions
def adding_clan(sno):
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to add clan")

    cur.execute("SELECT character from game where sno = %s", (sno,))
    get_character = cur.fetchone()

    if not get_character:
        return jsonify({"message": "Character not found"}), 200

    data = request.get_json()
    clan = data.get('clan')

    cur.execute("UPDATE game SET clan = %s WHERE sno = %s", (clan, sno))
    conn.commit()

    # Log the details into logger file
    logger(__name__).info(f"Character's clan details added: {data}")
    return jsonify({"message": "Character's clan details added", "Details": data}), 200

@app.route("/clan/<string:clan>", methods=["GET"], endpoint='show_same_clan_character')  # READ the cart list
@handle_exceptions
def show_same_clan_character(clan):
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to display characters if they belong to this clan ")

    show_query = "SELECT * FROM game WHERE clan = %s;"

    cur.execute(show_query, (clan,))
    data = cur.fetchall()

    # Log the details into logger file
    logger(__name__).info(f"Displayed Characters belonging to {clan} clan")
    return jsonify({"message": data})


@app.route("/characters/<int:sno>", methods=["PUT"], endpoint='update_character')
@handle_exceptions
def update_character(sno):
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to update details")


    cur.execute("SELECT character from game where sno = %s", (sno,))
    get_character = cur.fetchone()

    if not get_character:
        return jsonify({"message": "Character not found"}), 200
    data = request.get_json()
    char = data.get('char')
    mech = data.get('mech')
    interact = data.get('interact')

    if char:
        cur.execute("UPDATE game SET game.character = %s WHERE sno = %s", (char, sno))
    elif mech:
        cur.execute("UPDATE game SET mechanics = %s WHERE sno = %s", (mech, sno))
    elif interact:
        cur.execute("UPDATE game SET interactions = %s WHERE sno = %s", (interact, sno))

    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"Character details updated: {data}")
    return jsonify({"message": "Character details updated", "Details": data}), 200



@app.route("/delete/<int:sno>", methods=["DELETE"], endpoint='delete_student')      # DELETE an item from cart
@handle_exceptions
def delete_student(sno):
    # start the database connection
    cur, conn = connection()
    logger(__name__).warning("Starting the db connection to delete character from the list")

    delete_query = "DELETE from game WHERE sno = %s"
    cur.execute(delete_query, (sno,))
    conn.commit()
    # Log the details into logger file
    logger(__name__).info(f"Character with no. {sno} deleted from the table")
    return jsonify({"message": "Deleted Successfully", "char no": sno}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
