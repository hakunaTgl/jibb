from jibb import Project, Task, TaskStatus
from jibb.storage import JibbStore


def test_store_round_trip(tmp_path):
    store = JibbStore(tmp_path / "jibb.db")
    project = Project("Alpha")
    project.add(Task("Ship", owner="Tyler", status=TaskStatus.IN_PROGRESS, priority=1))

    store.save_project(project)
    loaded = store.load_project("Alpha")

    assert loaded.name == "Alpha"
    assert len(loaded.tasks) == 1
    assert loaded.tasks[0].title == "Ship"
    assert loaded.tasks[0].owner == "Tyler"
    assert loaded.tasks[0].status is TaskStatus.IN_PROGRESS


def test_list_projects(tmp_path):
    store = JibbStore(tmp_path / "jibb.db")
    store.save_project(Project("Beta"))
    store.save_project(Project("Alpha"))
    assert store.list_projects() == ["Alpha", "Beta"]
