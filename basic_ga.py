import random
from here import HereAPI
from instance import APP_ID, APP_CODE


here = HereAPI(APP_ID=APP_ID,APP_CODE=APP_CODE)
cost_table = here.calculate_matrix(points=here.seed_points())
cost_table = cost_table.set_index(['startIndex', 'destinationIndex'])


class Population:
    def __init__(self, n_routes):
        self.n_routes = n_routes
        self.elements = []
        for i in range(n_routes):
            route = list(range(1, 9))
            random.shuffle(route)
            self.elements.append(Route(points=[0] + route + [0]))

    def __repr__(self):
        return "<Population({} routes)>".format(self.n_routes)

    def setup_ga(self):
        self.order_by_fitness()
        self.set_route_relative_fitness()
        self.set_route_cumulative_odds()

    @property
    def best_genes(self, n_routes=2):
        self.order_by_fitness()
        return [i.points for i in self.elements[:n_routes]]

    def seed_best_genes(self, best_genes):
        for points in best_genes:
            self.elements.append(Route(points=points))

    def order_by_fitness(self):
        self.elements = sorted(self.elements, key=lambda route: route.fitness, reverse=True)

    def set_route_relative_fitness(self):
        sum_routes_fitness = sum(route.fitness for route in self.elements)
        for route in self.elements:
            route.relative_fitness = round(route.fitness / sum_routes_fitness, 4)

    def set_route_cumulative_odds(self):
        odds = 1
        for route in self.elements:
            route.cumulative_odds = round(odds, 4)
            odds -= route.relative_fitness

    def select_by_odds(self):
        selected_route = random.random()
        try:
            index, _ = next(route for route in enumerate(self.elements) 
                            if route[1].cumulative_odds < selected_route)
        except StopIteration:
            index = len(self.elements) - 1
        return self.elements[index]

    def tournament_selection(self):
        first, second = random.randint(0, len(self.elements)-1), random.randint(0, len(self.elements)-1)
        if self.elements[first].fitness > self.elements[second].fitness:
            return self.elements[first]
        else:
            return self.elements[second]

    def select_parents(self, method='roulette'):
        possible_methods = ['roulette', 'tournament']
        if method not in possible_methods:
            raise ValueError('The value {} is not one of the possible choices: {}'.format(
                            method, possible_methods))
        if method == 'roulette':
            parent_1, parent_2 = self.select_by_odds(), self.select_by_odds()
            while parent_2 == parent_1:
                parent_2 = self.select_by_odds()
            return parent_1, parent_2
        elif method == 'tournament':
            parent_1, parent_2 = self.tournament_selection(), self.tournament_selection()
            while parent_2 == parent_1:
                parent_2 = self.tournament_selection()
            return parent_1, parent_2

    def crossover_parents(self, parents, Pc=0.5, method='kSplits'):
        possible_methods = ['kSplits', 'sameIndexes']
        if method not in possible_methods:
            raise ValueError('Method {} not in {}'.format(method, possible_methods))
        parent_1, parent_2 = parents
        if random.random() <= Pc:
            routes = [[], []]
            if method == 'kSplits':
                for i, parent in enumerate(parents):
                    cp = random.randint(1, len(parent.points) - 2)
                    new_points = parent.points[:cp]
                    remaining_points = [point for point in parents[-i].points if point not in new_points] + [0]
                    routes[i] = new_points + remaining_points

            elif method == 'sameIndexes':
                base_route = [parent_1.points[i] if parent_2.points[i] == point else -1 
                                                for i, point in enumerate(parent_1.points)]
                remaining_points = [point for point in parent_1.points if point not in base_route]
                for i in range(2):
                    random.shuffle(remaining_points)
                    iter_remaining_points = iter(remaining_points)
                    routes[i] = [point if point >-1 else next(iter_remaining_points) for i, point in enumerate(base_route)]
            route1_points, route2_points = routes  
        else: 
            route1_points, route2_points = parent_1.points, parent_2.points
        return Route(points=route1_points), Route(points=route2_points)

    def mutate_points(self, Pm=0.1, force_neighbors=True):
        """Applies a random middle points swap with probability of Pm"""
        for element in self.elements[1:]:
            if random.random() <= Pm:
                element.swap(force_neighbors)
        element.fitness = element.route_fitness()        

   

class Route:
    def __init__(self, points):
        self.points = points
        self.fitness = self.route_fitness()

    def __repr__(self):
        return "<Route({}) Fitness: {}>".format(self.points, self.fitness)

    def route_fitness(self):
        """Calculates the total cost of the route"""
        if self.points[0] != 0 or self.points[-1] != 0:
            raise ValueError('Previous operation messed up order')
        result = 0
        for i in range(1, len(self.points)):
            cost = cost_table.xs((self.points[i-1], self.points[i]))['costFactor']
            result += cost
        return (1/result)
    
    def swap(self, force_neighbors=True):
        """Swaps two random middle points"""
        if force_neighbors:
            idx = random.randint(1, len(self.points) - 3)
            self.points[idx+1], self.points[idx] = self.points[idx], self.points[idx+1]
        else:
            idx1, idx2 = random.randint(1, len(self.points) - 2), random.randint(1, len(self.points) - 2)
            while idx1 == idx2:
                idx2 = random.randint(1, len(self.points) - 2)
            self.points[idx1], self.points[idx2] = self.points[idx2], self.points[idx1]

    def map_points(self):
        from map_route import MapRoute
        my_map = MapRoute(self)
        my_map.map_points()


def run_ga(n_generations=100, len_population=10, crossover=True, mutation=True, map=True):
    population = Population(len_population)
    population.setup_ga()
    print("Original", population.elements, '\n')

    for i in range(n_generations):
        newPopulation = Population(0)
        newPopulation.seed_best_genes(population.best_genes)
        for i in range(len_population - 1):
            parents = population.select_parents(method='tournament')
            children = population.crossover_parents(parents, method='sameIndexes')
            for child in children:
                newPopulation.elements.append(child) 
        newPopulation.mutate_points(force_neighbors=False)
        population = newPopulation
        population.setup_ga()
        print("Best: ", population.elements[0])
    if map:
        population.elements[0].map_points()
    return population.elements[0]
    

if __name__ == '__main__':
    n_generations = 50
    len_population = 20
    best_fitness = 0
    route = run_ga(n_generations, len_population, map=False)
    if route.fitness > best_fitness:
        best_route, best_fitness = route, route.fitness
    best_route.map_points()
    


