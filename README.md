# Relatório de Análise de Desempenho - Atividade 3

**Disciplina:** PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA  
**Alunos:** João Victor Fernandes De Oliveira (RA: 083318) | Tiago Geraldo de Lima Cosme (RA: 083095)  
**Turma:** ADS e SI  
**Professor:** Rafael Marconi Ramos  
**Data:** 02/06/2026  

---

# 1. Descrição do Problema

O programa resolve o problema de classificação automática de vagas de estacionamento a partir de imagens capturadas por câmeras de vigilância. O sistema percorre recursivamente uma massa de imagens do dataset **PKLot (UFPR04 + UFPR05)** para classificar cada vaga como **livre** ou **ocupada** utilizando técnicas de visão computacional com OpenCV.

* **Algoritmo:** Para cada imagem, o sistema aplica as seguintes etapas de processamento: (1) conversão para escala de cinza, (2) filtro Gaussiano para suavização, (3) equalização de histograma para melhora de contraste, (4) detecção de bordas com algoritmo de Canny, (5) filtro Laplaciano para detecção de bordas de alta frequência, (6) Transformada de Hough para detecção de linhas, e (7) cálculo de score combinado de densidade de bordas e desvio padrão. O modelo paralelo utiliza **`multiprocessing.Pool`** para distribuir o processamento entre múltiplos processos.
* **Tamanho da Entrada:** 7.416 imagens JPEG (UFPR04 + UFPR05), totalizando ~1,95 GB.
* **Objetivo:** O objetivo da paralelização é reduzir o tempo total de resposta (latency) ao distribuir a carga de processamento de imagens entre os múltiplos núcleos da CPU, superando o gargalo da execução sequencial.
* **Complexidade:** Aproximadamente $O(n \times p)$, onde $n$ é o número de imagens e $p$ é o custo de processamento por imagem (múltiplos filtros e transformadas).

---

# 2. Ambiente Experimental

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz |
| Número de núcleos           | 6 Núcleo(s) / 12 Threads |
| Memória RAM                 | 8,00 GB |
| Sistema Operacional         | Microsoft Windows 11 Home Single Language |
| Armazenamento               | SSD NVMe WD PC SN530 (1 TB) |
| Linguagem utilizada         | Python 3.x |
| Biblioteca de paralelização | Multiprocessing (stdlib) |
| Bibliotecas de visão        | OpenCV, NumPy |
| Compilador / Versão         | Python 3.x |

---

# 3. Metodologia de Testes

Os experimentos foram conduzidos medindo o tempo total de execução ("Wall Time") utilizando a função `time.perf_counter()`.

* **Execuções:** Foi realizada uma medição para cada configuração de processos.
* **Entrada:** Massa de teste fixa (pastas UFPR04 + UFPR05) com 7.416 imagens JPEG.
* **Configurações:** Testes realizados com 1 (serial), 2, 4, 8 e 12 processos.
* **Condições:** Execução em máquina local com carga de sistema reduzida (navegador, Discord e demais aplicativos fechados). É importante destacar que os resultados podem variar conforme a quantidade de memória RAM disponível no momento da execução — em testes realizados com muitos programas abertos, os tempos foram significativamente piores. Isso demonstra que a carga do sistema operacional impacta diretamente o desempenho, sendo recomendado sempre executar os testes com o menor número de programas abertos possível.

---

# 4. Resultados Experimentais

| Nº Threads/Processos | Tempo de Execução (s) |
| -------------------- | --------------------- |
| 1 (Serial)           | 259.8428              |
| 2                    | 154.9140              |
| 4                    | 105.3845              |
| 8                    | 95.7553               |
| 12                   | 89.6858               |

---

# 5. Resultados da Classificação

| Informação | Resultado |
| ---------- | --------- |
| Total de imagens processadas | 7.416 |
| Vagas livres identificadas | 1.319 |
| Vagas ocupadas identificadas | 6.097 |
| Erros | 0 |

---

# 6. Tabela de Resultados (Cálculos)

