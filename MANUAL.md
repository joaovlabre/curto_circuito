# Manual do Usuário — Curto-Circuito MT/BT

**Versão:** 0.1.0  
**Norma:** IEC 60909:2016  
**Plataforma:** Windows (Python 3.11+)

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Instalação](#2-instalação)
3. [Interface do Programa](#3-interface-do-programa)
4. [Montagem da Rede](#4-montagem-da-rede)
5. [Executar o Estudo](#5-executar-o-estudo)
6. [Interpretar os Resultados](#6-interpretar-os-resultados)
7. [Salvar e Abrir Projetos](#7-salvar-e-abrir-projetos)
8. [Exportar Relatórios](#8-exportar-relatórios)
9. [Conceitos de Cálculo (IEC 60909)](#9-conceitos-de-cálculo-iec-60909)
10. [Perguntas Frequentes](#10-perguntas-frequentes)

---

## 1. Visão Geral

O **Curto-Circuito MT/BT** é um software de cálculo de correntes de curto-circuito para instalações elétricas industriais e comerciais com barras de média tensão (MT) e baixa tensão (BT). Os cálculos seguem rigorosamente a norma **IEC 60909:2016**.

### Tipos de falta calculados

| Símbolo | Tipo de Falta |
|---------|---------------|
| **3F** | Trifásico simétrico |
| **2F** | Bifásico fase–fase (sem terra) |
| **1F-T** | Monofásico fase–terra |
| **2F-T** | Bifásico fase–fase–terra |

### Grandezas calculadas por barra

- **Ik''** — corrente simétrica inicial (valor eficaz, kA)
- **Ip** — corrente de pico (kA)
- **Ib** — corrente de abertura (kA)
- **κ** — fator de pico

---

## 2. Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip atualizado

### Instalar dependências

```bash
cd "C:\Claude Code\Curto_circuito"
pip install -r requirements.txt
```

### Iniciar o programa

```bash
python main.py
```

---

## 3. Interface do Programa

A janela principal é dividida em quatro áreas:

```
┌──────────────────────────────────────────────────────────────────┐
│  Barra de Menus: [Arquivo] [Estudo] [Exportar]                   │
│  Barra de Ferramentas: [▶ Executar Estudo] [Excel] [PDF]         │
├─────────────────┬────────────────────────────┬───────────────────┤
│                 │                            │                   │
│  ÁRVORE DA REDE │   DIAGRAMA UNIFILAR        │  (futuro:         │
│  (esquerda)     │   (centro)                 │   propriedades)   │
│                 │                            │                   │
│  ⊞ Rede         │  Barra MT                  │                   │
│   ├─[T1]→ BT    │   └──[T1]── Barra BT       │                   │
│   └─[T2]→ BT2   │            └──[C1]── Carga │                   │
│                 │                            │                   │
├─────────────────┴────────────────────────────┴───────────────────┤
│  TABELA DE RESULTADOS                                            │
│  Barra │ Un(kV) │ Ik3''(kA) │ Ip(kA) │ Ik2''│ Ik1'' │ Ik2E''   │
├──────────────────────────────────────────────────────────────────┤
│  Barra de Status                  [▶ Executar Estudo] [Excel]   │
└──────────────────────────────────────────────────────────────────┘
```

### Árvore da Rede (painel esquerdo)

Exibe a hierarquia da rede como um grafo em árvore. Cada ramo mostra o componente de conexão (`[Transformer]`, `[Cable]`) e o nó filho (barra de chegada).

**Botões da barra de ferramentas da árvore:**

| Botão | Ação |
|-------|------|
| `+ Rede` | Adiciona a conexão com a rede da concessionária (raiz) |
| `+ Trafo` | Adiciona transformador MT/BT ao nó selecionado |
| `+ Cabo` | Adiciona trecho de cabo ao nó selecionado |
| `+ Barra` | Adiciona barra intermediária ao nó selecionado |
| `Remover` | Remove o nó selecionado e todos os seus filhos |

> **Dica:** Clique com o botão direito em qualquer nó da árvore para acessar o menu de contexto com as mesmas opções.

### Diagrama Unifilar (painel central)

Representação gráfica simplificada da rede. Cores:
- **Azul escuro** — nó da rede/concessionária
- **Amarelo** — transformador
- **Verde** — cabo
- **Cinza** — barra

Use o mouse para arrastar (panorâmica) e a roda de rolagem para zoom.

---

## 4. Montagem da Rede

A montagem segue sempre a ordem: **da fonte para as cargas**.

### Passo 1 — Adicionar a conexão de rede

Clique em **`+ Rede`**. Preencha:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| ID | Identificador único | `GRID1` |
| Nome | Nome descritivo | `Concessionária CEMIG` |
| Tensão nominal Un | Tensão do barramento MT (kV) | `13,8` |
| Potência de CC Sk'' | Potência de curto disponível na entrada (MVA) | `500` |
| Razão R/X | Razão resistência/reatância da rede | `0,1` |
| Fator cmax | `1,10` para MT/AT; `1,05` para BT | `1,10` |

> **Sk'' = 0** configura barra infinita (impedância de rede = zero).

---

### Passo 2 — Adicionar Transformador

Selecione o nó MT na árvore → clique em **`+ Trafo`**:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| Sn (MVA) | Potência nominal | `0,630` |
| Un1 (kV) | Tensão do primário | `13,8` |
| Un2 (kV) | Tensão do secundário | `0,4` |
| uk% | Tensão de curto-circuito | `4,0` |
| Pk (kW) | Perdas em carga (corrente nominal) | `6,0` |
| Grupo vetorial | Define o caminho da seq. zero | `Dyn11` |
| Aterramento | Tipo de aterramento do neutro | `solid` |

Ao confirmar, o programa cria automaticamente:
- Um **ramo** com o transformador como componente
- Um **nó filho** representando a **barra secundária (BT)**, nomeado como `Barra [Nome] — [Un2] kV (Sec.)`

> **Importante — MT e BT na tabela de resultados:**  
> O nó pai (de onde você adicionou o trafo) representa a **barra de MT** do transformador.  
> O nó filho criado automaticamente representa a **barra de BT** (secundário).  
> Ambos aparecem na tabela de resultados — um na tensão de MT, outro na tensão de BT.  
> Se quiser uma barra MT separada e explicitamente nomeada, adicione primeiro um `+ Barra` na tensão de MT e depois conecte o trafo a ela.

---

### Passo 3 — Adicionar Cabos (opcional)

Selecione o nó de destino → clique em **`+ Cabo`**:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| Un (kV) | Tensão nominal do cabo | `0,4` |
| R1 (Ω/km) | Resistência seq. positiva | `0,206` |
| X1 (Ω/km) | Reatância seq. positiva | `0,080` |
| R0 (Ω/km) | Resistência seq. zero | `0,618` |
| X0 (Ω/km) | Reatância seq. zero | `0,240` |
| Comprimento (m) | Extensão do trecho | `100` |

> **Dica:** Para cabos de MT, use os valores do catálogo do fabricante referidos à tensão nominal.  
> Valores típicos para cabo 185 mm² Al XLPE 0,6/1 kV: R1 = 0,206 Ω/km, X1 = 0,08 Ω/km.

---

### Exemplo: Rede simples típica

```
[+ Rede] Concessionária (13,8 kV, 500 MVA)
    │
[+ Trafo] T1 – 630 kVA, 13,8/0,4 kV, uk=4%, Pk=6 kW, Dyn11
    │
    └── Barra T1 — 0,4 kV (Sec.)    ← nó criado automaticamente
            │
        [+ Cabo] C1 – 185 mm² Al, 100 m
            │
            └── Barra C1 (carga)
```

---

### Múltiplos transformadores

Para adicionar um segundo transformador no mesmo barramento de MT:

1. Selecione o nó da rede (ou barra MT) na árvore
2. Clique em `+ Trafo` novamente
3. O novo trafo aparece como segundo filho do mesmo nó MT

```
Concessionária (13,8 kV)
├── [T1] → Barra T1 — 0,4 kV (Sec.)
└── [T2] → Barra T2 — 0,4 kV (Sec.)
```

---

## 5. Executar o Estudo

Clique em **`▶ Executar Estudo`** (barra de ferramentas ou menu **Estudo**).

Há duas opções:

| Opção | Fator c | Uso |
|-------|---------|-----|
| **Executar (Imáx)** | cmax = 1,10 | Dimensionamento de equipamentos (disjuntores, cabos, barramentos) |
| **Executar (Imín)** | cmin = 1,00 | Ajuste de relés de sobrecorrente e proteções |

> O cálculo é executado em segundo plano. Para redes grandes, aguarde a mensagem de conclusão na barra de status.

---

## 6. Interpretar os Resultados

A tabela na parte inferior exibe uma linha por barra:

| Coluna | Grandeza | Unidade |
|--------|----------|---------|
| **Barra** | Nome do nó | — |
| **Un (kV)** | Tensão nominal da barra | kV |
| **Ik3'' (kA)** | Corrente de CC trifásico simétrico | kA |
| **Ip (kA)** | Corrente de pico (trifásico) | kA |
| **Ik2'' (kA)** | Corrente de CC bifásico | kA |
| **Ik1'' (kA)** | Corrente de CC monofásico fase-terra | kA |
| **Ik2E'' (kA)** | Corrente de CC bifásico com terra | kA |
| **κ** | Fator de pico (adimensional) | — |

### Relações esperadas

```
Ik3'' > Ik2'' ≥ Ik1''  (em sistemas solidamente aterrados)
Ip = κ × √2 × Ik3''
κ  tipicamente entre 1,02 e 2,0 (depende de R/X da rede)
```

### Correntes MT vs. BT

As correntes em kA em BT **podem ser numericamente maiores** que em MT, mesmo com menor potência de falta. Isso é fisicamente correto: em BT (400 V) a mesma potência de falta em MVA corresponde a correntes muito maiores em kA.

**Compare sempre pela potência de curto-circuito:**
```
Sk'' = √3 × Un × Ik''
```

---

## 7. Salvar e Abrir Projetos

### Salvar

**Arquivo → Salvar...** — salva a rede em formato **JSON** (`.json`).  
O arquivo contém todos os nós, ramos e parâmetros dos componentes.

### Abrir

**Arquivo → Abrir...** — abre um projeto `.json` salvo anteriormente.  
A rede é recarregada na árvore e no diagrama.

### Novo projeto

**Arquivo → Novo** — limpa a rede atual (não há confirmação — salve antes se necessário).

---

## 8. Exportar Relatórios

### Excel (`.xlsx`)

**Exportar → Excel...** ou botão **`Excel`** na barra.  
O arquivo gerado contém três abas:

| Aba | Conteúdo |
|-----|----------|
| **Resultados** | Correntes por barra e tipo de falta |
| **Impedâncias** | Z1 e Z0 de Thevenin (R, X, \|Z\|) em mΩ |
| **Rede** | Listagem de todos os componentes e parâmetros |

### PDF

**Exportar → PDF...** ou botão **`PDF`** na barra.  
Gera relatório paginado com:
- Cabeçalho: rede, data, norma, fator c
- Tabela de resultados
- Rodapé com referência à IEC 60909:2016

---

## 9. Conceitos de Cálculo (IEC 60909)

### Método da Corrente Equivalente de Curto-Circuito

A IEC 60909 substitui a tensão real pré-falta pela **tensão equivalente de curto-circuito** `c × Un / √3`, onde:
- `c` = fator de tensão (1,10 para MT/AT, máximo)
- `Un` = tensão nominal da barra de falta

### Impedâncias dos Componentes

**Transformador:**
```
ZT = (uk% / 100) × Un2² / Sn
RT = Pk × Un2² / Sn²
XT = √(ZT² − RT²)
KT = 0,95 × cmax / (1 + 0,6 × xT)   [fator de correção IEC]
```

**Cabo:**
```
Z1 = (R1 + j·X1) × L      [seq. positiva]
Z0 = (R0 + j·X0) × L      [seq. zero]
```

**Rede da concessionária:**
```
Z_rede = Un² / Sk''        [módulo]
R_rede = R/X × X_rede
```

### Fórmulas de Corrente

| Falta | Fórmula |
|-------|---------|
| **3F** | `Ik3'' = c·Un / (√3·\|Z1\|)` |
| **2F** | `Ik2'' = (√3/2)·Ik3''` |
| **1F-T** | `Ik1'' = √3·c·Un / \|2Z1 + Z0\|` |
| **2F-T** | IEC 60909 eq. 31 (componentes simétricas) |
| **Pico** | `Ip = κ·√2·Ik''` ;  `κ = 1,02 + 0,98·e^(−3R/X)` |

### Redes de Sequência Zero (Z0)

O percurso de Z0 depende do **grupo vetorial** do transformador:

| Grupo vetorial | Comportamento de Z0 |
|---------------|---------------------|
| **Dyn** (ex.: Dyn11) | Primário delta — bloqueia Z0 no lado MT. Z0 fica confinado ao circuito BT. |
| **YNyn** | Z0 percorre ambos os lados. |
| **Yyn** | Secundário estrela sem aterramento — Z0 bloqueado no secundário. |

---

## 10. Perguntas Frequentes

**P: Por que a Ik'' em BT é maior (em kA) do que em MT?**  
R: É fisicamente correto. Em tensões mais baixas, a mesma potência de falta corresponde a correntes maiores. Compare sempre usando Sk'' = √3 × Un × Ik'' (MVA).

**P: A barra MT do transformador aparece nos resultados?**  
R: Sim. Quando você adiciona um transformador, o **nó pai** (onde você clicou antes de adicionar) representa o lado MT. Esse nó aparece na tabela com sua tensão nominal de MT. O nó filho criado automaticamente (`Sec.`) representa o lado BT.  
Se quiser uma barra MT explicitamente nomeada para o trafo, adicione primeiro `+ Barra` na tensão de MT e conecte o trafo a ela.

**P: Posso analisar uma rede com dois transformadores em paralelo?**  
R: A versão atual suporta apenas redes **radiais**. Transformadores em paralelo (malha) requerem solução por matriz nodal — funcionalidade prevista para versões futuras.

**P: O que fazer quando Ik1'' aparece como infinito?**  
R: Significa que Z0 = 0 na barra de falta (ex.: barra infinita e transformador YNyn sem cabo). Verifique o grupo vetorial e o aterramento do trafo.

**P: Onde encontro R1, X1, R0, X0 dos cabos?**  
R: Nos catálogos dos fabricantes (Prysmian, Nexans, etc.) ou em tabelas da NBR 5410. Valores típicos para cabos XLPE BT 185 mm² Al:  
R1 = 0,206 Ω/km, X1 = 0,080 Ω/km, R0 ≈ 3×R1, X0 ≈ 3×X1.

---

*Software desenvolvido conforme IEC 60909:2016 — Short-circuit currents in three-phase a.c. systems.*
