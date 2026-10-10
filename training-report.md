# OutBRAKE — resultado do primeiro treinamento

Treino efetivamente executado: 3904 exemplos, abril–maio de 2024, 87 positivos. Teste reservado: 3904 exemplos, abril–maio de 2025, 73 positivos. São pares ponto/horário, não tornados únicos.

Alvo: registro de tornado num raio de 150 km nas próximas 6 horas. GFS histórico contínuo; avaliação retrospectiva sem antecedência fixa.

| Método | Brier (menor melhor) | AP (maior melhor) | ROC AUC |
|---|---:|---:|---:|
| Modelo treinado | 0.01629 | 0.235 | 0.902 |
| Fórmula anterior ajustada | 0.01652 | 0.239 | 0.891 |
| Frequência do treino | 0.01836 | 0.019 | 0.500 |

A redução do Brier versus a fórmula anterior foi de 1.4%. O intervalo de 95% do ganho absoluto, reamostrando dias, foi [-0.0007574476372785879, 0.0012596303366184604]; inclui zero. AP ficou ligeiramente abaixo da fórmula anterior. Resultado misto, sem evidência robusta de superioridade.

No limiar fixo de 10%: 30 acertos, 143 falsos alarmes e 43 eventos perdidos.

Não houve ajuste de hiperparâmetros ou limiar no conjunto de teste. O modelo permanece no laboratório do site. O histórico contínuo não permite anunciar desempenho com 24 h de antecedência.

A biblioteca geométrica usa 922 formas válidas entre 1.692 registros de polilinhas DAT de 2024. As formas são redimensionadas e orientadas pelo vetor de movimento. A relação entre ambiente e curvatura ainda não foi treinada.

Dados completos, fontes e método estão em `training/README.md`, `training/sources.json`, `training/dataset.csv` e `training-model.json` no repositório.

Fontes: [GFS/Open-Meteo](https://open-meteo.com/en/docs/historical-forecast-api), [NOAA NCEI](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/), [NWS DAT](https://services.dat.noaa.gov/arcgis/rest/services/nws_damageassessmenttoolkit/DamageViewer/MapServer).
