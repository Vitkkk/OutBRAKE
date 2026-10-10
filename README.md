# OutBRAKE · v0.4

Uma animação de um surto fictício de tempestades e tornados condicionada por um ambiente meteorológico real. Projeto de Vitkkk.

**Abrir a versão interativa:** https://outbrake-vito-v1.vitoskkkkk.chatgpt.site (acesso privado do criador).

## Versão atual

- Ambiente principal: **Geórgia / Macon**, 32,84°N / 83,63°W, GFS válido em **10/10/2026 às 19:00 UTC (15h EDT)**. CAPE: 2.070 J/kg; shear 0–6 km: 22,8 m/s; SRH 0–1 km: 62 m²/s². A semente inicial produz 7 células e 4 tornados fictícios, pico 208 km/h.
- Segundo cenário incluído: **Alabama / Dothan**, 31,22°N / 85,39°W, GFS válido em **10/10/2026 às 06:00 UTC (1h CDT)**. CAPE: 520 J/kg; shear: 32,2 m/s; SRH: 263 m²/s². Produz 4 células e 3 tornados fictícios, pico 228 km/h.
- Animação regional de quatro horas, controles de reprodução, novos cenários reproduzíveis, mapa de comparação global, perfil termodinâmico e hodógrafa.
- Consulta de novas previsões GFS e ECMWF por Open-Meteo, com mensagens de falha e preservação explícita do ambiente anterior.
- Gravação do canvas em vídeo de 36 segundos (30 de evolução + 6 de resumo) (WebM ou MP4, conforme o navegador), mantendo uma identificação de simulação no próprio vídeo.
- Câmera de campo ilustrativa, vinculada ao tornado ativo. Mapa e interface adaptados ao celular.

## Rodar localmente

Não há dependências de frontend nem etapa de build. Sirva a pasta do projeto por HTTP:

```bash
python3 -m http.server 8000
```

Abra `http://localhost:8000`. Abrir diretamente por `file://` pode impedir o carregamento dos arquivos JSON. As atualizações de previsão precisam de conexão com `api.open-meteo.com`. O cenário inicial usa dados incluídos no projeto e permanece disponível sem consultas externas.

## Método e limites

A comparação é uma amostra de **36 pontos**, escolhidos em regiões convectivas, nas próximas 24 horas. O índice experimental combina CAPE, diferença vetorial entre ventos de 10 m e 500 hPa, ponto de orvalho e CIN quando disponível. Não representa uma probabilidade calibrada, não cobre todos os pontos do planeta e não avalia a iniciação convectiva. Ausência de CIN recebe uma penalização explícita no índice, sem imputar CIN observada.

O perfil vertical utiliza temperatura, umidade, altura geopotencial e ventos em níveis de pressão do modelo. Os níveis abaixo do solo são descartados. As alturas são convertidas para AGL usando a elevação retornada pela API. O vento é interpolado por altura; o vento de 10 m representa a origem do perfil. O movimento usa a aproximação de Bunkers: vento médio 0–6 km, diferença entre as médias 0–0,5 e 5,5–6 km, desvio de 7,5 m/s e seleção do ramo ciclônico conforme o hemisfério. SRH é integrada em passos de 100 m e apresentada com sinal ciclônico local. LCL é aproximado por 125 × (T − Td). CAPE é o campo fornecido pelo serviço, sem renomeá-lo como MLCAPE.

O ambiente fica fixo nas quatro horas fictícias de evolução. O número de células, iniciação, duração, tornadogênese, ventos e largura dos tornados vêm de **regras heurísticas de entretenimento**, com semente reproduzível. Não se integram equações atmosféricas. Os ecos são campos sintéticos rasterizados: núcleo e escudo de precipitação, entalhe de entrada, apêndice contínuo e textura espacial reproduzível. A paleta de dBZ é ilustrativa, sem cálculo físico de refletividade. A classe EF exibida é simulada, calculada pela faixa do pico fictício convertido em mph e arredondado (limites superiores 85, 110, 135, 165 e 200 mph). A cauda de ventos abaixo de 65 mph fica no grupo EF0 do simulador. As cores das trilhas e todos os rótulos usam a mesma classificação. Não há simulação de danos estruturais.

Nesta versão ainda não há radiossondagens observadas, campo de relevo/DEM que influencie o motor, frentes ou convergência. Os contornos Natural Earth são geográficos e simplificados; não são orografia. Horário de validade e de obtenção não equivalem à inicialização de uma rodada. A fotografia inicial fica identificada como antiga depois de 12 horas.

## Arquivos

