# lv-price-engine

**AI-assisted construction price matching based on GAEB tender positions and construction price data.**

`lv-price-engine` 是一个面向建筑工程 **Leistungsverzeichnis (LV)** 的辅助 Kalkulation 系统。  
目标是从 LV Position 中识别材料相关信息，并从价格数据库中检索和推荐最合适的 Commodity 与价格。

系统不会完全替代 Kalkulator，而是优先自动处理高置信度结果，并将不确定结果交给人工审核。

---

## 1. Input Data

### GAEB X83

当前系统支持读取 **GAEB X83** 文件，并解析：

- GAEB ID
- OZ
- Kurztext
- Longtext
- Menge
- Einheit

对应模块：

```text
src/ingestion/
└── gaeb_lv_loader.py
```

### Artikel XML

材料与价格数据来自结构化 Artikel XML，并导入 PostgreSQL。

当前主要数据结构：

```text
ProductGroup
    ↓
CommodityGroup
    ↓
Commodity
    ├── CommodityPrice
    └── EstimatePrice
```

数据库包含 5 个主要表：

```text
product_groups
commodity_groups
commodities
commodity_prices
estimate_prices
```

---

## 2. Matching Pipeline

当前匹配流程采用 **Dense Retrieval + Sparse Retrieval + Reranking**：

```text
LV Position
    ↓
TextBuilder
    ↓
Query Text
    │
    ├───────────────┐
    ↓               ↓
VectorRetriever   BM25Retriever
   BGE-M3            BM25
    ↓               ↓
   Top-K           Top-K
    └───────┬───────┘
            ↓
         RRF Fusion
            ↓
      Candidate Pool
            ↓
         Reranker
  bge-reranker-v2-m3
            ↓
       Final Ranking
            ↓
       Post Process
```

当前模型：

```text
Embedder:
BAAI/bge-m3

Sparse Retrieval:
BM25

Fusion:
Reciprocal Rank Fusion (RRF)

Reranker:
BAAI/bge-reranker-v2-m3
```

---

## 3. Match Status

每个 LV Position 最终会得到一个 `PositionMatchResult`：

```text
AUTO_MATCHED
REVIEW_REQUIRED
UNMATCHED
```

- **AUTO_MATCHED**：Rank 1 Candidate 足够明确，可以自动采用。
- **REVIEW_REQUIRED**：多个 Candidate 较为接近，需要人工确认。
- **UNMATCHED**：当前数据库中没有足够可靠的候选。

---

## 4. Text Processing

LV Position 和 Commodity Candidate 会先通过 `TextBuilder` 转换为统一的检索文本。

例如：

```text
LV (short text + long text + unit):
Unit: m3 | Ortbeton Streifenfundamente | Normalbeton C30/37 XC3 XF1 XA2 W0 ...

Candidate (category path + label + description + unit):
Unit: m³ | Stoffe | Beton | Lieferbeton, Ortbeton | Beton C30/37 XC3 XF1 XA2 W0
```

`TextBuilder` 只负责：

```text
Domain Object
→ Retrieval / Ranking Text
```

Retriever 和 Reranker 本身不负责业务文本生成。

---

## 5. Project Structure

```text
src/
├── config/
├── database/
├── db_article_importing/
├── ingestion/
├── text_processing/
│   └── text_builder.py
├── retrieval/
│   ├── base_retriever.py
│   ├── vector_retriever.py
│   └── bm25_retriever.py
├── fusion/
│   └── rrf_fusion.py
├── ranking/
│   ├── base_reranker.py
│   └── bge_reranker.py
├── matching/
│   └── match_pipeline.py
├── models/
├── exporter/
└── logging/
```

主要职责：

- `ingestion`：读取 GAEB X83
- `db_article_importing`：解析 Artikel XML 并导入数据库
- `database`：读取 Commodity 与价格数据
- `text_processing`：生成 Retrieval / Ranking Text
- `retrieval`：Vector / BM25 Candidate Retrieval
- `fusion`：融合多个 Retriever 的排序结果
- `ranking`：使用 Cross-Encoder Reranker 精排
- `matching`：编排整个 Matching Workflow
- `exporter`：输出 LV、Candidate 和 Match Results

---

## 6. Current Scope

当前系统主要解决：

```text
LV Position
→ Material / Commodity Matching
→ Material Price Recommendation
```

需要注意：

**Material Price ≠ 完整 Einheitspreis**

完整 LV Einheitspreis 可能还包含：

```text
Material
+ Lohn
+ Geräte
+ Transport
+ Sonstiges
```

因此当前系统主要提供材料价格匹配，而不是完整施工报价。

另外，LV Unit 与 Commodity Unit 也不一定相同，例如：

```text
LV:        m²
Commodity: m³
```

未来需要进一步加入：

```text
Unit Normalization
Unit Compatibility
Quantity Conversion
```

---

## 7. Model Configuration

模型通过 YAML 配置：

```yaml
embedder:
  name: bge-m3
  path: ./models/embedding/bge-m3
  device: cuda
  trust_remote_code: false

reranker:
  name: bge-reranker-v2-m3
  path: ./models/reranker/bge-reranker-v2-m3
  device: cuda
  trust_remote_code: false
```

模型在 `MatchPipeline` 创建之前完成加载，并通过 Dependency Injection 传入。

---

## 8. Future Development

后续计划包括：

- Reranker 与 Threshold Evaluation
- Unit Compatibility / Quantity Conversion
- Material Attribute Extraction
- Vector Database / pgvector
- 更多价格数据与历史项目数据
- Material Cost Calculation
- 完整 Einheitspreis / Gesamtpreis Calculation
- GAEB / Excel Export
- iTWO Integration

---

## 9. Goal

长期目标是建立一个 **AI-assisted Kalkulation System**：

> Automatische Verarbeitung klarer Positionen – manuelle Prüfung nur dort, wo fachliche Entscheidung wirklich notwendig ist.
