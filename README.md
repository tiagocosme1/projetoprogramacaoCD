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
| Número de núcleos físicos   | 6 Núcleos (12 Threads via Hyper-Threading) |
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
* **Condições:** Execução em máquina local com carga de sistema reduzida (navegador, Discord e demais aplicativos fechados).
* **Monitoramento adicional:** Além do tempo de execução, foi monitorado o uso de **CPU** e **Memória RAM** durante cada configuração, utilizando o Gerenciador de Tarefas do Windows, para identificar com precisão qual recurso era o gargalo real da aplicação (seção 10 detalha essa investigação).
* **Variação entre execuções:** Foi observado que repetir os mesmos testes em momentos diferentes gera tempos levemente diferentes (variações de 5 a 15%), devido a processos de fundo do sistema operacional e ajuste dinâmico de frequência da CPU. Por esse motivo, os valores apresentados na tabela de resultados representam uma execução típica, sendo a tendência geral (queda de tempo, queda de eficiência) o dado mais importante a ser analisado, e não o valor absoluto de cada execução isolada.

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

## 10.1 O que é I/O Bound e o que é CPU Bound?

Antes de analisar os resultados, é importante esclarecer dois conceitos. Uma aplicação é **I/O Bound** quando seu maior gargalo é a entrada/saída de dados (leitura de disco, rede), e os processos ficam frequentemente com a CPU **ociosa esperando** esses dados chegarem. Já uma aplicação é **CPU Bound** quando o gargalo é a capacidade de processamento — a CPU está constantemente ocupada calculando, e o tempo de espera por disco é insignificante.

Inicialmente, suspeitou-se que o projeto fosse I/O Bound (gargalo no disco) ou limitado pela memória RAM. Para confirmar a causa real, foi realizada uma investigação prática descrita a seguir.

## 10.2 Investigação prática: CPU, Memória e a hipótese da RAM

Durante a execução do `paralelo.py`, foi monitorado o uso de **CPU** e **Memória RAM** pelo Gerenciador de Tarefas do Windows, para cada configuração de processos:

| Processos | Uso de CPU | Uso de Memória RAM |
| --------- | ---------- | ------------------- |
| 2         | 40% – 66%  | 82% – 87% (6,4–6,8 / 7,8 GB) |
| 4         | 66%        | 87% (6,8 / 7,8 GB) |
| 8         | 92%        | 87% (6,8 / 7,8 GB) |
| 12        | 95% – 97%  | 87% – 90% (6,8–7,0 / 7,8 GB) |

**Análise desses dados:** o uso de memória RAM permaneceu **praticamente constante** (entre 82% e 90%) em todas as configurações testadas, não importando se eram 2 ou 12 processos. Isso indica que a memória já estava naquele patamar antes mesmo da execução do script (consumida pelo próprio Windows e processos em segundo plano), e **não cresceu proporcionalmente ao número de processos paralelos**.

Já o uso de **CPU escalou claramente** com o número de processos: de 40-66% (2 e 4 processos) para 92-97% (8 e 12 processos). Isso evidencia que, a partir de 8 processos, a CPU está **praticamente saturada** — ou seja, o gargalo real do projeto é a **capacidade de processamento da CPU**, não a memória RAM.

**Testando a hipótese de otimização de memória:** como o orientador sugeriu que o problema poderia ser consumo excessivo de RAM forçando o uso de memória virtual (swap), foi implementada uma versão otimizada do `paralelo.py` utilizando `pool.imap_unordered()` com `chunksize` reduzido e `maxtasksperchild` (para reiniciar processos periodicamente e evitar acúmulo de memória). Os resultados dessa versão otimizada foram comparados com a versão original:

| Processos | Tempo (original) | Tempo (otimizado p/ RAM) | Diferença |
| --------- | ----------------- | -------------------------- | --------- |
| 2         | 158.64s            | 157.01s                     | -1.6s |
| 4         | 105.86s            | 105.48s                     | -0.4s |
| 8         | 94.95s             | 91.85s                      | -3.1s |
| 12        | 91.89s             | 91.11s                      | -0.8s |

A diferença foi mínima (menos de 3 segundos em todos os casos), o que **comprova que o problema não é causado por acúmulo de memória ou memory leak** — caso contrário, a otimização teria reduzido o tempo de forma muito mais expressiva, especialmente em 8 e 12 processos. Esse teste confirma que o gargalo real é a CPU, e não a memória RAM.

## 10.3 O speedup obtido foi próximo do ideal?

O speedup obtido ficou abaixo do ideal linear em todas as configurações. Com **2 processos** o speedup foi de **1.68** (ideal seria 2.0), com **4 processos** foi de **2.47** (ideal seria 4.0), com **8 processos** foi de **2.71** (ideal seria 8.0) e com **12 processos** atingiu **2.90** (ideal seria 12.0). A distância em relação ao ideal aumenta progressivamente conforme mais processos são adicionados.

## 10.4 Por que o tempo de execução com 8 e 12 processos é tão parecido?

