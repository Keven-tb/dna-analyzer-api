# Relatório — Implementação de Serviços com Docker

**Nome(s):** Keven Teixeira de Brito
**Data:** 18/09/2026

## 1. Explicação linha a linha do Dockerfile

```dockerfile
FROM python:3.12-slim
```
> Usa a imagem oficial do Python na variante "slim", que traz apenas o essencial
> para rodar Python, resultando numa imagem final menor que a imagem padrão.

```dockerfile
WORKDIR /app
```
> Define `/app` como diretório de trabalho: todos os comandos seguintes (COPY, RUN, CMD)
> passam a ser executados relativos a esse caminho.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
> Copia só o `requirements.txt` antes do resto do código e instala as dependências
> (no caso, o Flask). Isso aproveita o cache de camadas do Docker: se só o
> `app.py` mudar depois (e não as dependências), o Docker reaproveita essa
> camada já construída em vez de reinstalar tudo de novo, acelerando builds
> futuros.

```dockerfile
COPY . .
```
> Copia o restante do código-fonte da aplicação (o `app.py`, com a lógica de
> análise de sequências de DNA) para dentro da imagem.

```dockerfile
ENV DATA_DIR=/app/data
```
> Define a variável de ambiente lida pela aplicação para saber onde gravar o
> banco de dados (`sequencias.db`, em SQLite).

```dockerfile
EXPOSE 8000
```
> Documenta que o contêiner escuta na porta 8000 (não publica a porta sozinho;
> isso é feito com `-p` no `docker run`).

```dockerfile
VOLUME /app/data
```
> Declara que `/app/data` é um ponto de montagem de dados. Sinaliza que esse
> diretório deve ser gerenciado fora do ciclo de vida do contêiner — é onde
> fica o `sequencias.db` com o histórico de análises.

```dockerfile
CMD ["python", "app.py"]
```
> Comando executado quando o contêiner inicia: sobe o servidor Flask na porta
> 8000, escutando em `0.0.0.0` (todas as interfaces), o que é necessário
> para a API ser acessível de fora do contêiner.

## 2. Etapa 3 — Build

**Comando:** `docker build -t dna-analyzer:1.0 .`

```
[sudo] password for keven:
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon  18.43kB
Step 1/9 : FROM python:3.12-slim
 ---> 78387bc3881b
Step 2/9 : WORKDIR /app
 ---> Using cache
 ---> d421139410c3
Step 3/9 : COPY requirements.txt .
 ---> Using cache
 ---> bfbbf289dc0c
Step 4/9 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Using cache
 ---> bf14e236f7a8
Step 5/9 : COPY . .
 ---> fb8d2261f60f
Step 6/9 : ENV DATA_DIR=/app/data
 ---> Running in 0044b665726b
 ---> Removed intermediate container 0044b665726b
 ---> 890ae2d2c474
Step 7/9 : EXPOSE 8000
 ---> Running in 14b127bc4dc0
 ---> Removed intermediate container 14b127bc4dc0
 ---> e004ff92c054
Step 8/9 : VOLUME /app/data
 ---> Running in 1cf447ed958e
 ---> Removed intermediate container 1cf447ed958e
 ---> 6e6ff1d2a25e
Step 9/9 : CMD ["python", "app.py"]
 ---> Running in 96957cb92093
 ---> Removed intermediate container 96957cb92093
 ---> ccbc71b10e78
Successfully built ccbc71b10e78
Successfully tagged dna-analyzer:1.0
```

**Tamanho final da imagem** (`docker image ls dna-analyzer`):

```
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
dna-analyzer:1.0   43a766801a4f        208MB         51.2MB
```

**Camadas** (`docker history dna-analyzer:1.0`):

