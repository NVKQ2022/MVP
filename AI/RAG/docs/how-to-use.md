# Hướng dẫn chạy dự án RAG (RFC Search)

> Stack: `all-MiniLM-L6-v2` (384d, local) + `Chroma` + `FastAPI` + `Azure OpenAI` cho LLM.  
> Sau khi `git pull` bạn **phải build lại** `data/chunks` và `chroma_db` vì chúng đã bị `.gitignore` (không commit).

---

## 1. Yêu cầu

* Python 3.12 (tested `3.12.3`)
* Git
* RAM ≥ 4GB (embedding 6766 chunks tốn ~1GB RAM)
* Azure OpenAI `ENDPOINT` + `API_KEY` **chỉ cần nếu dùng `/rag`** (hỏi LLM). `/query` chạy local hoàn toàn.

---

## 2. Clone & tạo môi trường

```bash
git clone <your-repo-url> RAG
cd RAG

python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

# Nếu gặp lỗi torch CUDA lớn / chậm, cài bản CPU nhẹ hơn (khuyến nghị):
# pip install torch --index-url https://download.pytorch.org/whl/cpu
```

> `requirements.txt` chỉ pin **direct deps** (`chromadb`, `sentence-transformers`, `fastapi`, `uvicorn`, `openai`, `python-dotenv`) với `>=` + `<next major`, transitive để pip tự resolve → dễ bảo trì.

---

## 3. Cấu hình `.env`

```bash
cp .env.example .env
nano .env
```

`.env.example`:
```ini
ENDPOINT="https://your-resource.services.ai.azure.com/openai/v1"
PROVIDER="openai"
API_KEY="your-api-key-here"
LLM_MODEL="gpt-5.6-luna"
EMBEDDING_MODEL="all-MiniLM-L6-v2"
CHROMA_PERSIST_DIR="chroma_db"
CHROMA_COLLECTION="rfc_docs"
```

* **Bắt buộc cho RAG:** `ENDPOINT`, `API_KEY`, `LLM_MODEL` (lấy ở Azure AI Foundry → Project → OpenAI v1 endpoint).
* **Không cần cho search thuần:** `EMBEDDING_MODEL` mặc định `all-MiniLM-L6-v2` local, không gọi API.
* `CHROMA_PERSIST_DIR`/`CHROMA_COLLECTION` giữ mặc định nếu không custom.

> `.env` đã bị `.gitignore`, không bao giờ commit key thật.

---

## 4. Chuẩn bị dữ liệu

`data/docs/` đã có 8 RFC mẫu (`rfc1035.txt` … `rfc9110.txt`). Bạn có thể thêm file `.txt` riêng vào đó.

`data/chunks/` và `chroma_db/` **không có sau pull** (đã ignore) → phải build ở bước 5.

---

## 5. Build

### 5.1 Chunks ( deterministic, 300/30 )

```bash
python scripts/build_chunks.py
# hoặc custom:
python scripts/build_chunks.py --chunk-size 500 --overlap 50 --per-file
```

* Output duy nhất: `data/chunks/chunks.json` (6766 chunks mặc định, 2.5M).
* Kiểm tra: `ls -lh data/chunks/chunks.json`

> Lưu ý: không còn `data/chunks.json` lẻ như bản cũ – chỉ dùng `data/chunks/chunks.json`.

### 5.2 Embeddings → Chroma (cần tải model lần đầu ~80MB)

```bash
python scripts/build_embeddings.py --clear
# --clear: xóa collection cũ rồi thêm mới (tránh duplicate)
# --limit 100 : test nhanh 100 chunks
# --batch-size 128 : chỉnh nếu RAM thấp
```

* Lần đầu sẽ `Loading weights 103/103` + download `all-MiniLM-L6-v2` từ HuggingFace (~80MB, ~20-30s, cache ở `~/.cache/huggingface/`).
* Sau đó `embedded 6766 vectors` + `count after: 6766`. DB lưu ở `chroma_db/chroma.sqlite3` (22M).

**Nếu muốn dọn sạch để rebuild từ đầu:**

```bash
python scripts/clean_chroma.py --dry-run          # xem sẽ xóa gì
python scripts/clean_chroma.py --yes              # xóa collection rfc_docs
python scripts/clean_chroma.py --all --chunks --yes  # xóa cả chroma_db + data/chunks/*.json
```

