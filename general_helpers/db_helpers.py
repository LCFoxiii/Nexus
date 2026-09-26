def DBGrab(id, table, columns, id_name, cursor):    
    cursor.execute(
        f"SELECT {", ".join(columns)} FROM {table} WHERE {id_name} = ?",
        (id,)
    )
    
    result = cursor.fetchone()
    
    return result

def DBUpdate(id, table, updates, id_name, cursor, connection):
    set_clause = ", ".join([f"{column} = ?" for column in updates.keys()])
    values = list(updates.values()) + [id]
    
    cursor.execute(
        f"UPDATE {table} SET {set_clause} WHERE {id_name} = ?",
        values
    )
    connection.commit()

def DBIncrement(id, table, column, increment_value, id_name, cursor, connection):
    cursor.execute(
        f"UPDATE {table} SET {column} = {column} + ? WHERE {id_name} = ?",
        (increment_value, id)
    )
    connection.commit()