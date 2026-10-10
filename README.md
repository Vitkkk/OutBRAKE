# OutBRAKE · v0.1

Uma animação de um surto fictício de tempestades e tornados condicionada por um ambiente meteorológico real. Projeto de Vitkkk.

**Abrir a versão interativa:** https://outbrake-vito-v1.vitoskkkkk.chatgpt.site (acesso privado do criador).

## Primeira versão

- Consulta inicial real do GFS, obtida em **10/10/2026 às 14:47 UTC**, para **Santa Catarina, 27°S / 51°W**, com validade **10/10/2026 às 17:00 UTC**.
- CAPE do modelo: 1.550 J/kg; shear 0–6 km: 18,4 m/s; SRH ciclônica 0–1 km: 94 m²/s²; LCL aproximado: 300 m AGL.
- A semente inicial 1041026 produz 6 células e 4 tornados **fictícios**, com pico fictício de 217 km/h.
- Animação regional de quatro horas, controles de reprodução, novos cenários reproduzíveis, mapa de comparação global, perfil termodinâmico e hodógrafa.
- Consulta de novas previsões GFS e ECMWF por Open-Meteo, com mensagens de falha e preservação explícita do ambiente anterior.
- Gravação do canvas em vídeo de 30 segundos (WebM ou MP4, conforme o navegador), mantendo uma identificação de simulação no próprio vídeo.
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

O ambiente fica fixo nas quatro horas fictícias de evolução. O número de células, iniciação, duração, tornadogênese, ventos e largura dos tornados vêm de **regras heurísticas de entretenimento**, com semente reproduzível. Não se integram equações atmosféricas. Os ecos são ilustrações sintéticas, sem escala física de dBZ. Nenhuma categoria EF é atribuída a partir de CAPE ou aparência. Não há simulação de danos estruturais.

Nesta versão ainda não há radiossondagens observadas, campo de relevo/DEM, frentes ou convergência. Os contornos Natural Earth são geográficos e simplificados; não são orografia. Horário de validade e de obtenção não equivalem à inicialização de uma rodada. A fotografia inicial fica identificada como antiga depois de 12 horas.

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
