import json
import sqlite3
import sqlite_vec
from pathlib import Path

DB_PATH = Path("/data/vectors.db")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def init_vector_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS chunks (
            id        INTEGER PRIMARY KEY,
            session_id INTEGER NOT NULL,
            doc_type  TEXT NOT NULL,
            chunk_idx INTEGER NOT NULL,
            text      TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunk_embeddings USING vec0(
            chunk_id  INTEGER PRIMARY KEY,
            embedding FLOAT[1536]
        );
    """)
    conn.commit()
    conn.close()


def save_chunks(session_id: int, doc_type: str, chunks: list[str], embeddings: list[list[float]]):
    conn = _get_conn()
    for idx, (text, embedding) in enumerate(zip(chunks, embeddings)):
        cursor = conn.execute(
            "INSERT INTO chunks (session_id, doc_type, chunk_idx, text) VALUES (?, ?, ?, ?)",
            (session_id, doc_type, idx, text),
        )
        chunk_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO chunk_embeddings (chunk_id, embedding) VALUES (?, ?)",
            (chunk_id, json.dumps(embedding)),
        )
    conn.commit()
    conn.close()


def search(session_id: int, doc_type: str, query_embedding: list[float], top_k: int = 3) -> list[str]:
    conn = _get_conn()
    rows = conn.execute(
        """
        SELECT c.text
        FROM chunk_embeddings ce
        JOIN chunks c ON c.id = ce.chunk_id
        WHERE c.session_id = ? AND c.doc_type = ?
        ORDER BY vec_distance_cosine(ce.embedding, ?)
        LIMIT ?
        """,
        (session_id, doc_type, json.dumps(query_embedding), top_k),
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]
