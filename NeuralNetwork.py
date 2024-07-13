import math
import random 

class Connection:
    def __init__(self, from_node, to_node, weight):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight

    def mutate_weight(self):
        # big change
        if random.uniform(0,1 ) > 0.9:
            self.weight = random.uniform(-1,1)
        else: # small change
            self.weight += random.gauss(0,1)/10
            if self.weight > 1:
                self.weight = 1
            elif self.weight < -1:
                self.weight = -1

            
    def clone(self, from_node, to_node):
        clone = Connection(from_node, to_node, self.weight)

        return clone

class Node:

    def __init__(self, id):
        self.id = id
        self.layer = 0
        self.input_value = 0
        self.output_value = 0 
        self.connections = []

    def activate(self):
        def sigmoid(x):
            return 1/(1+math.exp(-x))

        if self.layer == 1:
            self.output_value = sigmoid(self.input_value)

        for i in range(len(self.connections)):
            self.connections[i].to_node.input_value += self.connections[i].weight * self.output_value 

    def clone(self):
        clone = Node(self.id)
        clone.id = self.id # already doing that?
        clone.layer = self.layer

        return clone 

class NeuralNetwork:

    def __init__(self, inputs, clone=False):
        self.connections = []
        self.nodes = []
        self.inputs = inputs
        self.net = []
        self.layers = 2

        # Create input nodes

        if not clone:
            for i in range(0, self.inputs):
                self.nodes.append(Node(i))
                self.nodes[i].layer = 0

            # Create bias node
            # self.inputs = 3 
            self.nodes.append(Node(self.inputs))
            self.nodes[self.inputs].layer = 0

            # Create output node
            self.nodes.append(Node(self.inputs+1))
            self.nodes[self.inputs+1].layer = 1

            # Creating connections

            for i in range(0,4):
                # starting out with random weights
                self.connections.append(Connection(self.nodes[i], self.nodes[self.inputs+1], random.uniform(-1,1))) 

    # ?
    def connect_nodes(self):
        for i in range(0, len(self.nodes)):
            self.nodes[i].connections = []

        for i in range(0, len(self.connections)):
            self.connections[i].from_node.connections.append(self.connections[i])

    # Generates the list of all neural networks
    def generate_net(self):
        self.connect_nodes()
        self.net = []

        # adds nodes to the net list acc to their layer
        for j in range(self.layers):
            for i in range(len(self.nodes)):
                if self.nodes[i].layer == j:
                    self.net.append(self.nodes[i])

    def feed_forward(self, vision):

        # ?
        for i in range(self.inputs):
            self.nodes[i].output_value = vision[i]

        # bias node remains 1
        self.nodes[3].output_value = 1

        # makes 2nd layer?
        for i in range(len(self.net)):
            self.net[i].activate()

        # Get the output value from the output node
        output_value = self.nodes[4].output_value

        # Reset all the node input values
        for i in range(0, len(self.nodes)):
            self.nodes[i].input_value = 0

        return output_value
    

    def clone(self):
        clone = NeuralNetwork(self.inputs, True)

       # Clone all the nodes
        for n in self.nodes:
            clone.nodes.append(n.clone())

        # Clone all connections
        for c in self.connections:
            clone.connections.append(c.clone(clone.getNode(c.from_node.id), clone.getNode(c.to_node.id)))

        clone.layers = self.layers
        clone.connect_nodes()

        return clone
    
    def getNode(self, id):
        for n in self.nodes:
            if n.id == id:
                return n
            
    def mutate(self):
        if random.uniform(0,1) > 0.8:
            for i in range(len(self.connections)):
                self.connections[i].mutate_weight()

    


    
    

        