---

## 6. Kiểm tra nhanh (không cần server)

```bash
# Search thuần (local, ~25ms sau khi model warm):
python scripts/query.py --query "QUIC handshake" --top-k 3
python scripts/query.py --query "What is DNS?" --top-k 5

# RAG + LLM (cần .env đúng, ~11s do gọi Azure):
python scripts/rag_query.py --query "What is DNS according to RFC 1035?" --top-k 3
```

* `query.py` trả `score` (cosine), `source#chunk_id`, `text`.
* `rag_query.py` sẽ retrieve 3 chunks rồi gọi `gpt-5.6-luna` để trả lời.

---

## 7. Chạy Server + Frontend (khuyên dùng – không còn chậm 26s mỗi lần)

Mỗi lần `python scripts/query.py` phải load lại model 26s. Server load **1 lần** rồi giữ warm.

```bash
python scripts/server.py --port 8000
# hoặc: uvicorn scripts.server:app --host 0.0.0.0 --port 8000
```

Đợi log:
```
[server] embedding all-MiniLM-L6-v2 dim=384 loaded in 21.3s
[server] chroma rfc_docs@... count=6766
[server] LLM gpt-5.6-luna @ https://...
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

Mở:
* **Frontend:** http://localhost:8000/ (giao diện dark, ô hỏi, top_k, nút Tìm kiếm / Hỏi RAG)
* **API docs:** http://localhost:8000/docs
* **Health:** http://localhost:8000/health

Test bằng curl:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"QUIC handshake","top_k":3}'
curl -X POST http://localhost:8000/rag -H "Content-Type: application/json" -d '{"query":"What is DNS?","top_k":3}'
```

---

## 8. Quy trình đầy đủ sau pull (tóm tắt)

```bash
git pull
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # rồi điền key
python scripts/build_chunks.py
python scripts/build_embeddings.py --clear
python scripts/server.py --port 8000
# mở http://localhost:8000/
```

---

## 9. Troubleshooting

| Lỗi | Nguyên nhân | Sửa |
|-----|-------------|-----|
| `chunks not found: data/chunks/chunks.json` | Chưa chạy `build_chunks` | `python scripts/build_chunks.py` |
| `DeploymentNotFound` khi dùng OpenAI embedding cũ | Bản mới đã bỏ Azure embedding, dùng local `all-MiniLM` – bỏ `EMBEDDING_MODEL=text-embedding-3-small` | Để `EMBEDDING_MODEL=all-MiniLM-L6-v2` |
| `Read timed out` khi `pip install torch` | Torch 500MB, mạng chậm | `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| `Loading weights 0/103` chậm 26s mỗi lần `query.py` | Load model mỗi lần | Dùng `server.py` để load 1 lần |
| `chroma count mismatch` / duplicate | Chạy `build_embeddings` 2 lần không `--clear` → `add_documents` tạo uuid mới → duplicate | `python scripts/clean_chroma.py --yes` rồi `build_embeddings --clear` |
| Fronted `✗ offline` | Server chưa chạy hoặc port khác | `curl http://localhost:8000/health` để check |

---

## 10. Dọn dẹp

```bash
# Xóa cache Python
find . -type d -name "__pycache__" ! -path "./venv/*" -exec rm -rf {} +
# Xóa DB / chunks để test lại từ đầu
python scripts/clean_chroma.py --all --chunks --yes
```

---

## 11. Cấu trúc sau khi build

```
RAG/
├── data/
│   ├── docs/*.txt              # committed
│   └── chunks/chunks.json      # generated (2.5M, ignored)
├── chroma_db/                  # generated (33M, ignored)
│   └── chroma.sqlite3
├── static/index.html           # frontend
├── scripts/
│   ├── build_chunks.py         # docs → chunks
│   ├── build_embeddings.py     # chunks → chroma
│   ├── clean_chroma.py         # dọn DB
│   ├── query.py / rag_query.py # CLI test
│   └── server.py               # FastAPI warm server
├── requirements.txt            # direct deps only
├── .env.example                # mẫu commit
└── docs/how-to-use.md          # file này
```
