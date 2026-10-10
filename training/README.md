# OutBRAKE — experimento 001

Pipeline real de coleta, treinamento e avaliação retrospectiva. Executar `python3 training/run.py` (Python, Node e dependências de `requirements.txt`). A coleta usa apenas APIs públicas, sem chave; mantém cache em `training/cache/`. Fontes, URLs completas, grade e hashes dos arquivos são registrados em `sources.json`. Os dados derivados usados no ajuste estão em `dataset.csv`.

## Desenho fixado antes do teste

- Grade: 16 pontos, latitudes 31/35/39/43°N × longitudes 100/95/90/85°W. Todos os horários 00/06/12/18 UTC, abril e maio.
- Treino: 2024. Teste: 2025, totalmente separado. Não foram escolhidos somente dias de surto.
- Alvo: ≥1 início de **registro NCEI de tornado** dentro de 150 km nas próximas 6 h. Registros NCEI podem representar segmentos por condado; não equivalem a tornados únicos. Não usamos sua contagem para ensinar o número de tornados. Ausência de registro é rótulo negativo, sujeito a subnotificação.
- Horários locais NCEI convertidos para UTC usando `CZ_TIMEZONE`; registros sem hora/coordenadas válidas são contabilizados e excluídos. `EVENT_ID` remove duplicatas.
- Modelo meteorológico: GFS Global no arquivo histórico contínuo do Open-Meteo. Este arquivo intercala rodadas e **não é um conjunto de previsões de antecedência fixa**. O ajuste é retrospectivo. Não interpretar métricas como desempenho de previsão de 24 h.
- Preditores: CAPE, CIN, temperatura/ponto de orvalho e ventos/alturas em níveis de pressão. `features.cjs` chama o mesmo `envFromData` do site para descarte de níveis subterrâneos, shear 0–6 km, SRH 0–1 km com Bunkers e LCL. Não há radar nem sondagens observadas adicionais.
- Regressão logística com padronização ajustada somente no treino, C=1, sem peso de classes. Preditores: log(1+CAPE), shear, SRH limitada a [-500,1500], LCL em km, Td, log(1+|CIN|), interações CAPE×shear e CAPE×SRH. Não houve busca de hiperparâmetros no teste.
- Comparações: frequência de eventos do treino e fórmula heurística anterior calibrada por regressão logística no mesmo treino. Limiar ilustrativo fixo de 10%, sem ajuste no teste.
- Incerteza: 500 reamostragens pareadas por dia do teste, mantendo seus pontos/horários juntos. Semente fixa. Dependência entre dias consecutivos pode permanecer; amostra pequena.

## Geometria

`fit_tracks.py` ajusta uma biblioteca empírica de formas de rastros DAT de 2024 (levantamentos preliminares). Aceita uma única polilinha, ≥3 vértices, comprimento de 2–150 km, razão comprimento/corda ≤1,3, deslocamento lateral ≤25% da corda e sem grandes retornos. Não infere curvatura de dois pontos. Usa 33 posições ao longo do comprimento normalizado.

O simulador sorteia uma forma reproduzível por célula, redimensiona-a pela distância associada à duração e ao movimento estimado e orienta-a pelo vetor Bunkers. O gancho e o tornado acompanham a direção tangente. Trata-se de **reamostragem de geometria**, ainda sem aprender sua dependência com CAPE, shear, modo convectivo ou relevo. O usuário pode desligá-la. Não há afirmação de que a trajetória de uma célula seja fisicamente equivalente a um rastro de tornado.

## Saídas e verificação

- `dist/training-model.json` (ou raiz no GitHub): coeficientes, normalização, métricas, calibração, fontes e limites.
- `dist/training-test.csv`: todos os exemplos reservados para teste.
- `dist/track-shapes.json`: biblioteca empírica de formas.
- Página `training.html`: comparação e consulta a qualquer exemplo de teste, inclusive falhas.
- `node training/check.cjs`: separação dos dias, inferência JavaScript versus Python e validade das formas.
- `node scripts/render-clip.cjs --video exemplo.mp4 --kml exemplo.kml`: verifica e renderiza o motor atualizado.

O classificador permanece na página de pesquisa: ainda não determina quantidades/intensidades no gerador. Não se converte uma probabilidade regional em probabilidade por célula. Novos dados requerem uma nova execução explícita do pipeline; não há treinamento contínuo automático no navegador.

## Próxima etapa

Incorporar arquivos de rodadas completas, com inicialização, disponibilidade e antecedência registradas; novos meses e anos; sondagens/radar; validação espacial; previsão de modo convectivo; só depois calibrar ocorrência, duração e intensidade condicional do gerador. As tentativas desta sessão no endpoint Previous Runs retornaram CAPE e temperatura de 24 h, mas recusaram os ventos em níveis de pressão com sufixo `previous_day1`; não substituímos esses dados por valores inventados.