- `index.html`, `style.css`, `app.js`: experiência no navegador.
- `bootstrap.json`: consulta real inicial, perfil previsto e comparação dos pontos.
- `world.json`: contornos Natural Earth simplificados.
- `scripts/refresh-snapshot.py`: renova a fotografia GFS e sua seleção regional.
- `scripts/render-clip.cjs`: renderiza o motor diretamente com `@napi-rs/canvas`; verifica reprodutibilidade, consistência de trajetórias e escolha de hemisfério. Gera MP4 com FFmpeg, sem navegador.

Para renderizar fora do ambiente original, instale `@napi-rs/canvas`, disponibilize `ffmpeg` e informe `OUTBRAKE_CANVAS_MODULE` como o nome do módulo ou seu caminho absoluto:

```bash
OUTBRAKE_CANVAS_MODULE=@napi-rs/canvas node scripts/render-clip.cjs --video OutBRAKE.mp4
```

## Fontes

- [GFS / Open-Meteo](https://open-meteo.com/en/docs/gfs-api)
- [ECMWF / Open-Meteo](https://open-meteo.com/en/docs/ecmwf-api)
- [Natural Earth](https://www.naturalearthdata.com/): dados geográficos de domínio público.
- Dados meteorológicos distribuídos pelo Open-Meteo sob as condições e atribuições do serviço. Uso desta integração gratuita sujeito aos limites de uso do serviço.

O botão de gravação requer um navegador com Canvas captureStream e MediaRecorder. O acesso às APIs externas pode falhar por rede, CORS ou limites do serviço; a interface informa a falha e conserva a consulta anterior.

## Mudanças na v0.2

- Ecos em pixels com formas irregulares e ganchos contínuos, substituindo círculos visíveis.
- Tornado posicionado no extremo do gancho; trilhas e câmera mantêm a mesma identificação.
- Legenda EF0–EF5 das trilhas; identificação e classe ao lado de cada tornado.
- Cena final de seis segundos com todos os rótulos e picos; tabela do resumo no site.
- A semente inicial continua com 6 células e 4 tornados: T01 EF1 (148 km/h), T02 EF2 (202 km/h), T03 EF1 (153 km/h), T04 EF2 (217 km/h).
- Faixas de referência: https://www.weather.gov/oun/efscale

## Mudanças na v0.3

- Fundo de satélite da superfície usando Esri World Imagery, alinhado por um retângulo geográfico EPSG:4326 retornado pelo serviço.
- Satélite ligado por padrão no mapa regional; contornos permanecem como alternativa.
- Cópia incluída de um mosaico do sudeste dos EUA. O mosaico usa imagens com datas de aquisição variáveis; não é satélite meteorológico ao vivo.
- Créditos visíveis no mapa e no vídeo: Esri, Vantor, Earthstar Geographics e GIS User Community.
- O site consulta um novo mosaico para outras regiões, quando necessário; falhas de rede mantêm a alternativa geográfica.
- Dois ambientes reais de 10/10/2026 selecionáveis, com seus horários explícitos: tarde na Geórgia e madrugada no Alabama. A imagem de superfície não altera a física do motor.
- Fonte das imagens: https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer

## Mudanças na v0.4

- Botão **Baixar KML** exporta todas as trajetórias geradas, independente do instante do player; **Gravar clipe** também baixa o KML do mesmo cenário. Se o navegador bloquear downloads múltiplos, o botão KML permite baixá-lo separadamente.
- Uma pasta por classe no Google Earth: EF0 azul claro (`#91cfff`), EF1 azul escuro (`#2459c4`), EF2 amarelo (`#ffd400`), EF3 laranja (`#ff8c24`), EF4 vermelho (`#f02c38`), EF5 rosa (`#ff71be`). Vídeo, mapa, resumo e KML compartilham a paleta.
- Cada tornado aparece com ID e classe no fim da linha. Seus dados incluem pico fictício, início/fim simulados em UTC, duração, comprimento aproximado, parâmetro de largura, célula e semente. Horários simulados = validade do ambiente + minutos do cenário.
- As coordenadas são a inversa do plano geográfico do mapa (111 km por grau de latitude; longitude corrigida pelo cosseno da latitude do ambiente); caminhos amostrados por minuto com início/fim exatos e presos à superfície. São as mesmas trajetórias do vídeo, sem precisão geodésica nem corredor de danos.
- Referência do formato: https://developers.google.com/kml/documentation/kmlreference

Para renderizar um clipe e o KML do mesmo cenário:

```bash
OUTBRAKE_CANVAS_MODULE=@napi-rs/canvas node scripts/render-clip.cjs --snapshot bootstrap-alabama.json --video Alabama.mp4 --kml Alabama.kml
```

O argumento `--kml` também funciona sem `--video`.
