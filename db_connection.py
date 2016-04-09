import boto3
from boto3.dynamodb.conditions import Key, Attr

class DBWaypoint:
    def __init__(self, node_id, name, connection_ids):
        self.node_id = node_id
        self.name = name
        self.connection_ids = connection_ids

class Database:
    def __init__(self):
        self.dynamo = boto3.resource(
                'dynamodb'
                #endpoint_url="http://localhost:8000"
        )
        self.waypoints_table = self.dynamo.Table('Localization')
        self.device_table = self.dynamo.Table('Device')
        self.cache = self.get_whole_fucking_graph()

    def get_whole_fucking_graph(self):
        """Returns an list object of the whole graph of waypoints"""
        response = self.waypoints_table.scan()

        results = []
        for item in response['Items']:
            results.append(self._item_to_waypoint(item))

        return results

    def waypoint_by_name(self, name):
        needle = name.lower()
        for waypoint in self.cache:
            if needle in waypoint.name.lower():
                return waypoint
        return None

    def waypoint_by_id(self, node_id):
        for waypoint in self.cache:
            if waypoint.node_id == node_id:
                return waypoint
        return None

    def set_device_waypoint(self, waypoint):
        self.device_table.update_item(
                Key=dict(device='main'),
                UpdateExpression='SET node_id = :val1',
                ExpressionAttributeValues={ ':val1': waypoint.node_id }
        )

    def get_device_waypoint(self):
        response = self.device_table.get_item(Key=dict(device='main'))
        item = response['Item']
        return self.waypoint_by_id(item[u'node_id'])

    def _item_to_waypoint(self, item):
        return DBWaypoint(item['node_id'], item['description'], list(item['connections']))
