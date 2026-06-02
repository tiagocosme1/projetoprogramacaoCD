# Relatório de Análise de Desempenho - Atividade 3

**Disciplina:** PROGRAMAÇÃO CONCORRENTE E DISTRIBUÍDA  
**Alunos:** João Victor Fernandes De Oliveira (RA: 083318) | Tiago Geraldo de Lima Cosme (RA: 083095)  
**Turma:** ADS e SI
**Professor:** Rafael Marconi  
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
| Memória RAM                 | 8,00 GB (apenas ~552 MB disponíveis durante os testes) |
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
* **Condições:** Execução em máquina local, com carga de sistema variável (processos de fundo do SO ativos). Durante os testes, a memória RAM disponível era de aproximadamente 552 MB, o que pode ter influenciado os resultados com maior número de processos.

---

# 4. Resultados Experimentais

| Nº Threads/Processos | Tempo de Execução (s) |
| -------------------- | --------------------- |
| 1 (Serial)           | 140.2143              |
| 2                    | 61.8382               |
| 4                    | 44.8976               |
| 8                    | 41.0309               |
| 12                   | 43.0464               |

---

# 6. Tabela de Resultados (Cálculos)

| Threads/Processos | Tempo (s) | Speedup | Eficiência |
| ----------------- | --------- | ------- | ---------- |
| 1                 | 140.2143  | 1.0000  | 1.0000     |
| 2                 | 61.8382   | 2.2674  | 1.1337     |
| 4                 | 44.8976   | 3.1230  | 0.7807     |
| 8                 | 41.0309   | 3.4173  | 0.4272     |
| 12                | 43.0464   | 3.2573  | 0.2714     |

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

Com **2 processos** o speedup foi de **2.27**, superando ligeiramente o ideal de 2.0. Isso é possível quando o sistema operacional aproveita melhor o cache do disco ou quando processos paralelos reduzem o tempo de espera por I/O em relação ao serial. Para **4, 8 e 12 processos**, o speedup ficou bem abaixo do linear esperado, atingindo no máximo **3.42 com 8 processos**, quando o ideal seria 8.0. Isso demonstra que o programa não consegue escalar linearmente devido a múltiplos fatores de limitação de hardware.

## A aplicação apresentou escalabilidade?

Sim, mas com **rendimento fortemente decrescente**. O tempo caiu de 140s (serial) para 41s (8 processos), porém com 12 processos o tempo voltou a **subir para 43s**, o que indica que a partir de certo ponto adicionar mais processos passa a prejudicar o desempenho ao invés de melhorá-lo. Essa queda de desempenho com 12 processos é um sinal claro de que os recursos da máquina foram saturados.

## Por que 4 e 8 processos tiveram tempos tão próximos?

O tempo com 4 processos foi de **44.89s** e com 8 processos foi de **41.03s** — uma diferença de apenas ~4 segundos. Isso acontece porque o gargalo do programa não é a CPU, mas sim a **leitura das imagens do disco (I/O Bound)**. Com 4 processos o disco já estava sendo utilizado próximo do seu limite de leitura. Adicionar mais processos (8) não acelera significativamente porque todos ficam concorrendo pelo mesmo recurso: o disco rígido. É como ter 4 ou 8 atendentes em uma loja com apenas 1 caixa — a fila no caixa continua sendo o gargalo independente de quantos atendentes existam.

## Por que 12 processos foi mais lento que 8?

Três fatores combinados explicam esse comportamento:

**1. Limitação de núcleos físicos:** O processador i5-11400H possui apenas **6 núcleos físicos**. Com 12 processos, cada núcleo precisa alternar entre 2 processos simultaneamente (context switching), gerando overhead de troca de contexto que consome tempo de CPU sem realizar trabalho útil.

**2. Memória RAM insuficiente:** Durante os testes, a memória disponível era de apenas **~552 MB**. Cada processo paralelo carrega imagens na memória para processá-las. Com 12 processos simultâneos, a RAM foi rapidamente esgotada, forçando o Windows a utilizar **memória virtual (swap)** — ou seja, gravar e ler dados temporários no disco rígido. Como o disco é muito mais lento que a RAM, isso causa uma queda drástica de desempenho, especialmente com muitos processos.

**3. Overhead de gerenciamento:** O sistema operacional precisa gerenciar 12 processos, alocar memória para cada um, fazer o escalonamento entre os núcleos e controlar a comunicação entre eles. Com 12 processos em um hardware limitado, esse overhead de gerenciamento supera o ganho de paralelismo.

## Em qual ponto a eficiência começou a cair?

A eficiência caiu drasticamente após 2 processos. Com 4 processos ela já estava em **0.78**, com 8 caiu para **0.43** e com 12 chegou a apenas **0.27**. Isso significa que com 12 processos, cada processo está aproveitando apenas 27% da sua capacidade teórica — os outros 73% são perdidos em overhead, espera por I/O e disputa por memória.

## Houve overhead de paralelização?

Sim. Os principais overheads observados foram:
- **Disputa por I/O de disco:** múltiplos processos tentando ler imagens simultaneamente
- **Pressão de memória RAM:** com poucos MB disponíveis, o sistema recorreu ao swap em disco
- **Context switching:** com mais processos que núcleos físicos, a CPU perde tempo trocando entre processos
- **Criação e destruição de processos:** o `multiprocessing.Pool` precisa inicializar cada processo worker com suas bibliotecas (OpenCV, NumPy), o que tem custo inicial

---

# 11. Conclusão

* **Desempenho:** O paralelismo foi eficaz, reduzindo o tempo de processamento de **~140s para ~41s** com 8 processos — uma redução de aproximadamente **71%**. Ainda assim, o ganho ficou muito abaixo do ideal teórico devido às limitações do hardware disponível.

* **Melhor Configuração:** Em termos de tempo bruto, **8 processos** foi o melhor resultado (41.03s). Em termos de custo-benefício (eficiência), a configuração com **2 processos** foi a ideal, com eficiência de 1.13 — aproveitando bem os recursos sem desperdiçar memória ou gerar overhead excessivo.

* **Escalabilidade:** O programa escala até 8 processos, sendo limitado principalmente por três fatores: (1) gargalo de leitura de imagens do disco (I/O Bound), (2) apenas 6 núcleos físicos disponíveis, e (3) memória RAM insuficiente (~552 MB disponíveis), que forçou o uso de swap com configurações maiores.

* **Impacto da memória:** A baixa quantidade de memória RAM disponível durante os testes (552 MB de 8 GB) foi um fator determinante para os resultados com 8 e 12 processos. Em uma máquina com 16 GB de RAM e maior disponibilidade de memória, os resultados com 8 e 12 processos seriam significativamente melhores.

* **Melhorias:** Uma implementação utilizando leitura assíncrona de imagens (`asyncio`) ou pré-carregamento em lotes (batching) antes do processamento poderia reduzir a contenção de I/O. Executar os testes com a máquina mais limpa (menos processos de fundo) e mais memória disponível também melhoraria os resultados. A longo prazo, processar as imagens em GPU com OpenCV-CUDA traria ganhos muito superiores ao paralelismo por CPU.