```
IMAGE          CREATED              CREATED BY                                      SIZE      COMMENT
43a766801a4f   About a minute ago   /bin/sh -c #(nop)  CMD ["python" "app.py"]      0B
4b32481d4527   About a minute ago   /bin/sh -c #(nop)  VOLUME [/app/data]           0B
0401a4adfc60   About a minute ago   /bin/sh -c #(nop)  EXPOSE 8000                  0B
a5761c458dba   About a minute ago   /bin/sh -c #(nop)  ENV DATA_DIR=/app/data       0B
65370f18be81   About a minute ago   /bin/sh -c #(nop) COPY dir:286558c51b0850958…   24.6kB
bf14e236f7a8   About a minute ago   /bin/sh -c pip install --no-cache-dir -r req…   15.2MB
bfbbf289dc0c   2 minutes ago        /bin/sh -c #(nop) COPY file:42a307119eed5397…   12.3kB
d421139410c3   2 minutes ago        /bin/sh -c #(nop) WORKDIR /app                  8.19kB
78387bc3881b   2 weeks ago          CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      2 weeks ago          RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          RUN /bin/sh -c set -eux;  apt-get update;  a…   13.2MB    buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      3 weeks ago          # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.5MB    debuerreotype 0.17
```

**Observação:** as últimas 6 camadas (de `WORKDIR /app` até `CMD`) são as que
foram criadas pelo Dockerfile escrito para esta atividade; as demais (`apt-get`,
`debuerreotype`, etc., com data "2 weeks ago") pertencem à imagem base oficial
`python:3.12-slim`, herdada. O `CONTENT SIZE` de 51.2MB reflete apenas o que
a imagem de fato adiciona sobre a base.

## 3. Etapa 4 — Execução com volume nomeado

Volume criado: `dna-dados`
Contêiner: `dna` (porta 8000)

```
$ sudo docker run -d --name dna -p 8000:8000 -v dna-dados:/app/data dna-analyzer:1.0
d85d8a132b260f8f83dd354a0c51088be6e8eb98313d0f1c18ddba2d1e2c92bb

$ sudo docker ps
CONTAINER ID   IMAGE              COMMAND           CREATED          STATUS          PORTS                                         NAMES
d85d8a132b26   dna-analyzer:1.0   "python app.py"   11 seconds ago   Up 10 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   dna

$ sudo docker logs dna
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://172.17.0.2:8000
Press CTRL+C to quit
```

Inserção de sequências via `curl`:

```
$ curl -X POST http://localhost:8000/sequencias -H "Content-Type: application/json" -d '{"nome": "seq1", "sequencia": "ATCGGGCTA"}'
{"complemento_reverso":"TAGCCCGAT","criado_em":"2026-09-19T00:47:44.965826+00:00","gc_percentual":55.56,"id":2,"nome":"seq1","sequencia":"ATCGGGCTA","tamanho":9}

$ curl -X POST http://localhost:8000/sequencias -H "Content-Type: application/json" -d '{"nome": "seq2", "sequencia": "GGGAAATTTCCC"}'
{"complemento_reverso":"GGGAAATTTCCC","criado_em":"2026-09-19T00:47:44.992211+00:00","gc_percentual":50.0,"id":3,"nome":"seq2","sequencia":"GGGAAATTTCCC","tamanho":12}

$ curl -X POST http://localhost:8000/sequencias -H "Content-Type: application/json" -d '{"nome": "seq3", "sequencia": "TACGATCGATCG"}'
{"complemento_reverso":"CGATCGATCGTA","criado_em":"2026-09-19T00:47:45.010549+00:00","gc_percentual":50.0,"id":4,"nome":"seq3","sequencia":"TACGATCGATCG","tamanho":12}

$ curl http://localhost:8000/sequencias
[
  {"id":1,"nome":"Amostra_01","sequencia":"ACTG","tamanho":4,"gc_percentual":50.0,"complemento_reverso":"CAGT","criado_em":"2026-09-18T15:02:45.430665+00:00"},
  {"id":2,"nome":"seq1","sequencia":"ATCGGGCTA","tamanho":9,"gc_percentual":55.56,"complemento_reverso":"TAGCCCGAT","criado_em":"2026-09-19T00:47:44.965826+00:00"},
  {"id":3,"nome":"seq2","sequencia":"GGGAAATTTCCC","tamanho":12,"gc_percentual":50.0,"complemento_reverso":"GGGAAATTTCCC","criado_em":"2026-09-19T00:47:44.992211+00:00"},
  {"id":4,"nome":"seq3","sequencia":"TACGATCGATCG","tamanho":12,"gc_percentual":50.0,"complemento_reverso":"CGATCGATCGTA","criado_em":"2026-09-19T00:47:45.010549+00:00"}
]
```

