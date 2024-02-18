from typing import Optional, List, TypedDict
import os
from abc import ABC, abstractmethod
import json
import pandas as pd


class Step(TypedDict):
    display_name: str
    description: str
    photo_paths: List[str]


class TripData(ABC):
    @property
    @abstractmethod
    def title(self) -> str:
        ...

    @property
    @abstractmethod
    def locations(self) -> Optional[pd.DataFrame]:
        ...

    @property
    @abstractmethod
    def steps(self) -> List[Step]:
        ...


class PolarStepsData(TripData):
    def __init__(self, path: str, title: str = None):
        self.create_steps(path)
        self._title = title if title else path.split("/")[-1]

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def locations(self) -> Optional[pd.DataFrame]:
        return self._locations
    
    @property
    def steps(self) -> List[Step]:
        return self._steps

    def create_steps(self, path):
        regions = [r for r in os.listdir(path) if os.path.isdir(path+r)]
        regions.sort(key=lambda x: x.split("_")[1])

        polar_steps = json.load(open(f"{path}/trip.json"))["all_steps"]
        steps = []
        for cnt, r in enumerate(regions):
            if os.path.isdir(path):
                photo_dir = f"{path}/{r}/photos/"

                polar_step=polar_steps[cnt]
                assert str(polar_step["id"]) == r.split("_")[1], f"{str(polar_step["id"])} should be equal to {r.split("_")[1]}"
                
                step: Step = {
                    "display_name": polar_step["display_name"], 
                    "description": polar_step["description"], 
                    "photo_paths": [photo_dir+f for f in os.listdir(photo_dir)],
                }
                steps.append(step)

        self._steps = steps


class CustomData(TripData):
    def __init__(self, title: str, locations: Optional[pd.DataFrame], steps: List[Step]):
        self._title = title
        self._locations = locations
        self._steps = steps
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def locations(self) -> Optional[pd.DataFrame]:
        return self._locations
    
    @property
    def steps(self) -> List[Step]:
        return self._steps
