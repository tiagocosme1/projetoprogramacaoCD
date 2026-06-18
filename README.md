# Relatório de Análise de Desempenho 

**Disciplina:** PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA  
**Alunos:** João Victor Fernandes De Oliveira (RA: 083318) | Tiago Geraldo de Lima Cosme (RA: 083095)  
**Turma:** ADS e SI  
**Professor:** Rafael Marconi Ramos  
**Data:** 02/06/2026  

---

# 1. Descrição do Problema

O programa resolve o problema de classificação automática de vagas de estacionamento a partir de imagens capturadas por câmeras de vigilância. O sistema percorre recursivamente uma massa de imagens do dataset **PKLot (UFPR04 + UFPR05)** para classificar cada vaga como **livre** ou **ocupada** utilizando técnicas de visão computacional com OpenCV.

* **Algoritmo:** Para cada imagem, o sistema aplica as seguintes etapas de processamento: (1) conversão para escala de cinza, (2) filtro Gaussiano para suavização, (3) equalização de histograma para melhora de contraste, (4) detecção de bordas com algoritmo de Canny, (5) filtro Laplaciano para detecção de bordas de alta frequência, (6) Transformada de Hough para detecção de linhas, e (7) cálculo de score combinado de densidade de bordas e desvio padrão. O modelo paralelo utiliza **`multiprocessing.Pool`** para distribuir o processamento entre múltiplos processos, onde cada processo recebe um **bloco contíguo** da lista de imagens (estratégia de particionamento para reduzir contenção de I/O).
* **Tamanho da Entrada:** 7.323 imagens JPEG (UFPR04 + UFPR05), totalizando ~1,95 GB.
* **Objetivo:** O objetivo da paralelização é reduzir o tempo total de resposta (latency) ao distribuir a carga de processamento de imagens entre os múltiplos núcleos da CPU, superando o gargalo da execução sequencial.
* **Complexidade:** Aproximadamente $O(n \times p)$, onde $n$ é o número de imagens e $p$ é o custo de processamento por imagem (múltiplos filtros e transformadas).

---

# 2. Ambiente Experimental

Os testes foram realizados em dois ambientes diferentes para comparar o impacto do hardware nos resultados:

## Máquina Principal (resultados oficiais)

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | AMD Ryzen 7 5700X @ 3.4GHz (Turbo 4.6GHz) |
| Número de núcleos físicos   | 8 Núcleos (16 Threads) |
| Memória RAM                 | 32,00 GB DDR4 3200MHz |
| Sistema Operacional         | Microsoft Windows 11 Pro |
| Armazenamento               | SSD NVMe Kingston NV2 1TB (3500 MB/s leitura) |
| Placa-mãe                   | Gigabyte B550M Aorus Elite |
| Linguagem utilizada         | Python 3.x |
| Biblioteca de paralelização | Multiprocessing (stdlib) |
| Bibliotecas de visão        | OpenCV, NumPy |

## Máquina Secundária (testes comparativos)

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | 11th Gen Intel Core i5-11400H @ 2.70GHz |
| Número de núcleos físicos   | 6 Núcleos (12 Threads via Hyper-Threading) |
| Memória RAM                 | 8,00 GB |
| Sistema Operacional         | Microsoft Windows 11 Home Single Language |
| Armazenamento               | SSD NVMe WD PC SN530 (1 TB) |

---

# 3. Metodologia de Testes

Os experimentos foram conduzidos medindo o tempo total de execução ("Wall Time") utilizando a função `time.perf_counter()`.

* **Execuções:** Foi realizada uma medição para cada configuração de processos.
* **Entrada:** Massa de teste fixa (pastas UFPR04 + UFPR05) com 7.323 imagens JPEG.
* **Configurações:** Testes realizados com 1 (serial), 2, 4, 8 e 12 processos.
* **Particionamento:** cada processo recebe um bloco contíguo da lista de imagens (processo 1 lê as primeiras N, processo 2 as próximas N, etc.), evitando que múltiplos processos acessem regiões espalhadas do disco simultaneamente.
* **Condições:** Execução em máquina local com carga de sistema reduzida (navegador, Discord e demais aplicativos fechados).
* **Monitoramento adicional:** Além do tempo de execução, foi monitorado o uso de **CPU** e **Memória RAM** durante cada configuração, utilizando o Gerenciador de Tarefas do Windows (seção 10 detalha essa investigação).
* **Variação entre execuções:** Foi observado que repetir os mesmos testes em momentos diferentes gera tempos levemente diferentes (variações de 5 a 15%), devido a processos de fundo do sistema operacional e ajuste dinâmico de frequência da CPU.

---

# 4. Resultados Experimentais

