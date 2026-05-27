"""
serial.py — Processamento SERIAL das imagens do PKLot
Classifica cada vaga como LIVRE ou OCUPADA usando OpenCV
"""

import os
import time
import csv
import cv2
import numpy as np

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO — ajuste o caminho do dataset
# ─────────────────────────────────────────────
DATASET_DIR = r"C:\Users\João Victor\Downloads\UFPR05\data"  # pasta raiz com as imagens do PKLot (UFPR04 + UFPR05)
RESULTS_CSV = "resultados_serial.csv"

# ──────────────────────────────────────────────────────────────────────────────
def classificar_vaga(caminho_imagem: str) -> dict:
    """
    Recebe o caminho de uma imagem de vaga recortada e retorna:
      - caminho : str
      - status  : 'livre' | 'ocupada'
      - score   : float  (0 = certamente livre, 1 = certamente ocupada)
    """
    img = cv2.imdecode(np.fromfile(caminho_imagem, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return {"caminho": caminho_imagem, "status": "erro", "score": -1}

    # Converte para escala de cinza e aplica desfoque
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detecta bordas (vagas ocupadas têm muito mais bordas — o carro)
    edges = cv2.Canny(blur, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size   # fração de pixels com borda

    # Desvio padrão dos tons de cinza (carros → mais textura → maior desvio)
    std_dev = np.std(gray) / 255.0

    # Score combinado
    score = 0.6 * edge_density * 10 + 0.4 * std_dev * 3
    score = min(score, 1.0)

    status = "ocupada" if score > 0.35 else "livre"
    return {"caminho": caminho_imagem, "status": status, "score": round(score, 4)}


def coletar_imagens(base_dir: str) -> list[str]:
    """Percorre recursivamente a pasta e retorna todos os .jpg / .jpeg / .png"""
    imagens = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                imagens.append(os.path.join(root, f))
    return sorted(imagens)


def processar_serial(imagens: list[str]) -> tuple[list[dict], float]:
    inicio = time.perf_counter()
    resultados = [classificar_vaga(img) for img in imagens]
    fim = time.perf_counter()
    return resultados, fim - inicio


def salvar_csv(resultados: list[dict], tempo: float, arquivo: str):
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


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Coletando imagens...")
    imagens = coletar_imagens(DATASET_DIR)

    if not imagens:
        print(f"[ERRO] Nenhuma imagem encontrada em '{DATASET_DIR}'.")
        print("Ajuste a variável DATASET_DIR no topo do arquivo.")
        exit(1)

    print(f"{len(imagens)} imagens encontradas. Processando serialmente...")
    resultados, tempo = processar_serial(imagens)
    salvar_csv(resultados, tempo, RESULTS_CSV)

    # Salva o tempo para o script de métricas usar depois
    with open("tempo_serial.txt", "w") as f:
        f.write(f"{tempo:.6f}\n{len(imagens)}")
