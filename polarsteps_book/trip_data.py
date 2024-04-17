import json
import os
from abc import ABC, abstractmethod
from typing import List, NamedTuple, Optional, TypedDict


class Step(TypedDict):
    display_name: str
    description: str
    photo_paths: Optional[List[str]]


class Locations(NamedTuple):
    lon: list[float]
    lat: list[float]


class TripData(ABC):
    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def locations(self) -> Optional[Locations]: ...

    @property
    @abstractmethod
    def steps(self) -> List[Step]: ...


class PolarStepsData(TripData):
    def __init__(self, path: str, title: str = None):
        self.path = path
        self._title = title if title else self.path.split("/")[-2].title()
        self.create_locations()
        self.create_steps()

    @property
    def title(self) -> str:
        return self._title

    @property
    def locations(self) -> Optional[Locations]:
        return self._locations

    @property
    def steps(self) -> List[Step]:
        return self._steps

    def create_locations(self):
        data = json.load(open(f"{self.path}locations.json"))
        lon = [loc["lon"] for loc in data["locations"]]
        lat = [loc["lat"] for loc in data["locations"]]
        self._locations = Locations(lon, lat)

    def create_steps(self):
        regions = [r for r in os.listdir(self.path) if os.path.isdir(self.path + r)]
        regions.sort(key=lambda x: x.split("_")[1])
        polar_steps = json.load(open(f"{self.path}/trip.json"))["all_steps"]

        steps = []
        id = 1
        for ps in polar_steps:
            assert ps["id"] > id
            id = ps["id"]
            step: Step = {
                "display_name": ps["display_name"],
                "description": ps["description"],
                "photo_paths": None,
            }

            for r in regions:
                if r.split("_")[1] == str(id):
                    photo_dir = f"{self.path}/{r}/photos/"
                    step["photo_paths"] = [photo_dir + f for f in os.listdir(photo_dir)]
                    regions.remove(r)
                    break

            steps.append(step)
        assert not regions, f"`regions` should be empty, not {regions}"
        self._steps = steps


class CustomData(TripData):
    def __init__(self, title: str, locations: Optional[Locations], steps: List[Step]):
        self._title = title
        self._locations = locations
        self._steps = steps

    @property
    def title(self) -> str:
        return self._title

    @property
    def locations(self) -> Optional[Locations]:
        return self._locations

    @property
    def steps(self) -> List[Step]:
        return self._steps
