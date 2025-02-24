import numpy as np


class EONEnvironment:
    def __init__(self, topology_data, num_wavelengths, traffic_generator):
        """
        topology_data (dict): (cac node, cac canh, danh sach lien ket)
        num_wavelengths (int): So luong buoc song moi lien ket
        traffic_generator (TrafficGenerator)
        """
        self.nodes = topology_data['nodes']
        self.edges = topology_data['edges']
        self.adjacency_list = topology_data['adjacency_list']
        self.num_wavelengths = num_wavelengths
        self.traffic_generator = traffic_generator
        self.current_service_request = None
        self.reset()

    def reset(self):
        self.wavelength_usage = {
            edge: np.zeros(self.num_wavelengths, dtype=int) for edge in self.edges
        }
        self.current_service_request = None
        self.service_history = []
        return self._get_state()

    def step(self, action):
        """
        Thuc hien action trong environment va tra ve next state, reward, done
        action (int): Chi so buoc song duoc gan
        """
        reward = 0
        done = False
        info = {}

        if self.current_service_request is None:
            done = True
            reward = 0
            return self._get_state(), reward, done, info

        if action == -1:
            reward = -1
            info['action_taken'] = 'block'
            info['wavelength_assigned'] = -1
            self.service_history.append(
                {'request': self.current_service_request, 'action': 'blocked'})
            done = True
        else:
            wavelength_index = action
            if 0 <= wavelength_index < self.num_wavelengths:
                path = self.current_service_request['path']
                if self._is_wavelength_available(path, wavelength_index):
                    self._assign_wavelength(path, wavelength_index)
                    reward = 1
                    info['action_taken'] = 'assign'
                    info['wavelength_assigned'] = wavelength_index
                    self.service_history.append(
                        {'request': self.current_service_request, 'action': 'assigned', 'wavelength': wavelength_index})
                    done = True
                else:
                    reward = -10
                    info['action_taken'] = 'invalid_assign'
                    info['wavelength_assigned'] = -1
                    done = True
            else:
                reward = -10
                info['action_taken'] = 'invalid_action_index'
                info['wavelength_assigned'] = -1
                print(f"action = {action}")
        self.current_service_request = None
        return self._get_state(), reward, done, info

    def _get_state(self):
        state_components = []
        for edge in self.edges:
            usage = self.wavelength_usage[edge]
            remaining_capacity = self.num_wavelengths - np.sum(usage)
            state_components.extend([remaining_capacity])

        if self.current_service_request:
            state_components.extend([
                self.current_service_request['source'],
                self.current_service_request['destination'],
                self.current_service_request['demand']
            ])
        else:
            state_components.extend([0, 0, 0])
        return np.array(state_components).flatten()

    def get_next_service_request(self):
        self.current_service_request = self.traffic_generator.generate_request(
            self.nodes)
        if self.current_service_request:
            source = self.current_service_request['source']
            destination = self.current_service_request['destination']
            self.current_service_request['path'] = self._shortest_path(
                source, destination)
        return self.current_service_request

    def _is_wavelength_available(self, path, wavelength_index):
        for edge in path:
            if self.wavelength_usage[edge][wavelength_index] == 1:
                return False
        return True

    def _assign_wavelength(self, path, wavelength_index):
        for edge in path:
            self.wavelength_usage[edge][wavelength_index] = 1

    def _shortest_path(self, source, destination):
        """
        Return:
            list: list of edges
            None: Neu khong ton tai duong di
        """
        distances = {node: float('inf') for node in self.nodes}
        previous_nodes = {node: None for node in self.nodes}
        distances[source] = 0
        unvisited_nodes = set(self.nodes)

        while unvisited_nodes:
            current_node = min(
                unvisited_nodes, key=lambda node: distances[node])
            unvisited_nodes.remove(current_node)

            if distances[current_node] == float('inf'):
                break

            if current_node == destination:
                break

            for neighbor in self.adjacency_list[current_node]:
                weight = 1
                distance = distances[current_node] + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node

        path_edges = []
        current = destination
        while current != source and current is not None:
            prev_node = previous_nodes[current]
            if prev_node is None:
                return None
            path_edges.insert(0, tuple(sorted((prev_node, current))))
            current = prev_node

        if current != source:
            return None

        return path_edges


if __name__ == '__main__':
    from environment.topology import create_nsfnet_topology
    from environment.traffic_generator import RandomTrafficGenerator

    test_topology_data = create_nsfnet_topology()
    test_num_wavelengths = 10
    test_traffic_generator = RandomTrafficGenerator(
        arrival_rate=0.5, duration_mean=5)

    env = EONEnvironment(test_topology_data,
                         test_num_wavelengths, test_traffic_generator)

    state = env.reset()
    print("Initial State:", state)

    request = env.get_next_service_request()
    if request:
        print("Service Request:", request)

        test_action = 0
        next_state, test_reward, test_done, test_info = env.step(test_action)
        print("Next State:", next_state)
        print("Reward:", test_reward)
        print("Done:", test_done)
        print("Info:", test_info)
    else:
        print("No service request generated.")
