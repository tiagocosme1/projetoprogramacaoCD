"""
serial.py — Processamento SERIAL das imagens do PKLot
Classifica cada vaga como LIVRE ou OCUPADA usando OpenCV
Algoritmo CPU-bound com múltiplas passagens de processamento
"""

import os
import time
import csv
import cv2
import numpy as np

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO
# ─────────────────────────────────────────────
DATASET_DIR = r"C:\Users\João Victor\Downloads\UFPR05\data"
RESULTS_CSV = "resultados_serial.csv"

# Número de passagens de processamento por imagem (aumenta carga CPU)
N_PASSAGENS = 1

# ──────────────────────────────────────────────────────────────────────────────
def classificar_vaga(caminho_imagem: str) -> dict:
    """
    Classifica uma vaga como livre ou ocupada.
    Executa N_PASSAGENS de processamento para aumentar a carga de CPU,
    usando o resultado da última passagem para a classificação final.
    """
    img = cv2.imdecode(np.fromfile(caminho_imagem, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return {"caminho": caminho_imagem, "status": "erro", "score": -1}

    edge_density = 0
    std_dev = 0

    for _ in range(N_PASSAGENS):
        # Pré-processamento
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detecção de bordas com Canny
        edges = cv2.Canny(blur, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Equalização de histograma
        equalized = cv2.equalizeHist(gray)

        # Filtro Laplaciano
        laplacian = cv2.Laplacian(equalized, cv2.CV_64F)
        _ = laplacian.var()

        # Transformada de Hough
        cv2.HoughLinesP(edges, 1, np.pi / 180,
                        threshold=30, minLineLength=20, maxLineGap=5)

        # Desvio padrão de textura
        std_dev = np.std(gray) / 255.0

    # Score baseado nos mesmos critérios originais (threshold calibrado)
    score = 0.6 * edge_density * 10 + 0.4 * std_dev * 3
    score = min(score, 1.0)

    status = "ocupada" if score > 0.35 else "livre"
    return {"caminho": caminho_imagem, "status": status, "score": round(score, 4)}


def coletar_imagens(base_dir: str) -> list:
    imagens = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                imagens.append(os.path.join(root, f))
    return sorted(imagens)


def processar_serial(imagens: list) -> tuple:
    inicio = time.perf_counter()
    resultados = [classificar_vaga(img) for img in imagens]
    fim = time.perf_counter()
    return resultados, fim - inicio


def salvar_csv(resultados: list, tempo: float, arquivo: str):
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["caminho", "status", "score"])
        writer.writeheader()
        writer.writerows(resultados)
    livres   = sum(1 for r in resultados if r["status"] == "livre")
    ocupadas = sum(1 for r in resultados if r["status"] == "ocupada")
    erros    = sum(1 for r in resultados if r["status"] == "erro")
    print(f"\n{'='*55}")
    print(f"  RESULTADO SERIAL")
    print(f"{'='*55}")
    print(f"  Total de imagens : {len(resultados)}")
    print(f"  Livres           : {livres}")
    print(f"  Ocupadas         : {ocupadas}")
    print(f"  Erros            : {erros}")
    print(f"  Tempo total      : {tempo:.4f} s")
    print(f"  Resultados em    : {arquivo}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    print("Coletando imagens...")
    imagens = coletar_imagens(DATASET_DIR)

    if not imagens:
        print(f"[ERRO] Nenhuma imagem encontrada em '{DATASET_DIR}'.")
        exit(1)

    print(f"{len(imagens)} imagens encontradas. Processando serialmente...")
    resultados, tempo = processar_serial(imagens)
    salvar_csv(resultados, tempo, RESULTS_CSV)

    with open("tempo_serial.txt", "w") as f:
        f.write(f"{tempo:.6f}\n{len(imagens)}")