| Nº Processos | Tempo de Execução (s) |
| ------------ | --------------------- |
| 1 (Serial)   | 255.6109              |
| 2            | 124.2306              |
| 4            | 78.5912               |
| 8            | 61.6876               |
| 12           | 60.6810               |

---

# 5. Resultados da Classificação

| Informação | Resultado |
| ---------- | --------- |
| Total de imagens processadas | 7.323 |
| Vagas livres identificadas | 1.307 |
| Vagas ocupadas identificadas | 6.016 |
| Erros | 0 |

---

# 6. Tabela de Resultados (Cálculos)

| Processos | Tempo (s) | Speedup | Eficiência |
| --------- | --------- | ------- | ---------- |
| 1         | 255.6109  | 1.0000  | 1.0000     |
| 2         | 124.2306  | 2.0576  | 1.0288     |
| 4         | 78.5912   | 3.2524  | 0.8131     |
| 8         | 61.6876   | 4.1436  | 0.5180     |
| 12        | 60.6810   | 4.2124  | 0.3510     |

---

# 7. Gráfico de Tempo de Execução
![Gráfico Tempo Execução](graficos/tempo_execucao.png)

# 8. Gráfico de Speedup
![Gráfico Speedup](graficos/speedup.png)

# 9. Gráfico de Eficiência
![Gráfico Eficiência](graficos/eficiencia.png)

---

# 10. Análise dos Resultados

## 10.1 O que é I/O Bound e o que é CPU Bound?

Antes de analisar os resultados, é importante esclarecer dois conceitos. Uma aplicação é **I/O Bound** quando seu maior gargalo é a entrada/saída de dados (leitura de disco, rede), e os processos ficam frequentemente com a CPU **ociosa esperando** esses dados chegarem. Já uma aplicação é **CPU Bound** quando o gargalo é a capacidade de processamento — a CPU está constantemente ocupada calculando, e o tempo de espera por disco é insignificante.

Inicialmente, suspeitou-se que o projeto fosse I/O Bound ou limitado pela memória RAM. Para confirmar a causa real, foi realizada uma investigação prática descrita a seguir.

## 10.2 Investigação prática: CPU, Memória e a hipótese da RAM

Durante a execução do `paralelo.py` na máquina secundária (i5-11400H, 6 núcleos), foi monitorado o uso de **CPU** e **Memória RAM** pelo Gerenciador de Tarefas do Windows:

| Processos | Uso de CPU | Uso de Memória RAM |
| --------- | ---------- | ------------------- |
| 2         | 40% – 66%  | 82% – 87% |
| 4         | 66%        | 87% |
| 8         | 92%        | 87% |
| 12        | 95% – 97%  | 87% – 90% |

O uso de memória RAM permaneceu **praticamente constante** em todas as configurações, enquanto o uso de **CPU escalou claramente** — chegando a 92-97% com 8-12 processos. Isso evidencia que o gargalo real é a **CPU**, não a memória.

Para confirmar, foi implementada uma versão otimizada com `imap_unordered()`, `chunksize` reduzido e `maxtasksperchild` para reduzir uso de RAM. Os resultados foram:

| Processos | Tempo (original) | Tempo (otimizado p/ RAM) | Diferença |
| --------- | ---------------- | ------------------------ | --------- |
| 2         | 158.64s          | 157.01s                  | -1.6s     |
| 4         | 105.86s          | 105.48s                  | -0.4s     |
| 8         | 94.95s           | 91.85s                   | -3.1s     |
| 12        | 91.89s           | 91.11s                   | -0.8s     |

A diferença mínima (< 3s) **comprova que a memória não era o gargalo** — o problema era o número insuficiente de núcleos físicos.

## 10.3 Impacto do Hardware — Comparação entre as duas máquinas

Para confirmar definitivamente que o gargalo era o número de núcleos físicos, os mesmos testes foram executados em dois hardwares diferentes:

| Processos | Notebook (6 núcleos) | PC Desktop (8 núcleos) | Ganho |
| --------- | -------------------- | ---------------------- | ----- |
| Serial    | 259.84s              | 255.61s                | similar |
| 2         | 154.91s / ef: 0.84   | 124.23s / ef: **1.03** | +22% |
| 4         | 105.38s / ef: 0.62   | 78.59s / ef: **0.81**  | +34% |
| 8         | 95.76s / ef: 0.34    | 61.69s / ef: **0.52**  | +36% |
| 12        | 89.69s / ef: 0.24    | 60.68s / ef: **0.35**  | +32% |

A melhora é consistente em todas as configurações — especialmente com 8 processos, onde o PC desktop (8 núcleos físicos) consegue rodar cada processo em seu próprio núcleo, **sem context switching**, enquanto o notebook (6 núcleos) já estava saturado. Isso prova que o código está correto — o limitador era o hardware.

