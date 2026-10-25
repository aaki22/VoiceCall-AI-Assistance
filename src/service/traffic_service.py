from src.tools.traffic_tool import TrafficTool


class TrafficService:
    def __init__(self, traffic_tool: TrafficTool):
        self._traffic_tool = traffic_tool

    def get_traffic_time(self, start_place: str, end_place: str) -> str:
        return self._traffic_tool.get_traffic_time(start_place, end_place)
