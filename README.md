# Relatório de Análise de Desempenho - Atividade 3

**Disciplina:** PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA  
**Alunos:** João Victor Fernandes De Oliveira (RA: 083318) | Tiago Geraldo de Lima Cosme (RA: 083095)  
**Turma:** ADS e SI  
**Professor:** Rafael Marconi Ramos 
**Data:** 02/06/2026  

---

# 1. Descrição do Problema

O programa resolve o problema de classificação automática de vagas de estacionamento a partir de imagens capturadas por câmeras de vigilância. O sistema percorre recursivamente uma massa de imagens do dataset **PKLot (UFPR04 + UFPR05)** para classificar cada vaga como **livre** ou **ocupada** utilizando técnicas de visão computacional com OpenCV.

* **Algoritmo:** Para cada imagem, o sistema aplica conversão para escala de cinza, filtro Gaussiano, detecção de bordas (Canny) e calcula um score combinado de densidade de bordas e desvio padrão — vagas ocupadas possuem mais bordas e textura (contorno do veículo). O modelo paralelo utiliza **`multiprocessing.Pool`** para distribuir o processamento entre múltiplos processos.
* **Tamanho da Entrada:** 7.416 imagens JPEG (UFPR04 + UFPR05), totalizando ~1,95 GB.
* **Objetivo:** O objetivo da paralelização é reduzir o tempo total de resposta (latency) ao distribuir a carga de processamento de imagens entre os múltiplos núcleos da CPU, superando o gargalo da execução sequencial.
* **Complexidade:** Aproximadamente $O(n \times p)$, onde $n$ é o número de imagens e $p$ é o custo de processamento por imagem (filtros + cálculo de bordas).

---

# 2. Ambiente Experimental

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz |
| Número de núcleos           | 6 Núcleo(s) / 12 Threads |
| Memória RAM                 | 8,00 GB |
| Sistema Operacional         | Microsoft Windows 11 Home Single Language |
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
* **Condições:** Execução em máquina local com carga de sistema reduzida (navegador, Discord e demais aplicativos fechados). É importante destacar que os resultados podem variar conforme a quantidade de memória RAM disponível no momento da execução — em testes realizados com muitos programas abertos, o tempo serial chegou a **140s**, enquanto com o sistema mais limpo o mesmo processamento levou **97s**, uma diferença de aproximadamente 30%. Isso demonstra que a carga do sistema operacional impacta diretamente o desempenho, mesmo no processamento serial.

---

# 4. Resultados Experimentais

| Nº Threads/Processos | Tempo de Execução (s) |
| -------------------- | --------------------- |
| 1 (Serial)           | 97.8697               |
| 2                    | 60.1549               |
| 4                    | 43.8804               |
| 8                    | 41.5875               |
| 12                   | 42.3247               |

---

# 6. Tabela de Resultados (Cálculos)

| Threads/Processos | Tempo (s) | Speedup | Eficiência |
| ----------------- | --------- | ------- | ---------- |
| 1                 | 97.8697   | 1.0000  | 1.0000     |
| 2                 | 60.1549   | 1.6271  | 0.8135     |
| 4                 | 43.8804   | 2.2304  | 0.5576     |
| 8                 | 41.5875   | 2.3533  | 0.2942     |
| 12                | 42.3247   | 2.3124  | 0.1927     |

---

# 7. Gráfico de Tempo de Execução
![Gráfico Tempo Execução](graficos/tempo_execucao.png)

# 8. Gráfico de Speedup
![Gráfico Speedup](graficos/speedup.png)

# 9. Gráfico de Eficiência
![Gráfico Eficiência](graficos/eficiencia.png)

---

# 10. Análise dos Resultados

## O speedup obtido foi próximo do ideal?

O speedup obtido ficou bem abaixo do ideal linear em todas as configurações. Com **2 processos** o speedup foi de **1.63** (ideal seria 2.0), com **4 processos** foi de **2.23** (ideal seria 4.0) e com **8 processos** atingiu o máximo de **2.35** (ideal seria 8.0). Isso demonstra que o programa não consegue escalar linearmente devido a múltiplos fatores de limitação de hardware e características da carga de trabalho.

## A aplicação apresentou escalabilidade?

Sim, mas com **rendimento fortemente decrescente**. O tempo caiu de 97s (serial) para 41s (8 processos), porém com 12 processos o tempo voltou a **subir para 42s**, indicando que a partir de certo ponto adicionar mais processos passa a prejudicar o desempenho. Essa queda com 12 processos é um sinal claro de que os recursos da máquina foram saturados.