| Threads/Processos | Tempo (s) | Speedup | Eficiência |
| ----------------- | --------- | ------- | ---------- |
| 1                 | 259.8428  | 1.0000  | 1.0000     |
| 2                 | 154.9140  | 1.6773  | 0.8387     |
| 4                 | 105.3845  | 2.4657  | 0.6164     |
| 8                 | 95.7553   | 2.7136  | 0.3392     |
| 12                | 89.6858   | 2.8973  | 0.2414     |

---

# 7. Gráfico de Tempo de Execução
![Gráfico Tempo Execução](graficos/tempo_execucao.png)

# 8. Gráfico de Speedup
![Gráfico Speedup](graficos/speedup.png)

# 9. Gráfico de Eficiência
![Gráfico Eficiência](graficos/eficiencia.png)

---

# 10. Análise dos Resultados

## O que é I/O Bound e por que afeta o desempenho?

Antes de analisar os resultados, é importante entender o conceito de **I/O Bound**. Uma aplicação é considerada I/O Bound quando o seu maior gargalo não é o processador (CPU), mas sim operações de entrada e saída — no caso deste projeto, a **leitura das imagens do disco**. Enquanto um processo lê sua imagem, os outros ficam com a CPU **parada esperando** — e CPU parada é eficiência desperdiçada. Isso explica por que adicionar mais processos nem sempre resulta em ganho proporcional de desempenho. Vale destacar que mesmo com um **SSD NVMe** (WD PC SN530), que é um dos tipos de armazenamento mais rápidos disponíveis, o gargalo de I/O ainda existe quando múltiplos processos competem simultaneamente pelo mesmo recurso. O principal limitador neste projeto, no entanto, é a quantidade de **núcleos físicos da CPU**, conforme explicado nas seções seguintes.

## O speedup obtido foi próximo do ideal?

O speedup obtido ficou abaixo do ideal linear em todas as configurações. Com **2 processos** o speedup foi de **1.68** (ideal seria 2.0), com **4 processos** foi de **2.47** (ideal seria 4.0), com **8 processos** foi de **2.71** (ideal seria 8.0) e com **12 processos** atingiu **2.90** (ideal seria 12.0). Embora o speedup tenha crescido a cada configuração, a distância em relação ao ideal aumenta progressivamente, demonstrando que o programa não consegue escalar linearmente devido aos fatores descritos abaixo.

## A aplicação apresentou escalabilidade?

Sim. O tempo continuou caindo a cada configuração — de 259s (serial) para 154s (2 processos), 105s (4 processos), 95s (8 processos) e 89s (12 processos). Isso ocorre porque o algoritmo robusto utilizado (com Laplaciano, Hough e múltiplas etapas) tornou o processamento mais **CPU-bound**, fazendo com que cada processo adicional contribua com trabalho útil antes de saturar os recursos da máquina.

## Por que o speedup não cresce proporcionalmente ao número de processos?

O speedup não é linear por uma combinação de fatores:

**1. Limitação de núcleos físicos:** O processador i5-11400H possui apenas **6 núcleos físicos** (12 threads via Hyper-Threading). Com 8 ou 12 processos, o sistema operacional precisa escalonar mais processos do que núcleos físicos disponíveis, gerando **context switching** — troca de contexto que consome tempo de CPU sem realizar trabalho útil na aplicação. Este é o principal fator limitante nos resultados obtidos.

**2. Gargalo de I/O:** Mesmo com SSD NVMe, quando múltiplos processos acessam o disco simultaneamente ocorre contenção — todos competem pelo mesmo recurso. Isso limita o ganho real mesmo quando a CPU tem capacidade disponível.

**3. Overhead de criação e gerenciamento de processos:** O `multiprocessing.Pool` precisa inicializar cada processo worker com o interpretador Python e todas as bibliotecas (OpenCV, NumPy). Esse custo de inicialização é fixo e representa um overhead que não escala com o número de imagens processadas.

