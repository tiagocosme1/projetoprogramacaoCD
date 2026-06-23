# Relatório de Análise de Desempenho 

**Disciplina:** PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA  
**Alunos:** João Victor Fernandes De Oliveira (RA: 083318) | Tiago Geraldo de Lima Cosme (RA: 083095)  
**Turma:** ADS e SI  
**Professor:** Rafael Marconi Ramos  
**Data:** 02/06/2026  

---

# 1. Descrição do Problema

O programa resolve o problema de classificação automática de vagas de estacionamento a partir de imagens capturadas por câmeras de vigilância. O sistema percorre recursivamente uma massa de imagens do dataset **PKLot (UFPR04 + UFPR05)** para classificar cada vaga como **livre** ou **ocupada** utilizando técnicas de visão computacional com OpenCV.

* **Algoritmo:** Para cada imagem, o sistema aplica as seguintes etapas de processamento: (1) conversão para escala de cinza, (2) filtro Gaussiano para suavização, (3) equalização de histograma para melhora de contraste, (4) detecção de bordas com algoritmo de Canny, (5) filtro Laplaciano para detecção de bordas de alta frequência, (6) Transformada de Hough para detecção de linhas, e (7) cálculo de score combinado de densidade de bordas e desvio padrão. O modelo paralelo utiliza **`multiprocessing.Pool`** para distribuir o processamento entre múltiplos processos.
* **Tamanho da Entrada:** 7.323 imagens JPEG (UFPR04 + UFPR05), totalizando ~1,95 GB.
* **Objetivo:** Reduzir o tempo total de processamento distribuindo a carga entre múltiplos núcleos da CPU.
* **Complexidade:** Aproximadamente $O(n \times p)$, onde $n$ é o número de imagens e $p$ é o custo de processamento por imagem.

---

# 2. Ambiente Experimental

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | AMD Ryzen 7 5700X @ 3.4GHz (Turbo 4.6GHz) |
| Número de núcleos físicos   | 8 Núcleos (16 Threads) |
| Memória RAM                 | 32,00 GB DDR4 3200MHz |
| Sistema Operacional         | Microsoft Windows 11 Pro |
| Armazenamento               | SSD NVMe Kingston NV2 1TB (3500 MB/s leitura) |
| Placa-mãe                   | Gigabyte B550M Aorus Elite |
| Placa de Vídeo              | NVIDIA GeForce RTX 4060 Ti 8GB |
| Linguagem utilizada         | Python 3.x |
| Biblioteca de paralelização | Multiprocessing (stdlib) |
| Bibliotecas de visão        | OpenCV, NumPy |

---

# 3. Metodologia de Testes

Os experimentos foram conduzidos medindo o tempo total de execução ("Wall Time") utilizando a função `time.perf_counter()`.

* **Execuções:** Foi realizada uma medição para cada configuração de processos.
* **Entrada:** Massa de teste fixa (pastas UFPR04 + UFPR05) com 7.323 imagens JPEG.
* **Configurações:** Testes realizados com 1 (serial), 2, 4, 8 e 12 processos.
* **Condições:** Execução em máquina local com carga de sistema reduzida (navegador, Discord e demais aplicativos fechados).
* **Variação entre execuções:** Foi observado que repetir os mesmos testes em momentos diferentes gera tempos levemente diferentes, devido a processos de fundo do sistema operacional, estado do cache de disco e ajuste dinâmico de frequência da CPU (Turbo Boost). Os valores reportados representam uma execução típica do sistema.

---

# 4. Resultados Experimentais

| Nº Processos | Tempo de Execução (s) |
| ------------ | --------------------- |
| 1 (Serial)   | 246.6                 |
| 2            | 129.8                 |
| 4            | 70.1                  |
| 8            | 40.6                  |
| 12           | 47.0                  |

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
| 1         | 246.6     | 1.00    | 100,0%     |
| 2         | 129.8     | 1.90    | 95,0%      |
| 4         | 70.1      | 3.52    | 88,0%      |
| 8         | 40.6      | 6.08    | 76,0%      |
| 12        | 47.0      | 5.24    | 43,7%      |

---

# 7. Gráfico de Tempo de Execução
![Gráfico Tempo Execução](graficos/tempo_execucao(1).png)

# 8. Gráfico de Speedup
![Gráfico Speedup](graficos/speedup(1).png)

# 9. Gráfico de Eficiência
![Gráfico Eficiência](graficos/eficiencia(1).png)

---

# 10. Análise dos Resultados

## 10.1 O speedup obtido foi próximo do ideal?

O speedup cresceu de forma muito satisfatória até 8 processos: **1.90x** (2 processos), **3.52x** (4 processos) e **6.08x** (8 processos) — este último é o melhor resultado, próximo do ideal teórico de 8.0x. Porém, com **12 processos o speedup caiu para 5.24x**, indicando que o desempenho não apenas estagnou, mas **regrediu** ao ultrapassar os núcleos físicos disponíveis.

