"""
paralelo.py — Processamento PARALELO das imagens do PKLot
Usa multiprocessing.Pool para distribuir as imagens entre processos
Testa com 2, 4, 8 e 12 processos e salva os tempos em tempos_paralelos.csv
"""

import os
import time
import csv
import cv2
import numpy as np
import multiprocessing
from multiprocessing import Pool

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO — mesmo caminho do serial.py
# ─────────────────────────────────────────────
DATASET_DIR = r"C:\PKLot\data"
RESULTADOS_DIR   = "resultados_paralelos"
TEMPOS_CSV       = "tempos_paralelos.csv"
CONFIGURACOES    = [2, 4, 8, 12]   # número de processos a testar


# ──────────────────────────────────────────────────────────────────────────────
#  Função de classificação — DEVE estar no módulo principal para o Windows
#  (multiprocessing no Windows usa spawn, não fork)
# ──────────────────────────────────────────────────────────────────────────────
def classificar_vaga(caminho_imagem: str) -> dict:
    img = cv2.imread(caminho_imagem)
    if img is None:
        return {"caminho": caminho_imagem, "status": "erro", "score": -1}

    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    edge_density = np.sum(edges > 0) / edges.size
    std_dev      = np.std(gray) / 255.0
    score        = min(0.6 * edge_density * 10 + 0.4 * std_dev * 3, 1.0)
    status       = "ocupada" if score > 0.35 else "livre"

    return {"caminho": caminho_imagem, "status": status, "score": round(score, 4)}


def coletar_imagens(base_dir: str) -> list[str]:
    imagens = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                imagens.append(os.path.join(root, f))
    return sorted(imagens)


def processar_paralelo(imagens: list[str], n_processos: int) -> tuple[list[dict], float]:
    """Distribui as imagens entre n_processos usando Pool.map"""
    inicio = time.perf_counter()
    with Pool(processes=n_processos) as pool:
        resultados = pool.map(classificar_vaga, imagens)
    fim = time.perf_counter()
    return resultados, fim - inicio


def salvar_resultados(resultados: list[dict], n_proc: int):
    os.makedirs(RESULTADOS_DIR, exist_ok=True)
    arquivo = os.path.join(RESULTADOS_DIR, f"resultados_{n_proc}proc.csv")
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["caminho", "status", "score"])
        writer.writeheader()
        writer.writerows(resultados)


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # OBRIGATÓRIO no Windows — protege a criação dos processos filhos
    multiprocessing.freeze_support()

    print("Coletando imagens...")
    imagens = coletar_imagens(DATASET_DIR)

    if not imagens:
        print(f"[ERRO] Nenhuma imagem encontrada em '{DATASET_DIR}'.")
        print("Ajuste a variável DATASET_DIR no topo do arquivo.")
        exit(1)

    print(f"{len(imagens)} imagens encontradas.\n")

    tempos = []

    for n_proc in CONFIGURACOES:
        print(f"  Testando com {n_proc:2d} processos... ", end="", flush=True)
        resultados, tempo = processar_paralelo(imagens, n_proc)
        salvar_resultados(resultados, n_proc)
        tempos.append({"processos": n_proc, "tempo": round(tempo, 6)})
        print(f"{tempo:.4f} s")

    # Salva tempos em CSV para o script de métricas
    with open(TEMPOS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["processos", "tempo"])
        writer.writeheader()
        writer.writerows(tempos)

    print(f"\nTempos salvos em: {TEMPOS_CSV}")
    print("Resultados por configuração salvos em:", RESULTADOS_DIR)