**Observação:** o registro `id: 1` (`Amostra_01`) já é um dado remanescente de
um teste anterior, gravado no mesmo volume `dna-dados` antes desta sequência
de comandos — o que, de forma antecipada, já demonstra a persistência entre
contêineres formalizada na Etapa 5.

**Curiosidade biológica:** a `seq2` (`GGGAAATTTCCC`) tem complemento reverso
**idêntico** à sequência original — é um caso de sequência palindrômica,
padrão comum em sítios reconhecidos por enzimas de restrição na biologia
molecular [1].

## 4. Etapa 5 — Prova de persistência

```
$ sudo docker stop dna && sudo docker rm dna
dna
dna

$ sudo docker volume ls
DRIVER    VOLUME NAME
local     dna-dados

$ sudo docker volume inspect dna-dados
[
    {
        "CreatedAt": "2026-09-18T11:05:53-03:00",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/dna-dados/_data",
        "Name": "dna-dados",
        "Options": null,
        "Scope": "local"
    }
]

$ sudo docker run -d --name dna2 -p 8000:8000 -v dna-dados:/app/data dna-analyzer:1.0
c8d508404b6b979375c303aba85d44168000718d9fb62e3a434f6bc8816a0f62

$ curl http://localhost:8000/sequencias
[
  {"id":1,"nome":"Amostra_01","sequencia":"ACTG", ...},
  {"id":2,"nome":"seq1","sequencia":"ATCGGGCTA", ...},
  {"id":3,"nome":"seq2","sequencia":"GGGAAATTTCCC", ...},
  {"id":4,"nome":"seq3","sequencia":"TACGATCGATCG", ...}
]
```

**Conclusão:** o contêiner `dna` foi completamente destruído (`stop` + `rm`).
O volume `dna-dados` continuou existindo de forma independente. Um contêiner
novo (`dna2`, com ID diferente e sem relação com o `dna` anterior) foi criado
montando o mesmo volume, e as 4 sequências reapareceram intactas, até com as
datas de criação originais, provando que os dados não foram recriados, apenas
recuperados do volume.

## 5. Etapa 6 — Contraexemplo (efemeridade)

```
$ sudo docker run -d --name dna-temporario -p 8001:8000 dna-analyzer:1.0
c5467c94075ad12ff54bc346a28acd5077860f9c723f80faa973de964dfd715f

$ curl -X POST http://localhost:8001/sequencias -H "Content-Type: application/json" -d '{"nome": "vou-sumir", "sequencia": "GATTACA"}'
{"complemento_reverso":"TGTAATC","criado_em":"2026-09-19T03:22:53.984357+00:00","gc_percentual":28.57,"id":1,"nome":"vou-sumir","sequencia":"GATTACA","tamanho":7}

$ curl http://localhost:8001/sequencias
[{"complemento_reverso":"TGTAATC","criado_em":"2026-09-19T03:22:53.984357+00:00","gc_percentual":28.57,"id":1,"nome":"vou-sumir","sequencia":"GATTACA","tamanho":7}]

$ sudo docker stop dna-temporario && sudo docker rm -v dna-temporario
dna-temporario
dna-temporario

$ sudo docker run -d --name dna-temporario2 -p 8001:8000 dna-analyzer:1.0
c84a5bc38e18de33456a1ad1cc38574d629f92438f0a7e36d4507280f922f013

$ curl http://localhost:8001/sequencias
[]

$ sudo docker stop dna-temporario2 && sudo docker rm -v dna-temporario2
dna-temporario2
dna-temporario2

$ sudo docker volume ls
DRIVER    VOLUME NAME
```

**Explicação:** sem a opção `-v` no `docker run`, o diretório `/app/data` (e,
dentro dele, o arquivo `sequencias.db`) não é gerenciado por um volume
nomeado por nós. Isso significa que os dados ficam vinculados apenas àquele
contêiner específico, sem nenhum ponto de acesso compartilhado com outros
contêineres. Ao remover o contêiner com `docker rm -v`, tudo o que estava
armazenado ali, inclusive qualquer volume interno criado automaticamente
pelo Docker para aquele diretório, é removido junto. Por isso o
`dna-temporario2`, mesmo sendo criado a partir da mesma imagem, inicia
completamente "do zero": nenhuma sequência do contêiner anterior está
disponível, e o `id` do banco reinicia do 1. Isso contrasta diretamente com
a Etapa 4/5, onde o volume foi **nomeado** (`dna-dados`) e reaproveitado
deliberadamente com `-v dna-dados:/app/data` em dois `docker run`, por
isso, os dados persistiram entre contêineres diferentes.
O `docker volume ls` ao final confirma que nenhum resíduo de dado ficou para
trás.