## 10.2 Por que 12 processos teve resultado PIOR que 8 processos?

Este é o ponto central da análise. O processador utilizado, **AMD Ryzen 7 5700X, possui exatamente 8 núcleos físicos**. Isso explica perfeitamente o comportamento observado:

**Com 8 processos:** cada processo é executado em um núcleo físico próprio, sem nenhuma disputa de recursos. O sistema operacional não precisa fazer nenhum tipo de troca de contexto — é a configuração ideal para este hardware, resultando no melhor tempo (40.6s) e melhor speedup (6.08x) de todo o experimento.

**Com 12 processos:** como existem apenas 8 núcleos físicos disponíveis, os 4 processos excedentes precisam **compartilhar núcleos já ocupados**. O sistema operacional passa a realizar **context switching** constante — pausando um processo, salvando seu estado, carregando outro processo no mesmo núcleo, e repetindo esse ciclo continuamente. Esse processo consome ciclos de CPU **sem realizar nenhum trabalho útil de classificação de imagens**.

O resultado prático foi uma **piora real de desempenho**: o tempo subiu de 40.6s para 47.0s (+15,8%), e a eficiência despencou de 76% para apenas 43,7% — uma queda de mais de 30 pontos percentuais. Isso comprova, de forma direta e quantitativa, que **adicionar processos além do número de núcleos físicos não apenas deixa de ajudar, como efetivamente prejudica o desempenho**.

## 10.3 Por que a eficiência cai progressivamente?

A eficiência mede o quanto cada processo está sendo aproveitado em relação ao seu potencial teórico (eficiência = speedup ÷ número de processos). A queda observada — 95% (2 processos) → 88% (4 processos) → 76% (8 processos) → 43,7% (12 processos) — segue um padrão claro:

* **Até 8 processos**, a queda é suave e esperada: cada processo adicional ainda tem acesso a um núcleo físico, mas o overhead de criação/gerenciamento de processos (inicialização do interpretador Python, carregamento do OpenCV e NumPy em cada worker) cresce proporcionalmente.
* **Acima de 8 processos**, a queda se torna abrupta: o context switching introduzido pelos 4 processos excedentes consome recursos que deveriam estar sendo usados para processamento real, fazendo a eficiência despencar de forma desproporcional ao aumento no número de processos.

## 10.4 Houve overhead de paralelização?

Sim. Os principais overheads identificados foram:

- **Context switching (principal causa da queda de 8→12):** com mais processos do que núcleos físicos, o sistema operacional precisa constantemente alternar qual processo está sendo executado em cada núcleo, gerando custo computacional sem produzir resultado útil.
- **Criação e inicialização de processos:** o `multiprocessing.Pool` precisa inicializar cada processo worker com o interpretador Python e as bibliotecas OpenCV e NumPy — esse custo fixo por processo se torna mais significativo proporcionalmente quanto mais processos são criados.
- **Serialização (pickle):** o Pool precisa serializar os dados de entrada e saída para comunicação entre o processo principal e os processos workers.

---

# 11. Conclusão

* **Desempenho:** O paralelismo foi muito eficaz até 8 processos, reduzindo o tempo de **246.6s (serial) para 40.6s (8 processos)** — uma redução de **83,5%**, com speedup de 6.08x.

* **Ponto ótimo identificado:** **8 processos é a configuração ideal** para este hardware — coincide exatamente com o número de núcleos físicos disponíveis (Ryzen 7 5700X, 8 núcleos), maximizando o speedup e mantendo eficiência de 76%.

* **12 processos é contraproducente:** ao ultrapassar o número de núcleos físicos, o desempenho **regride** — tempo pior (47.0s vs 40.6s) e eficiência muito menor (43,7% vs 76%). Isso demonstra, de forma quantitativa, que mais processos nem sempre significa mais velocidade.

* **Causa raiz:** o número de núcleos físicos da CPU é o fator determinante para a escalabilidade do paralelismo neste projeto. Enquanto o número de processos não excede os núcleos físicos, o ganho é consistente; ao exceder, o context switching introduzido degrada o desempenho.

* **Melhor custo-benefício:** a configuração com **2 processos** apresenta a maior eficiência (95%), sendo a escolha ideal quando o objetivo é maximizar o aproveitamento de cada processo, ainda que o tempo absoluto seja maior que com 8 processos.

* **Melhorias possíveis:** para escalar além de 8 processos com eficiência, seria necessário um processador com mais núcleos físicos (ex: Ryzen 9 ou processadores de servidor com 16+ núcleos). Como alternativa, processar as imagens em GPU com OpenCV-CUDA (a RTX 4060 Ti disponível na máquina) eliminaria a dependência do número de núcleos da CPU, já que operações de visão computacional são altamente paralelizáveis em hardware gráfico.

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
