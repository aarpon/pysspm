from pysspm.lib.project_status import ProjectStatus


def test_project_status():

    p = ProjectStatus.new
    assert p == "new"
    assert ProjectStatus.new == ProjectStatus("new")
    assert p.is_open()

    p = ProjectStatus.feedback
    assert p == "feedback"
    assert ProjectStatus.feedback == ProjectStatus("feedback")
    assert p.is_open()

    p = ProjectStatus.in_progress
    assert p == "in progress"
    assert ProjectStatus.in_progress == ProjectStatus("in progress")
    assert p.is_open()

    p = ProjectStatus.waiting_for_data
    assert p == "waiting for data"
    assert ProjectStatus.waiting_for_data == ProjectStatus("waiting for data")
    assert p.is_open()

    p = ProjectStatus.superseded
    assert p == "superseded"
    assert ProjectStatus.superseded == ProjectStatus("superseded")
    assert not p.is_open()

    p = ProjectStatus.dropped
    assert p == "dropped"
    assert ProjectStatus.dropped == ProjectStatus("dropped")
    assert not p.is_open()

    p = ProjectStatus.completed
    assert p == "completed"
    assert ProjectStatus.completed == ProjectStatus("completed")
    assert not p.is_open()
