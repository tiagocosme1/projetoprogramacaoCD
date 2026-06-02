"""
paralelo.py — Processamento PARALELO das imagens do PKLot
Usa multiprocessing.Pool (mais estável no Windows)
Testa com 2, 4, 8 e 12 processos
"""

import os
import time
import csv
import multiprocessing
import cv2
import numpy as np

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO
# ─────────────────────────────────────────────
DATASET_DIR = r"C:\Users\João Victor\Downloads\UFPR05\data"
RESULTADOS_DIR = "resultados_paralelos"
TEMPOS_CSV = "tempos_paralelos.csv"
CONFIGURACOES = [2, 4, 8, 12]

# ──────────────────────────────────────────────────────────────────────────────
#  CLASSIFICAÇÃO (mesma lógica do serial.py)
# ──────────────────────────────────────────────────────────────────────────────
def classificar_vaga(caminho_imagem: str) -> dict:
    img = cv2.imdecode(np.fromfile(caminho_imagem, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return {"caminho": caminho_imagem, "status": "erro", "score": -1}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    std_dev = np.std(gray) / 255.0
    score = 0.6 * edge_density * 10 + 0.4 * std_dev * 3
    score = min(score, 1.0)
    status = "ocupada" if score > 0.35 else "livre"
    return {"caminho": caminho_imagem, "status": status, "score": round(score, 4)}


# ──────────────────────────────────────────────────────────────────────────────
#  COLETA DE IMAGENS
# ──────────────────────────────────────────────────────────────────────────────
def coletar_imagens(base_dir: str) -> list:
    imagens = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                imagens.append(os.path.join(root, f))
    return sorted(imagens)


# ──────────────────────────────────────────────────────────────────────────────
#  PROCESSAMENTO PARALELO COM POOL
# ──────────────────────────────────────────────────────────────────────────────
def processar_paralelo(imagens: list, num_processos: int):
    inicio = time.perf_counter()
    with multiprocessing.Pool(processes=num_processos) as pool:
        resultados = pool.map(classificar_vaga, imagens)
    fim = time.perf_counter()
    return resultados, fim - inicio


# ──────────────────────────────────────────────────────────────────────────────
#  SALVAR RESULTADOS
# ──────────────────────────────────────────────────────────────────────────────
def salvar_resultados(resultados: list, num_processos: int):
    os.makedirs(RESULTADOS_DIR, exist_ok=True)
    arquivo = os.path.join(RESULTADOS_DIR, f"resultados_{num_processos}proc.csv")
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["caminho", "status", "score"])
        writer.writeheader()
        writer.writerows(resultados)
    return arquivo


# ──────────────────────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    multiprocessing.freeze_support()  # necessário no Windows

    print("Coletando imagens...")
    imagens = coletar_imagens(DATASET_DIR)

    if not imagens:
        print(f"[ERRO] Nenhuma imagem encontrada em '{DATASET_DIR}'.")
        exit(1)

    print(f"{len(imagens)} imagens encontradas.\n")

    # Lê tempo serial
    tempo_serial = None
    if os.path.exists("tempo_serial.txt"):
        with open("tempo_serial.txt") as f:
            tempo_serial = float(f.readline().strip())
        print(f"Tempo serial carregado: {tempo_serial:.4f} s\n")
    else:
        print("[AVISO] tempo_serial.txt não encontrado. Speedup não será calculado.\n")

    tempos = []

    for num_proc in CONFIGURACOES:
        print(f"{'='*55}")
        print(f"  Testando com {num_proc} processos...")
        print(f"{'='*55}")

        resultados, tempo = processar_paralelo(imagens, num_proc)
        arquivo = salvar_resultados(resultados, num_proc)

        livres   = sum(1 for r in resultados if r["status"] == "livre")
        ocupadas = sum(1 for r in resultados if r["status"] == "ocupada")
        erros    = sum(1 for r in resultados if r["status"] == "erro")

        speedup    = round(tempo_serial / tempo, 4) if tempo_serial else "-"
        eficiencia = round((tempo_serial / tempo) / num_proc, 4) if tempo_serial else "-"

        print(f"  Total de imagens : {len(resultados)}")
        print(f"  Livres           : {livres}")
        print(f"  Ocupadas         : {ocupadas}")
        print(f"  Erros            : {erros}")
        print(f"  Tempo total      : {tempo:.4f} s")
        print(f"  Speedup          : {speedup}")
        print(f"  Eficiência       : {eficiencia}")
        print(f"  Resultados em    : {arquivo}\n")

        tempos.append({
            "processos": num_proc,
            "tempo": round(tempo, 4),
            "speedup": speedup,
            "eficiencia": eficiencia
        })

    # Salva tabela de tempos
    with open(TEMPOS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["processos", "tempo", "speedup", "eficiencia"])
        writer.writeheader()
        if tempo_serial:
            writer.writerow({
                "processos": 1,
                "tempo": round(tempo_serial, 4),
                "speedup": "1.0000",
                "eficiencia": "1.0000"
            })
        writer.writerows(tempos)

    print(f"{'='*55}")
    print(f"  Tabela de tempos salva em: {TEMPOS_CSV}")
    print(f"{'='*55}\n")