## Por que a eficiência cai conforme aumentam os processos?

A eficiência mede o quanto cada processo está sendo aproveitado em relação ao seu potencial teórico. Com **2 processos** a eficiência foi de **0.84** — cada processo aproveitou 84% de sua capacidade teórica. Com **4 processos** caiu para **0.62**, com **8** para **0.34** e com **12** chegou a apenas **0.24**. Isso significa que com 12 processos, 76% do potencial computacional está sendo desperdiçado em overhead e context switching — consequência direta de executar mais processos do que núcleos físicos disponíveis.

## Por que o tempo com 8 e 12 processos é próximo?

O tempo com 8 processos foi de **95.75s** e com 12 processos foi de **89.68s** — uma diferença de apenas ~6 segundos para 4 processos extras. Com 8 processos já ultrapassamos o limite de 6 núcleos físicos, e adicionar mais 4 processos (totalizando 12) gera ainda mais context switching. O ganho marginal existe mas é pequeno porque o sistema operacional está gastando cada vez mais tempo alternando entre processos em vez de processá-los. É como adicionar mais carros numa pista que já está congestionada — o trânsito melhora pouco e o caos aumenta.

## Impacto da carga do sistema nos resultados

Os resultados são sensíveis à carga do sistema operacional no momento da execução. Em testes realizados com o navegador com 14 abas abertas, Discord e outros programas ativos, os tempos foram significativamente piores. Ao fechar esses programas e liberar memória RAM, os resultados melhoraram consideravelmente. Em máquinas com 8 GB de RAM, a concorrência por memória entre o programa e outros processos do sistema operacional é um fator determinante no desempenho.

## Houve overhead de paralelização?

Sim. Os principais overheads observados foram:
- **Context switching:** com mais processos que núcleos físicos, a CPU alterna entre processos gastando tempo sem realizar trabalho útil
- **Contenção de I/O:** múltiplos processos acessando o disco simultaneamente, mesmo sendo SSD NVMe
- **Criação e inicialização de processos:** o `multiprocessing.Pool` precisa inicializar cada processo worker com o interpretador Python e bibliotecas (OpenCV, NumPy)
- **Serialização de dados (pickle):** o pool precisa serializar os caminhos das imagens para enviar aos processos filhos

---

# 11. Conclusão

* **Desempenho:** O paralelismo foi eficaz, reduzindo o tempo de processamento de **~259s para ~89s** com 12 processos — uma redução de aproximadamente **65%**. Com o algoritmo mais robusto (múltiplas etapas de visão computacional), o ganho de paralelismo foi mais expressivo, pois a carga de CPU por imagem aumentou tornando o processamento mais CPU-bound.

* **Melhor Configuração:** Em termos de tempo bruto, **12 processos** foi o melhor resultado (89.68s). Em termos de custo-benefício (eficiência), a configuração com **2 processos** foi a mais equilibrada, com eficiência de 0.84 — aproveitando bem os recursos sem gerar overhead excessivo.

* **Escalabilidade:** O programa escala progressivamente até 12 processos, com ganhos decrescentes. A limitação principal são os apenas **6 núcleos físicos** disponíveis — testar com 8 e 12 processos em uma máquina de 6 núcleos inevitavelmente gera context switching excessivo, limitando o speedup obtido.

* **Variação por carga do sistema:** Os resultados são sensíveis à quantidade de memória e recursos disponíveis no momento da execução. Em máquinas com 8 GB de RAM, recomenda-se fechar programas desnecessários antes de executar o processamento paralelo para obter resultados mais consistentes e representativos.

* **Melhorias:** A principal melhoria seria utilizar uma máquina com mais núcleos físicos (8 ou 12 núcleos), o que permitiria aproveitar melhor as configurações de 8 e 12 processos sem gerar context switching. Adicionalmente, processar as imagens em GPU com OpenCV-CUDA traria ganhos muito superiores ao paralelismo por CPU, pois as operações de visão computacional são altamente paralelizáveis em GPU.