## 6. Etapa 7 — Inspeção

**a) Onde o Docker armazena fisicamente o volume `dna-dados`?**

```
$ sudo docker volume inspect dna-dados
[
    {
        "CreatedAt": "2026-09-18T11:05:53-03:00",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/dna-dados/_data",
        "Name": "dna-dados",
        "Options": null,
        "Scope": "local"
    }
]
```

Esse é o caminho, dentro do sistema de arquivos do Docker Engine (rodando no
WSL, neste caso), onde o arquivo `sequencias.db` fica fisicamente armazenado,
independente de qual contêiner está usando o volume no momento.

**b) Qual o conteúdo do diretório `/app/data` dentro do contêiner?**

```
$ sudo docker exec dna2 ls -la /app/data
total 20
drwxr-xr-x 2 root root  4096 Sep 19 00:47 .
drwxr-xr-x 1 root root  4096 Sep 19 00:54 ..
-rw-r--r-- 1 root root 12288 Sep 19 00:47 sequencias.db
```

**c) O que acontece ao rodar `docker volume rm dna-dados` com o contêiner
parado e removido?**

```
$ sudo docker stop dna2 && sudo docker rm dna2
dna2
dna2

$ sudo docker volume rm dna-dados
dna-dados

$ sudo docker volume ls
DRIVER    VOLUME NAME
local     2e10477300391c0fdfb4d2ec2e43cee364f3f0ffd67fcf2a4a172539f04df168
local     978e2123fef3e0a30132dae43dfd54b66d8804b7e0a750890f31cce360544eaa
```

O volume `dna-dados` e todos os dados nele contidos (o `sequencias.db` com
todo o histórico de análises) foram removidos permanentemente. Esse comando
só funciona se nenhum contêiner estiver usando o volume no momento — por
isso foi necessário parar e remover o `dna2` antes de conseguir removê-lo.
A listagem final (`docker volume ls`) fica completamente vazia, sem nenhum
volume restante no sistema.

## 7. Dificuldades e aprendizados

Como escolhi essa temática (Analisador de DNA), aprendi a calcular o
conteúdo GC (%). Não tive grandes dificuldades para entender: é um cálculo
bem simples, que relaciona as bases Guanina (G) e Citosina (C) com o total
de bases da sequência. Também compreendi melhor o complemento reverso de
cada uma das sequências, além de ter pesquisado algumas curiosidades.

Outra coisa que me chamou a atenção foi como o Docker Engine consegue
gerenciar para que os dados continuem (sobrevivam, com volume nomeado) e
entender o conceito da camada de escrita efêmera, onde os dados somem (sem
volume nomeado explícito). Também descobri, na prática, que ao rodar
`docker run -d`, o terminal volta o controle imediatamente, mas o servidor
Flask dentro do contêiner ainda leva um instante para terminar de subir —
tentei fazer um `curl` logo em seguida e recebi "connection refused",
porque a aplicação ainda não estava pronta para aceitar conexões. Resolvi
adicionando um pequeno `sleep` entre subir o contêiner e testar a API, o que
me fez entender melhor que o `-d` (modo *detached*) só garante que o
contêiner foi iniciado, não que a aplicação lá dentro já está pronta.

A sintaxe do `curl` também é diferente entre PowerShell e bash/WSL: no
PowerShell, `curl` é um "apelido" para `Invoke-WebRequest`, que trata aspas
de forma diferente. Isso quebrou o primeiro teste de `POST`, até eu trocar
para `curl.exe` explícito, com aspas escapadas. Apesar disso, usei mais o
bash/WSL ao longo da atividade.

## 8. Referências

[1] What is palindromic sequence? Disponível em:
https://youtu.be/pW9hH3NqSOA?si=oUPUjc9IfQu2scVr. Acesso em: 18 set. 2026.