Esta é a observação central deste relatório, e a investigação da seção 10.2 explica exatamente o motivo: **o processador possui apenas 6 núcleos físicos**. Com 8 processos, já estamos pedindo 2 processos extras além da capacidade física de execução simultânea da CPU — e com 12 processos, o dobro. Quando isso acontece, o sistema operacional precisa fazer **context switching**: pausar um processo, salvar seu estado, carregar outro processo no mesmo núcleo, e repetir esse ciclo constantemente. Esse processo consome tempo de CPU **sem realizar nenhum trabalho útil de classificação de imagens** — é puro custo administrativo do sistema operacional.

Isso foi confirmado na prática: o uso de CPU subiu para 92% (8 processos) e 95-97% (12 processos) — ou seja, a CPU já está no seu limite máximo de capacidade a partir de 8 processos. Adicionar mais processos depois desse ponto não traz mais "poder de processamento" disponível — só mais fila de espera e mais trocas de contexto. É como tentar colocar mais carros numa autoestrada que já está no limite da sua capacidade: o fluxo não melhora, e o congestionamento (overhead) aumenta.

## 10.5 Por que a eficiência cai tanto conforme aumentam os processos?

A eficiência mede o quanto cada processo está sendo aproveitado em relação ao seu potencial teórico (eficiência = speedup ÷ número de processos). Com **2 processos** a eficiência foi de **0.84** (84% aproveitado), com **4 processos** caiu para **0.62**, com **8** para **0.34** e com **12** chegou a apenas **0.24**.

A queda é matematicamente esperada quando o número de processos ultrapassa o número de núcleos físicos: como demonstrado na seção 10.2, a partir de 8 processos a CPU já está saturada (92-97%), então o "trabalho extra" de cada processo adicional é, em boa parte, apenas overhead de gerenciamento — e não processamento real de imagens. Por isso a eficiência cai de forma acentuada: estamos dividindo o mesmo "bolo" de capacidade de CPU entre cada vez mais processos, e cada fatia rende cada vez menos.

## 10.6 Houve overhead de paralelização?

Sim. Com base na investigação prática realizada, os principais overheads identificados foram:

- **Context switching (principal causa):** com 8 e 12 processos rodando em apenas 6 núcleos físicos, a CPU constantemente troca de contexto entre processos, gerando custo computacional sem trabalho útil. Confirmado pelo uso de CPU em 92-97% nessas configurações.
- **Criação e inicialização de processos:** o `multiprocessing.Pool` precisa inicializar cada processo worker com o interpretador Python e bibliotecas (OpenCV, NumPy), processo que tem custo fixo independente do volume de trabalho.
- **Variação do sistema operacional:** testes repetidos nas mesmas condições apresentaram variações de tempo entre 5% e 15%, devido a processos de fundo do Windows e ajuste dinâmico de frequência da CPU (Turbo Boost).
- **Memória RAM:** descartada como causa principal após teste prático (seção 10.2) — o consumo de RAM permaneceu estável (82-90%) independente do número de processos, e uma versão otimizada para reduzir uso de memória não trouxe melhora significativa de tempo.

---

# 11. Conclusão

* **Desempenho:** O paralelismo foi eficaz, reduzindo o tempo de processamento de **~259s para ~89s** com 12 processos — uma redução de aproximadamente **65%**.

* **Causa raiz da eficiência baixa (confirmada com evidência prática):** através do monitoramento de CPU e memória durante a execução, foi comprovado que o gargalo real do projeto é a **limitação de 6 núcleos físicos** do processador, e não a memória RAM como inicialmente suspeitado. O uso de CPU sobe para 92-97% a partir de 8 processos (acima do número de núcleos físicos), gerando context switching excessivo, enquanto o uso de memória permanece estável (82-90%) independente do número de processos. Uma tentativa de otimizar o uso de memória (`imap_unordered` + `maxtasksperchild`) resultou em ganhos inferiores a 3 segundos em todas as configurações, confirmando que a memória não era a causa do problema.

* **Melhor Configuração:** Em termos de tempo bruto, **12 processos** foi o melhor resultado (89.68s). Em termos de custo-benefício (eficiência), a configuração com **2 processos** foi a mais equilibrada, com eficiência de 0.84.

* **Escalabilidade:** O programa escala progressivamente até 12 processos, mas com ganhos cada vez menores a partir de 8 processos — exatamente o ponto em que a quantidade de processos supera a quantidade de núcleos físicos (6) disponíveis na máquina.

* **Melhorias possíveis:** A melhoria mais efetiva seria executar o programa em uma máquina com mais núcleos físicos (8 ou 12 núcleos reais), eliminando o context switching observado. Como alternativa, processar as imagens em GPU utilizando OpenCV-CUDA traria ganhos superiores ao paralelismo por CPU, já que operações de visão computacional (convoluções, filtros, transformadas) são altamente paralelizáveis em hardware gráfico, que possui milhares de núcleos simples otimizados para esse tipo de cálculo.
