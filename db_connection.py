class DBWaypoint:
    def __init__(self, node_id, name, connection_ids):
        self.node_id = node_id
        self.name = name
        self.connection_ids = connection_ids

class Database:
    def __init__(self):
        pass

    def get_whole_fucking_graph(self):
        """Returns an list object of the whole graph of waypoints"""
        pass

    def waypoint_by_name(self, name):
        pass

    def waypoint_by_id(self, node_id):
        pass

    def set_device_waypoint(self, waypoint):
        pass

    def get_device_waypoint(self):
        pass
