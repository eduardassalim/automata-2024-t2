"""Processa."""

from typing import Set, Dict, Tuple, List, Union


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


def load_automata(filename: str) -> Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]]:
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

        if estado_inicial not in estados:
            raise ErroException("Estado inicial não está dentro de estados.")

        if not estados_finais .issubset(estados):
            raise ErroException("Estado final não está dentro de estados.")

        transicoes = {}

        for regra in linhas[4:]:
            nodo = regra.split()
            if len(nodo) != 3:
                raise ErroException("Transição inválida.")

            origem, simbolo, destino = nodo

            if origem not in estados or simbolo not in alfabeto and simbolo != '&' or destino not in estados:
                raise ErroException("Símbolos inválidos.")

            if (origem, simbolo) not in transicoes:
                transicoes[(origem, simbolo)] = destino
            else:
                if isinstance(transicoes[(origem, simbolo)], list):
                    transicoes[(origem, simbolo)].append(destino)
                else:
                    transicoes[(origem, simbolo)] = [transicoes[(origem, simbolo)], destino]

        return estados, alfabeto, transicoes, estado_inicial, estados_finais
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo {filename} não encontrado.") from e


def process(
    automata: Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]],
    words: List[str]
) -> Dict[str, str]:
    """ Processa automato."""
    _, sigma, _, _, _ = automata
    dfa = convert_to_dfa(automata)
    _, _, dfa_transicao, dfa_inicial, dfa_final = dfa

    verifica = {}
    try:
        for word in words:
            estado_atual = dfa_inicial
            verificacao = True

            for simbolo in word:
                if simbolo not in sigma and simbolo != '&':
                    verifica[word] = "INVALIDA"
                    verificacao = False
                    break

                if (estado_atual, simbolo) in dfa_transicao:
                    estado_atual = dfa_transicao[(estado_atual, simbolo)]
                else:
                    verifica[word] = "REJEITA"
                    verificacao = False
                    break

            if verificacao:
                if estado_atual in dfa_final:
                    verifica[word] = "ACEITA"
                else:
                    verifica[word] = "REJEITA"

    except Exception as e:
        raise ErroException(f"Erro ao processar palavra '{word}': {e}.") from e

    return verifica


def epsilon_closure(
    estado: str, transicao: Dict[Tuple[str, str], Union[str, List[str]]]
) -> Set[str]:
    """ Process epsilon_closure."""
    closure = {estado}
    pilha = [estado]

    while pilha:
        estado_atual = pilha.pop()
        if (estado_atual, '&') in transicao:
            destinos = transicao[(estado_atual, '&')]
            if isinstance(destinos, str):
                destinos = [destinos]
            for dest in destinos:
                if dest not in closure:
                    closure.add(dest)
                    pilha.append(dest)
    return closure


def convert_to_dfa(
    automata: Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]]
) -> Tuple[Set[str], Set[str], Dict[Tuple[str, str], str], str, Set[str]]:
    """ Processa conversão."""
    _, sigma, dfa_transicao, dfa_inicial, dfa_final = automata

    estados_novos = set()
    nova_transicao = {}
    nao_processado = [frozenset(epsilon_closure(dfa_inicial, dfa_transicao))]
    mapeamento = {frozenset(epsilon_closure(dfa_inicial, dfa_transicao)): 'S0'}
    novo_inicial = 'S0'
    novo_estado_final = set()
    contador = 1

    while nao_processado:
        subset_atual = nao_processado.pop()
        novo_estado_atual = mapeamento[subset_atual]

        if not subset_atual.isdisjoint(dfa_final):
            novo_estado_final.add(novo_estado_atual)

        estados_novos.add(novo_estado_atual)

        for simbolo in sigma:
            proximo = frozenset(
                dest for state in subset_atual
                if (state, simbolo) in dfa_transicao
                for dest in (
                    dfa_transicao[(state, simbolo)]
                    if isinstance(dfa_transicao[(state, simbolo)], list)
                    else [dfa_transicao[(state, simbolo)]]
                )
                for dest in epsilon_closure(dest, dfa_transicao)
            )

            if proximo:
                if proximo not in mapeamento:
                    mapeamento[proximo] = f'S{contador}'
                    nao_processado.append(proximo)
                    contador += 1

                nova_transicao[(novo_estado_atual, simbolo)] = mapeamento[proximo]

    return estados_novos, sigma, nova_transicao, novo_inicial, novo_estado_final