## Por que 4 e 8 processos tiveram tempos tão próximos?

O tempo com 4 processos foi de **43.88s** e com 8 processos foi de **41.58s** — uma diferença de apenas ~2 segundos. Isso acontece porque o gargalo do programa não é a CPU, mas sim a **leitura das imagens do disco (I/O Bound)**. Com 4 processos o disco já estava sendo utilizado próximo do seu limite de leitura. Adicionar mais processos (8) não acelera significativamente porque todos ficam concorrendo pelo mesmo recurso: o disco rígido. É como ter 4 ou 8 atendentes em uma loja com apenas 1 caixa — a fila no caixa continua sendo o gargalo independente de quantos atendentes existam.

## Por que 12 processos foi mais lento que 8?

Dois fatores combinados explicam esse comportamento:

**1. Limitação de núcleos físicos:** O processador i5-11400H possui apenas **6 núcleos físicos**. Com 12 processos, cada núcleo precisa alternar entre 2 processos simultaneamente (context switching), gerando overhead de troca de contexto que consome tempo de CPU sem realizar trabalho útil.

**2. Overhead de gerenciamento:** O sistema operacional precisa gerenciar 12 processos, alocar memória para cada um, fazer o escalonamento entre os núcleos e controlar a comunicação entre eles. Com 12 processos em um hardware limitado, esse overhead supera o ganho de paralelismo.

## Em qual ponto a eficiência começou a cair?

A eficiência caiu desde o início — já com 2 processos foi de **0.81**, com 4 caiu para **0.56**, com 8 chegou a **0.29** e com 12 atingiu apenas **0.19**. Isso significa que com 12 processos, cada processo está aproveitando apenas 19% da sua capacidade teórica — os outros 81% são perdidos em overhead, espera por I/O e disputas entre processos.

## Impacto da carga do sistema nos resultados

Um fator importante observado durante os testes foi a influência da carga do sistema operacional nos resultados. Em uma execução realizada com o navegador (14 abas abertas), Discord e outros programas ativos, o tempo serial foi de **140s**. Ao fechar esses programas e liberar memória RAM, o mesmo processamento serial levou apenas **97s** — uma melhora de **30% simplesmente por liberar recursos do sistema**. Isso evidencia que em máquinas com 8 GB de RAM, a concorrência por memória entre o programa e outros processos do sistema operacional é um fator determinante no desempenho, podendo variar significativamente entre execuções.

## Houve overhead de paralelização?

Sim. Os principais overheads observados foram:
- **Disputa por I/O de disco:** múltiplos processos tentando ler imagens simultaneamente
- **Context switching:** com mais processos que núcleos físicos, a CPU perde tempo trocando entre processos
- **Criação e inicialização de processos:** o `multiprocessing.Pool` precisa inicializar cada processo worker com suas bibliotecas (OpenCV, NumPy), o que tem custo inicial

---

# 11. Conclusão

* **Desempenho:** O paralelismo foi eficaz, reduzindo o tempo de processamento de **~97s para ~41s** com 8 processos — uma redução de aproximadamente **57%**. Ainda assim, o ganho ficou abaixo do ideal teórico devido às características I/O Bound da aplicação e às limitações do hardware disponível.

* **Melhor Configuração:** Em termos de tempo bruto, **8 processos** foi o melhor resultado (41.58s). Em termos de custo-benefício (eficiência), a configuração com **2 processos** foi a mais equilibrada, com eficiência de 0.81 — aproveitando bem os recursos sem gerar overhead excessivo.

* **Escalabilidade:** O programa escala até 8 processos, sendo limitado principalmente por dois fatores: (1) gargalo de leitura de imagens do disco (I/O Bound) e (2) apenas 6 núcleos físicos disponíveis. A partir de 8 processos o overhead de gerenciamento supera o ganho de paralelismo.

* **Variação por carga do sistema:** Os resultados são sensíveis à quantidade de memória e recursos disponíveis no momento da execução. Em máquinas com 8 GB de RAM, recomenda-se fechar programas desnecessários antes de executar o processamento paralelo para obter resultados mais consistentes e representativos.

* **Melhorias:** Uma implementação utilizando leitura assíncrona de imagens (`asyncio`) ou pré-carregamento em lotes (batching) poderia reduzir a contenção de I/O. A longo prazo, processar as imagens em GPU com OpenCV-CUDA traria ganhos muito superiores ao paralelismo por CPU.
