class ErroException(Exception):
    """Exceção personalizada para erros no autômato."""
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)


def load_automata(filename: str) -> tuple:
    """Carrega um autômato a partir de um arquivo."""
    try:
        with open(filename, encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()

            if len(linhas) < 5:
                raise ErroException("Arquivo não é um autômato válido.")

            alfabeto = linhas[0].strip().split()
            estados = linhas[1].strip().split()
            estados_finais = linhas[2].strip().split()
            estado_inicial = linhas[3].strip()
            transicoes = [linha.strip().split() for linha in linhas[4:]]

            if estado_inicial not in estados:
                raise ErroException("Estado inicial não encontrado nos estados definidos.")
            for estado_final in estados_finais:
                if estado_final not in estados:
                    raise ErroException(f"Estado final '{estado_final}' não encontrado nos estados definidos.")
            for origem, simbolo, destino in transicoes:
                if origem not in estados or destino not in estados or simbolo not in alfabeto:
                    raise ErroException(f"Transição '{origem} - {simbolo} -> {destino}' inválida.")

            delta = {estado: {simbolo: None for simbolo in alfabeto} for estado in estados}
            for origem, simbolo, destino in transicoes:
                delta[origem][simbolo] = destino

            return (estados, alfabeto, delta, estado_inicial, estados_finais)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo '{filename}' não encontrado.") from e


def process(automata, words: list) -> dict:
    """Processa uma lista de palavras utilizando um autômato."""
    estados, alfabeto, delta, estado_inicial, estados_finais = automata
    resultados = {}

    for word in words:
        estado_atual = estado_inicial
        aceita = False

        for simbolo in word:
            if simbolo not in alfabeto:
                resultados[word] = "INVÁLIDA"
                aceita = None
                break
            estado_atual = delta[estado_atual].get(simbolo)
            if estado_atual is None:
                aceita = False
                break

        if aceita is None:
            continue  

        if estado_atual in estados_finais:
            resultados[word] = "ACEITA"
        else:
            resultados[word] = "REJEITA"

    return resultados


def convert_to_dfa(automata) -> tuple:
    """Converte um autômato para um autômato dfa."""
    estados, alfabeto, delta, estado_inicial, estados_finais = automata


    if all(len(delta[estado][simbolo]) == 1 for estado in estados for simbolo in alfabeto):
        return automata

    novo_delta = {}
    novo_estados_finais = []

    def epsilon_fecho(estados):
        fecho = set(estados)
        for estado in estados:
            if '' in delta[estado]:
                fecho.update(delta[estado][''])
                fecho.update(epsilon_fecho(delta[estado]['']))
        return fecho

    novo_estado_inicial = frozenset(epsilon_fecho([estado_inicial]))
    estados_processados = set()

    estados_pendentes = [novo_estado_inicial]
    while estados_pendentes:
        estado_atual = estados_pendentes.pop()
        if estado_atual in estados_processados:
            continue
        estados_processados.add(estado_atual)
        
        novo_delta[estado_atual] = {simbolo: set() for simbolo in alfabeto}
        
        fecho_estado_atual = epsilon_fecho(estado_atual)
        
        if any(estado in estados_finais for estado in fecho_estado_atual):
            novo_estados_finais.append(estado_atual)
        
        for simbolo in alfabeto:
            prox_estado = set()
            for estado in fecho_estado_atual:
                if simbolo in delta[estado]:
                    prox_estado.update(delta[estado][simbolo])
            fecho_prox_estado = epsilon_fecho(prox_estado)
            novo_estado = frozenset(fecho_prox_estado)
            novo_delta[estado_atual][simbolo] = novo_estado
            if novo_estado not in estados_processados:
                estados_pendentes.append(novo_estado)
    
    novo_estados = list(novo_delta.keys())
    novo_delta_tuplas = {estado: {simbolo: tuple(sorted(novo_delta[estado][simbolo])) for simbolo in alfabeto} for estado in novo_estados}
    novo_estado_inicial_tupla = tuple(sorted(novo_estado_inicial))
    novo_estados_finais_tupla = [tuple(sorted(estado)) for estado in novo_estados_finais]

    return (novo_estados, alfabeto, novo_delta_tuplas, novo_estado_inicial_tupla, novo_estados_finais_tupla)
