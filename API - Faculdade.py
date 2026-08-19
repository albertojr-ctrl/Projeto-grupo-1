import requests
 
Base_url = "https://servicodados.ibge.gov.br/api/v3/agregados"
 
 
def montar_periodos(ano_inicio, tri_inicio, ano_fim, tri_fim):
    
    periodos = []
    ano, tri = ano_inicio, tri_inicio
    while (ano, tri) <= (ano_fim, tri_fim):
        periodos.append(f"{ano}{tri:02d}")
        tri += 1
        if tri > 4:
            tri, ano = 1, ano + 1
    return "|".join(periodos)
 
 
def listar_variaveis(agregado):
    
    resp = requests.get(f"{Base_url}/{agregado}/metadados")
    resp.raise_for_status()
    for v in resp.json().get("variaveis", []):
        print(f"{v['id']}: {v['nome']}")
 
 
def listar_categorias(agregado, classificacao_id):
    
    resp = requests.get(f"{Base_url}/{agregado}/metadados")
    resp.raise_for_status()
    for c in resp.json().get("classificacoes", []):
        if str(c["id"]) == str(classificacao_id):
            print(f"Classificação {c['id']} - {c['nome']}:")
            for cat in c["categorias"]:
                print(f"  {cat['id']}: {cat['nome']}")
            return
    print("Classificação não encontrada nesse agregado.")
 
 
def consultar_agregado(agregado, variavel, periodos, localidade="N3[26]", classificacoes=None):

    classificacoes = classificacoes or {2: "all"}
    filtro_class = "".join(
        f"&classificacao={cid}[{cats}]" for cid, cats in classificacoes.items()
    )
 
    url = (
        f"{Base_url}/{agregado}/periodos/{periodos}/variaveis/{variavel}"
        f"?localidades={localidade}{filtro_class}"
    )
 
    resposta = requests.get(url)
    if resposta.status_code != 200:
        print(f"Erro ao consultar a API. Status: {resposta.status_code}")
        return None
 
    dados = resposta.json()
    if not dados:
        print("Nenhum resultado retornado.")
        return None
 
    item = dados[0]
    print(f"Variável: {item['variavel']}  |  Unidade: {item.get('unidade', 'N/D')}")
 
    for resultado in item.get("resultados", []):
        rotulo = ", ".join(
            nome
            for c in resultado.get("classificacoes", [])
            for nome in c.get("categoria", {}).values()
        )
        for serie in resultado.get("series", []):
            cabecalho = serie["localidade"]["nome"]
            if rotulo:
                cabecalho += f" — {rotulo}"
            print(f"\n{cabecalho}")
            for periodo, valor in serie["serie"].items():
                print(f"  {periodo}: {valor}")
 
    return dados
 
 
if __name__ == "__main__":
    periodos = montar_periodos(2012, 1, 2026, 2)
    
    consultar_agregado(agregado=4093, variavel=4099, periodos=periodos)

# Eu acho que é assim? sla eu realmente to exausto de passar o dia todo fazendo isso.