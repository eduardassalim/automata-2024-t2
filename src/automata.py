import os
from typing import Set, Dict, Tuple, List, Union

def load_automata(filename: str) -> Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]]:

    try:
        with open(filename, 'r') as file:
            lines = file.read().splitlines()

        if len(lines) < 5:
            raise ValueError("Descrição incompleta do autômato.")

        linhaAlfabeto  = set(lines[0].split())  # Símbolos do alfabeto
        linhaEstados  = set(lines[1].split())  # Estados
        linhaEstadoFinal  = set(lines[2].split())  # Estados finais
        linhaEstadoInicial = lines[3]  # Estado inicial

        if linhaEstadoInicial not in linhaEstados :
            raise ValueError("Estado inicial não está no conjunto de estados.")

        if not linhaEstadoFinal .issubset(linhaEstados ):
            raise ValueError("Estados finais não estão no conjunto de estados.")

        delta = {}  

        for rule in lines[4:]:
            parts = rule.split()
            if len(parts) != 3:
                raise ValueError("Formato inválido da regra de transição.")
            origin, symbol, destination = parts
            if origin not in linhaEstados  or (symbol not in linhaAlfabeto  and symbol != '&') or destination not in linhaEstados :
                raise ValueError("Componentes da regra inválidos.")
            if (origin, symbol) not in delta:
                delta[(origin, symbol)] = destination
            else:
                if isinstance(delta[(origin, symbol)], list):
                    delta[(origin, symbol)].append(destination)
                else:
                    delta[(origin, symbol)] = [delta[(origin, symbol)], destination]

        return linhaEstados , linhaAlfabeto , delta, linhaEstadoInicial, linhaEstadoFinal 
    except FileNotFoundError as exc:
        raise FileNotFoundError("Arquivo não encontrado.") from exc
    except Exception as e:
        raise Exception(f"Erro ao carregar o autômato: {e}") from e


def process(
    automato: Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]],
    words: List[str]
) -> Dict[str, str]:
 
    _, sigma, _, _, _ = automato
    dfa = convert_to_dfa(automato)
    _, _, dfa_delta, dfa_q0, dfa_final = dfa
    results = {}

    for word in words:
        current_state = dfa_q0
        valid = True
        for symbol in word:
            if symbol not in sigma and symbol != '&':
                results[word] = "INVALIDA"
                valid = False
                break
            if (current_state, symbol) in dfa_delta:
                current_state = dfa_delta[(current_state, symbol)]
            else:
                results[word] = "REJEITA"
                valid = False
                break
        if valid:
            if current_state in dfa_final:
                results[word] = "ACEITA"
            else:
                results[word] = "REJEITA"
    return results


def epsilon_closure(
    state: str, delta: Dict[Tuple[str, str], Union[str, List[str]]]
) -> Set[str]:
  
    closure = {state}
    stack = [state]
    while stack:
        current_state = stack.pop()
        if (current_state, '&') in delta:
            destinations = delta[(current_state, '&')]
            if isinstance(destinations, str):
                destinations = [destinations]
            for dest in destinations:
                if dest not in closure:
                    closure.add(dest)
                    stack.append(dest)
    return closure


def convert_to_dfa(
    automato: Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]]
) -> Tuple[Set[str], Set[str], Dict[Tuple[str, str], str], str, Set[str]]:
  
    _, sigma, delta, q0, final_states = automato

    new_states = set()
    new_delta = {}
    unprocessed_states = [frozenset(epsilon_closure(q0, delta))]
    state_mapping = {frozenset(epsilon_closure(q0, delta)): 'S0'}
    new_q0 = 'S0'
    new_final_states = set()
    state_counter = 1

    while unprocessed_states:
        current_subset = unprocessed_states.pop()
        current_state_name = state_mapping[current_subset]

        if not current_subset.isdisjoint(final_states):
            new_final_states.add(current_state_name)

        new_states.add(current_state_name)

        for symbol in sigma:
            next_subset = frozenset(
                dest for state in current_subset
                if (state, symbol) in delta
                for dest in (
                    delta[(state, symbol)]
                    if isinstance(delta[(state, symbol)], list)
                    else [delta[(state, symbol)]]
                )
                for dest in epsilon_closure(dest, delta)
            )

            if next_subset:
                if next_subset not in state_mapping:
                    state_mapping[next_subset] = f'S{state_counter}'
                    unprocessed_states.append(next_subset)
                    state_counter += 1

                new_delta[(current_state_name, symbol)] = state_mapping[next_subset]

    return new_states, sigma, new_delta, new_q0, new_final_states


if __name__ == "__main__":
    current_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(current_directory, "../examples/06-nfa.txt")

    automato = load_automata(absolute_path)
    automato_dfa = convert_to_dfa(automato)

    words = ["a", "b", "ab", "abb", "aabb", "abab", "baba", "bbaa", "bbbabaaa", "bbabbaa"]
    results = process(automato_dfa, words)

    print("Resultados no DFA:")
    for word, result in results.items():
        print(f"{word}:{result}", end= ', ')