## 10.4 O speedup obtido foi próximo do ideal?

Na máquina principal (8 núcleos), o speedup foi: **2.06x** (2 processos), **3.25x** (4 processos), **4.14x** (8 processos) e **4.21x** (12 processos). O speedup com 2 processos superou ligeiramente o ideal (2.06 > 2.0), o que pode ocorrer por variações do sistema ou cache aquecido. Com 8 processos, o speedup de **4.14x** (ideal seria 8.0) reflete o impacto do I/O residual e overhead de gerenciamento de processos.

## 10.5 Por que o ganho diminui progressivamente (2→4→8→12)?

O ganho de tempo encolhe a cada configuração: de **-131.4s** (2→4 processos) para **-16.9s** (4→8) e apenas **-1.0s** (8→12). Isso ocorre por dois fatores combinados:

**1. Limite de núcleos físicos:** com 8 núcleos físicos, os 8 primeiros processos rodam cada um no seu próprio núcleo. A partir do 9º processo, o sistema operacional precisa fazer **context switching** — alternando processos no mesmo núcleo, gerando overhead sem trabalho útil. Por isso 12 processos traz ganho mínimo sobre 8.

**2. I/O residual:** mesmo com particionamento em blocos contíguos, múltiplos processos ainda acessam o disco simultaneamente. O SSD NVMe mitiga muito esse problema (3500 MB/s de leitura), mas alguma contenção ainda existe com 8+ processos simultâneos.

## 10.6 Por que a eficiência cai conforme aumentam os processos?

A eficiência mede o quanto cada processo está sendo aproveitado em relação ao seu potencial teórico. Com **2 processos** a eficiência foi de **1.03** (acima do ideal — cache e turbo boost do processador ajudaram), caindo progressivamente para **0.81** (4 processos), **0.52** (8 processos) e **0.35** (12 processos). Com 12 processos, 65% do potencial teórico é perdido em overhead de context switching e I/O — consequência direta de rodar 4 processos além dos 8 núcleos físicos disponíveis.

## 10.7 Houve overhead de paralelização?

Sim. Os principais overheads identificados foram:

- **Context switching:** com mais processos que núcleos físicos (a partir de 9 processos), a CPU alterna entre processos gastando tempo sem trabalho útil
- **I/O residual:** múltiplos processos acessando o disco simultaneamente, mesmo com particionamento em blocos e SSD NVMe
- **Criação e inicialização de processos:** o `multiprocessing.Pool` precisa inicializar cada processo worker com o interpretador Python e bibliotecas (OpenCV, NumPy)
- **Serialização (pickle):** o pool serializa os dados para enviar entre processos

---

# 11. Conclusão

* **Desempenho:** O paralelismo foi eficaz, reduzindo o tempo de processamento de **~255s para ~60s** com 12 processos — uma redução de aproximadamente **76%**.

* **Causa raiz confirmada:** a limitação de núcleos físicos é o principal fator que determina a escalabilidade do programa. Isso foi comprovado pela comparação direta entre as duas máquinas: o mesmo código no PC desktop (8 núcleos) produziu eficiência consistentemente superior ao notebook (6 núcleos) em todas as configurações.

* **Melhor configuração:** Em termos de tempo bruto, **8 processos** foi o ponto ótimo (61.69s), com boa eficiência (0.52). Com 12 processos o ganho adicional foi mínimo (-1s), com custo de eficiência significativo.

* **Melhor custo-benefício:** a configuração com **2 processos** foi a mais eficiente (1.03), aproveitando quase 100% do potencial teórico de cada processo.

* **Melhorias possíveis:** utilizar um processador com mais núcleos físicos (ex: Ryzen 9, Intel i9) para testar configurações acima de 8 processos com maior eficiência. Como alternativa, processar as imagens em GPU com OpenCV-CUDA traria ganhos muito superiores, já que operações de visão computacional são altamente paralelizáveis em GPU (RTX 4060 Ti disponível na máquina principal poderia ser explorada).

---

# 12. Como obter as imagens do Dataset

As imagens não estão incluídas no repositório. Faça o download pelos links abaixo:

**UFPR05 (5º andar):**
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_9
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_10
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_11
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_12

**UFPR04 (4º andar):**
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_5
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_6
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_7
- https://huggingface.co/datasets/Voxel51/PKLot/tree/main/data/data_8

Após o download, ajuste a variável `DATASET_DIR` no topo dos arquivos `serial.py` e `paralelo.py` para o caminho da pasta onde as imagens foram salvas.

**Referência:** Almeida, P., Oliveira, L. S., Silva Jr, E., Britto Jr, A., Koerich, A., *PKLot – A robust dataset for parking lot classification*, Expert Systems with Applications, 42(11):4937-4949, 2015.
