"""Aqui vou implementar dfa."""


class ErroException(Exception):
    """Aqui crio uma exceção personalizada.

    Args:
        mensagem (str): descrição do erro encontrado.
    """

    def __init__(self, mensagem):
        """Aqui inicializa a exceção.

        Args:
            mensagem (str): Mensagem do erro.
        """
        self.mensagem = mensagem
        super().__init__(self.mensagem)


def load_automata(filename: str):
    """Aqui carrega um autômato a partir de um arquivo."""
    try:
        with open(filename, encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()

            if len(linhas) < 5:
                raise ErroException("Arquivo não é autômato.")

            alfabeto = linhas[0].strip().split()
            estados = linhas[1].strip().split()
            estados_finais = linhas[2].strip().split()
            estado_inicial = linhas[3].strip()
            transicao = [linha.strip().split() for linha in linhas[4:]]

            transicoes = {}

            for estado in estados:
                transicoes[transicoes] = []
                for simbolo in alfabeto:
                    transicoes[estado][simbolo] = None

            for origem, simbolo, destino in transicao:
                if origem in estados and simbolo in alfabeto and destino in estados:
                    transicao[origem][simbolo] = destino
                else:
                    raise ErroException("Transição inválida.")

            for estado in estados_finais:
                if estado not in estados:
                    raise ErroException("Estado final não encontrado.")

            if estado_inicial not in estados:
                raise ErroException("Estado inicial não encontrado")

            automata = alfabeto, estados, transicao, estado_inicial, estados_finais
            return automata

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo {filename} não encontrado.") from e


def process(automata, words):
    """Aqui processa lista de palavras."""
    alfabeto, estados_finais, estado_inicial, transicoes = automata

    verifica = {}
    try:
        for word in words:
            estado_atual = estado_inicial
            verificacao = True

            for simbolo in word:
                if simbolo not in alfabeto:
                    verifica[word] = "INVÁLIDA"
                    verificacao = False
                    break

                estado_atual = transicoes[estado_atual].get(simbolo)

                if estado_atual is None:
                    verifica[word] = "REJEITA"
                    verificacao = False
                    break

                if verificacao:
                    if estado_atual in estados_finais:
                        verifica[word] = "ACEITA"
                    else:
                        verifica[word] = "REJEITA"

    except Exception as e:
        raise ErroException(f"Erro ao processar palavra '{word}': {e}.") from e

    return verifica


def convert_to_dfa(automata):
    """Aqui crio a função."""

    alfabeto, estados, transicao, estado_inicial, estados_finais = automata

    if all(len(transicao[estado].keys()) == len(alfabeto) for estado in estados):
        return automata

    def move(estado):
        movimento = set()
        pilha = [estado]
        while pilha:
            s = pilha.pop()
            movimento.add(s)
            for dest in transicao[s].get('&', []):
                if dest not in movimento:
                    pilha.append(dest)
        return movimento

    nfa_para_dfa = {}

    def estados_alcancaveis(estado_nfa):
        alcanca = set()
        for estado in estado_nfa:
            for dest in transicao.get(estado, {}).keys():
                if dest != '&':
                    alcanca.add(dest)
                    alcanca.update(transicao[estado].get(dest, []))
        return tuple(sorted(alcanca))

    movimento_inicial = move(estado_inicial)
    nfa_para_dfa[movimento_inicial] = {}
    estados_dfa = [movimento_inicial]

    fila = [movimento_inicial]
    while fila:
        estado_dfa = fila.pop(0)
        for simbolo in alfabeto:
            if simbolo == '&':
                continue
            novo_estado_nfa = set()
            for estado_nfa in estado_dfa:
                if simbolo in transicao.get(estado_nfa, {}):
                    novo_estado_nfa.update(transicao[estado_nfa][simbolo])
            novo_estado_nfa_fecho = move(tuple(sorted(novo_estado_nfa)))
            if novo_estado_nfa_fecho not in nfa_para_dfa:
                nfa_para_dfa[novo_estado_nfa_fecho] = {}
                estados_dfa.append(novo_estado_nfa_fecho)
                fila.append(novo_estado_nfa_fecho)
            nfa_para_dfa[estado_dfa][simbolo] = novo_estado_nfa_fecho

    estados_finais_dfa = []
    for estado_dfa in estados_dfa:
        for estado_nfa in estado_dfa:
            if estado_nfa in estados_finais:
                estados_finais_dfa.append(estado_dfa)
                break

    novo_automato = (alfabeto, estados_dfa, nfa_para_dfa, movimento_inicial, estados_finais_dfa)

    return novo_automato
