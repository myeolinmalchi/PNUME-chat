import json

from db.models.universities import DepartmentModel, UniversityModel
from db.repositories.base import transaction
from db.repositories.university import UniversityRepository

URLs = {}

with open('urls/notices.json') as f:
    URLs = json.load(f)


@transaction()
def run():
    models = []
    for university, departments in URLs.items():
        departments = [
            DepartmentModel(name=department)
            for department in departments.keys()
        ]

        model = UniversityModel(name=university, departments=departments)
        models.append(model)

    repo = UniversityRepository()
    repo.create_all(models)


if __name__ == "__main__":
    run()
