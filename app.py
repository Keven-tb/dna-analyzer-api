import os
import re
import sqlite3
from datetime import datetime, timezone

from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
DB_PATH = os.path.join(DATA_DIR, "sequencias.db")

BASES_VALIDAS = set("ATCG")
COMPLEMENTO = {"A": "T", "T": "A", "C": "G", "G": "C"}


def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sequencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                sequencia TEXT NOT NULL,
                tamanho INTEGER NOT NULL,
                gc_percentual REAL NOT NULL,
                complemento_reverso TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )
        conn.commit()


def calcular_gc_percentual(sequencia: str) -> float:
    total = len(sequencia)
    if total == 0:
        return 0.0
    gc = sum(1 for base in sequencia if base in "GC")
    return round((gc / total) * 100, 2)


def calcular_complemento_reverso(sequencia: str) -> str:
    complemento = "".join(COMPLEMENTO[base] for base in sequencia)
    return complemento[::-1]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/sequencias", methods=["POST"])
def criar_sequencia():
    payload = request.get_json(silent=True)

    if not payload or "nome" not in payload or "sequencia" not in payload:
        return jsonify({"erro": "Envie um JSON com os campos 'nome' e 'sequencia'."}), 400

    nome = str(payload["nome"]).strip()
    sequencia = str(payload["sequencia"]).strip().upper()

    if not nome or not sequencia:
        return jsonify({"erro": "'nome' e 'sequencia' não podem ser vazios."}), 400

    sequencia = re.sub(r"\s", "", sequencia)
    bases_invalidas = set(sequencia) - BASES_VALIDAS
    if bases_invalidas:
        return jsonify({
            "erro": f"Sequência contém bases inválidas: {sorted(bases_invalidas)}. "
                    f"Use apenas A, T, C, G."
        }), 400

    tamanho = len(sequencia)
    gc_percentual = calcular_gc_percentual(sequencia)
    complemento_reverso = calcular_complemento_reverso(sequencia)
    criado_em = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sequencias
                (nome, sequencia, tamanho, gc_percentual, complemento_reverso, criado_em)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, sequencia, tamanho, gc_percentual, complemento_reverso, criado_em),
        )
        conn.commit()
        nova_id = cursor.lastrowid

    return jsonify({
        "id": nova_id,
        "nome": nome,
        "sequencia": sequencia,
        "tamanho": tamanho,
        "gc_percentual": gc_percentual,
        "complemento_reverso": complemento_reverso,
        "criado_em": criado_em,
    }), 201


@app.route("/sequencias", methods=["GET"])
def listar_sequencias():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM sequencias ORDER BY id ASC"
        ).fetchall()

    sequencias = [dict(row) for row in rows]
    return jsonify(sequencias), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)