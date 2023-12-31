"""
Comportamiento generalizado para caminar por la cuadrícula, una celda a la vez.
"""
import math
import mesa

def get_distance(pos_1, pos_2):
    """
    Obtiene la distancia entre dos puntos según
    la distancia Euclidea entre dos puntos

    Args:
        pos_1, pos_2: Coodenadas de las tuplas de ambos puntos
    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

class Walker(mesa.Agent):
    """
    Clase que implementa métodos de caminante (walker) de manera generalizada.
    No está diseñado para usarse por sí solo, sino para heredar sus métodos a muchos otros agentes.
    """

    grid = None
    x = None
    y = None
    moore = True

    def __init__(self, unique_id, pos, model, moore=False):
        """
        grid: El objeto MultiGrid en el que vive el agente.
        x: La coordenada x actual del agente.
        y: La coordenada y actual del agente.
        moore: Si es Verdadero, puede moverse en las 8 direcciones.
                De lo contrario, sólo arriba, abajo, izquierda, derecha.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.moore = moore

    # Comprueba si una celda de la cuadrícula está ya ocupada
    # por otro agente tipo Avión
    def esta_ocupado(self, pos):
        from agents import Avion
        this_cell = self.model.grid.get_cell_list_contents([pos])
        ret = any(isinstance(agent, Avion)
                  for agent in this_cell
                  )
        return ret

    def volar_aeropuerto(self, control_colisiones):

        # Si es viaje de ida se vuela aeropuerto de salida -> llegada
        # Sino llegada -> salida

        if self.viaje_ida:
            next_moves = self.model.grid.get_neighborhood(self.pos_llegada, self.moore, True)
        else:
            next_moves = self.model.grid.get_neighborhood(self.pos_salida, self.moore, True)

        # Reducir posiciones de la cuadricula a los más cercanos
        min_dist = min(get_distance(self.pos, pos) for pos in next_moves)
        # Si hay distancia minima calculamos el camino
        if min_dist > 0:
            while min_dist > 0:
                final_candidates = [
                    pos for pos in next_moves if get_distance(self.pos, pos) == min_dist
                ]
                next_move = final_candidates[0]
                next_moves = self.model.grid.get_neighborhood(next_move, self.moore, True)
                min_dist = min(get_distance(self.pos, pos) for pos in next_moves)

            # Como es 0, lo movemos a esta posicion

            # Comprobamos si ya esta ocupado para evitar colision si
            # esta activado este parametro (solo en ruta, no se tiene en cuenta en aeropuerto)
            if self.control_colisiones:
                # Comprobamos que el siguente movimiento no es un avion
                # y que no se corresponde con el salida o llegada (por si hay más aviones estacionados)
                if self.esta_ocupado(next_move) and self.pos_salida != next_move and self.pos_llegada != next_move:
                    next_moves_colision = self.model.grid.get_neighborhood(self.pos, self.moore, True)
                    final_candidates_colision = [
                        pos for pos in next_moves_colision if not self.esta_ocupado(pos)
                    ]
                    next_move = final_candidates_colision[0]
                    print("POSIBLE COLISION DEL AVION "+ str(self.unique_id) + " --> Cambio de ruta de pos: " + str(self.pos) + " a " + str(next_move))

            self.model.grid.move_agent(self, next_move)
            self.pos = next_move
        # Si la distancia minima es 0 es que ha llegado
        elif min_dist == 0:
            if self.viaje_ida: # vuelo salida -> llegada
                self.model.grid.move_agent(self, self.pos_llegada)
                self.pos = self.pos_llegada
                self.viaje_ida = False
                self.en_vuelo = False
            else: # vuelo llegada -> salida
                self.model.grid.move_agent(self, self.pos_salida)
                self.pos = self.pos_salida
                self.viaje_ida = True
                self.en_vuelo = False

