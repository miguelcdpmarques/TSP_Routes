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

    def select_parents(self):
        parent_1, parent_2 = self.select_by_odds(), self.select_by_odds()
        while parent_2 == parent_1:
            parent_2 = self.select_by_odds()
        return parent_1, parent_2

    def crossover_parents(self, parents, Pc=0.7):
        parent_1, parent_2 = parents
        if random.random() <= Pc:
            routes = [[], []]
            for i, parent in enumerate(parents):
                cp = random.randint(1, len(parent.points) - 2)
                new_points = parent.points[:cp]
                remaining_points = [point for point in parents[-i].points if point not in new_points] + [0]
                routes[i] = new_points + remaining_points
            route1_points, route2_points = routes  
        else: 
            route1_points, route2_points = parent_1.points, parent_2.points
        return Route(points=route1_points), Route(points=route2_points)

    def mutate_points(self, Pm=0.4):
        """Applies a random middle points swap with probability of Pm"""
        for element in self.elements[1:]:
            if random.random() <= Pm:
                element.swap()
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
    
    def swap(self):
        """Swaps two random middle points"""
        idx = random.randint(1, len(self.points) - 3)
        self.points[idx+1], self.points[idx] = self.points[idx], self.points[idx+1]

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
            parents = population.select_parents()
            children = population.crossover_parents(parents)
            for child in children:
                newPopulation.elements.append(child) 
        newPopulation.mutate_points()
        population = newPopulation
        population.setup_ga()
        print("Best: ", population.elements[0])
    if map:
        population.elements[0].map_points()
    return population.elements[0]
    

if __name__ == '__main__':
    n_generations = 200
    len_population = 15
    best_fitness = 0
    for i in range(5):
        route = run_ga(n_generations, len_population, map=False)
        if route.fitness > best_fitness:
            best_route, best_fitness = route, route.fitness
    best_route.map_points()
    


