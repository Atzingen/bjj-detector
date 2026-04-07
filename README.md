# BJJ Position Detector

Detecção de posições de jiu-jitsu em imagens usando YOLO11.

## Classes

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
python data/download.py
python scripts/convert_dataset.py
```

## Treino

```bash
python train.py
```

## Interface

```bash
python app.py
```

Acesse http://localhost:7860

## Deploy (Docker)

```bash
docker compose up --build -d
```

## Dataset

[ViCoS Lab - Brazilian Jiu-Jitsu Positions Dataset](https://vicos.si/resources/jiujitsu/)
Licenca: CC BY-NC-SA 4.0
