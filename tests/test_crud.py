from jibb import JibbStore, Task, TaskStatus


def test_task_ids_are_stable(tmp_path):
    store = JibbStore(tmp_path / "jibb.db")
    first = store.add_task("Alpha", Task("One"))
    second = store.add_task("Alpha", Task("Two"))
    project = store.load_project("Alpha")
    assert [task.id for task in project.tasks] == [first, second]


def test_update_and_complete_task(tmp_path):
    store = JibbStore(tmp_path / "jibb.db")
    task_id = store.add_task("Alpha", Task("Ship", priority=3))
    store.update_task(task_id, priority=1, owner="team")
    store.complete_task(task_id)
    task = store.load_project("Alpha").task(task_id)
    assert task.priority == 1
    assert task.owner == "team"
    assert task.status is TaskStatus.DONE


def test_delete_task(tmp_path):
    store = JibbStore(tmp_path / "jibb.db")
    task_id = store.add_task("Alpha", Task("Temporary"))
    store.delete_task(task_id)
    assert store.load_project("Alpha").tasks == []
