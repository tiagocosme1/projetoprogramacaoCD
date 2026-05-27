# 🅿️ Projeto Programação CD — Dataset PKLot

## 📋 Sobre o Dataset

Este projeto utiliza o **PKLot Dataset**, um conjunto de dados robusto para classificação de vagas em estacionamentos, composto por imagens capturadas em diferentes condições climáticas (ensolarado, nublado e chuvoso).

Os subconjuntos utilizados neste projeto são o **UFPR04** e **UFPR05**, capturados do **4º e 5º andar** do prédio da Universidade Federal do Paraná (UFPR), em Curitiba, Brasil. Ambos registram o mesmo estacionamento, porém de ângulos de câmera diferentes.

## 📊 Informações do Dataset

| Informação | Detalhe |
|---|---|
| 📷 Total de imagens utilizadas (UFPR04 + UFPR05) | A atualizar |
| 🌤️ Condições climáticas | Ensolarado, Nublado, Chuvoso |
| 🅿️ Vagas monitoradas | 45 vagas |
| 📐 Resolução | 1280 × 720 pixels |
| 📁 Formato | JPEG |

## 📁 Arquivos do Projeto

| Arquivo | Descrição |
|---|---|
| `serial.py` | Processa todas as imagens sequencialmente, uma por uma |
| `paralelo.py` | Processa as imagens em paralelo usando 2, 4, 8 e 12 processos |

## 🔍 Como os Scripts Funcionam

### Captura das Imagens

Ambos os scripts percorrem automaticamente todas as subpastas do dataset usando `os.walk()`, coletando o caminho de cada imagem `.jpg` encontrada:

```python
def coletar_imagens(base_dir):
    imagens = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                imagens.append(os.path.join(root, f))
    return sorted(imagens)
```

Isso significa que, independentemente de como as subpastas estão organizadas (por data, condição climática etc.), todas as imagens são encontradas automaticamente.

### serial.py — Processamento Sequencial

Processa as imagens uma por uma, em sequência. Para cada imagem:

1. Lê o arquivo com `cv2.imread()`
2. Converte para escala de cinza
3. Aplica filtro Gaussiano para suavização
4. Detecta bordas com o algoritmo de Canny
5. Calcula a densidade de bordas — vagas ocupadas têm mais bordas (contorno do veículo)
6. Calcula o desvio padrão de intensidade — veículos têm mais textura que o asfalto vazio
7. Combina os dois valores em um score → classifica como livre ou ocupada

Ao final, salva o tempo total em `tempo_serial.txt` e os resultados em `resultados_serial.csv`.

### paralelo.py — Processamento Paralelo

Usa a mesma lógica de classificação do `serial.py`, mas distribui as imagens entre múltiplos processos usando `multiprocessing.Pool`. O script testa automaticamente 4 configurações:

| Processos | Imagens por processo |
|---|---|
| 2 | ~1.708 |
| 4 | ~854 |
| 8 | ~427 |
| 12 | ~285 |

Cada processo trabalha de forma independente, sem precisar se comunicar com os outros durante o processamento. No final, os resultados são reunidos pelo processo principal.

Os tempos de cada configuração são salvos em `tempos_paralelos.csv`.

> ⚠️ **Windows:** O bloco `if __name__ == "__main__":` é obrigatório pois o Windows usa o método `spawn` para criar processos, diferente do Linux que usa `fork`.

## ⚙️ Como Executar

### 1. Instalar dependências

```bash
pip install opencv-python numpy matplotlib
```

### 2. Configurar o caminho das imagens

Abra `serial.py` e `paralelo.py` e ajuste a variável no topo do arquivo:

```python
DATASET_DIR = r"C:\caminho\para\sua\pasta\data"
```

### 3. Executar

```bash
python serial.py
python paralelo.py
```

## ⬇️ Como baixar as imagens

As imagens não estão incluídas neste repositório devido ao tamanho elevado dos arquivos.

Faça o download pelos links abaixo:

**UFPR05 (5º andar):**
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_9
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_10
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_11
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_12

**UFPR04 (4º andar):**
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_5
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_6
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_7
- 🔗 https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_8

## 📚 Referência

Almeida, P., Oliveira, L. S., Silva Jr, E., Britto Jr, A., Koerich, A., *PKLot – A robust dataset for parking lot classification*, Expert Systems with Applications, 42(11):4937-4949, 2015.
