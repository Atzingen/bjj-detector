# BJJ Position Detector

Deteccao de posicoes de jiu-jitsu em imagens e videos usando YOLO11.

## Posicoes Detectaveis

| ID | Posicao | Descricao |
|----|---------|-----------|
| 0 | standing | Em pe |
| 1 | takedown | Queda |
| 2 | open_guard | Guarda aberta |
| 3 | half_guard | Meia guarda |
| 4 | closed_guard | Guarda fechada |
| 5 | fifty_fifty | 50-50 |
| 6 | side_control | Cem quilos |
| 7 | mount | Montada |
| 8 | back | Pegada nas costas |
| 9 | turtle | Tartaruga |

## Setup

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

## Dataset

```bash
python data/download.py              # baixa ~10GB do ViCoS Lab
python scripts/convert_dataset.py    # converte para formato YOLO
```

## Treino

```bash
# Local (requer GPU)
python train.py --epochs 50 --batch 16

# Via Docker (recomendado — evita problemas de compatibilidade)
docker compose -f docker-compose.train.yml up
```

Os pesos ficam em `runs/detect/bjj-detector/weights/best.pt`.
Copie para a raiz do projeto: `cp runs/detect/bjj-detector/weights/best.pt best.pt`

## Interfaces

### Flask (principal)

```bash
python webapp.py
```

Acesse http://localhost:5000 — login: `demo` / `demo1234`

Funcionalidades:
- Upload de imagem (drag-and-drop)
- Captura pela camera do celular
- Processamento de video frame a frame

### Gradio (simples)

```bash
python app.py
```

Acesse http://localhost:7860

## Deploy (Docker)

```bash
docker compose up --build -d
```

## Estrutura

```
bjj-detector/
├── data/
│   └── download.py              # baixa dataset ViCoS
├── scripts/
│   └── convert_dataset.py       # COCO keypoints -> YOLO bboxes
├── templates/                   # templates Flask
├── static/                      # CSS e JS
├── tests/
├── train.py                     # wrapper de treino YOLO11
├── app.py                       # interface Gradio
├── webapp.py                    # interface Flask (principal)
├── docker-compose.yml           # deploy producao (Gradio)
├── docker-compose.train.yml     # treino via Docker com GPU
├── Dockerfile
└── best.pt                      # modelo treinado
```

## Dataset

[ViCoS Lab - Brazilian Jiu-Jitsu Positions Dataset](https://vicos.si/resources/jiujitsu/)
Licenca: CC BY-NC-SA 4.0
