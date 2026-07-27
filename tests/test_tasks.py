from datetime import date, timedelta

PAST = str(date.today() - timedelta(days=3))
FUTURE = str(date.today() + timedelta(days=7))


# POST /tasks
def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post("/tasks", json={"title": "Test task"})
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "Test task"
    assert body["description"] == ""
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["assignee"] is None
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": " "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "X", "priority": "Bogus"})
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "X", "unknown": "field"})
    assert response.status_code == 422


# GET /tasks
def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "low task", "priority": "Low"})
    client.post("/tasks", json={"title": "high task", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "high task"
    assert body[0]["priority"] == "High"


# GET /tasks/{id}
def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "fixture task"


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id does-not-exist not found"


# PATCH /tasks/{id}
def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"description": "updated"})
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "updated"
    assert body["title"] == "fixture task"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/does-not-exist", json={"description": "x"})
    assert response.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert response.status_code == 422


# DELETE /tasks/{id}
def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/does-not-exist")
    assert response.status_code == 404


def test_delete_then_get_returns_404(client, created_task):
    task_id = created_task["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


# ---------------------------------------------------------------------------
# Edge cases: creation
# ---------------------------------------------------------------------------
def test_create_with_all_fields(client):
    response = client.post("/tasks", json={
        "title": "full",
        "description": "details",
        "status": "InProgress",
        "priority": "High",
        "assignee": "wadih",
    })
    assert response.status_code == 201
    body = response.json()
    assert body["description"] == "details"
    assert body["status"] == "InProgress"
    assert body["priority"] == "High"
    assert body["assignee"] == "wadih"


def test_create_with_status_done_is_allowed(client):
    # Creation sets status directly and does NOT run transition validation.
    response = client.post("/tasks", json={"title": "born done", "status": "Done"})
    assert response.status_code == 201
    assert response.json()["status"] == "Done"


def test_create_invalid_status_returns_422(client):
    response = client.post("/tasks", json={"title": "x", "status": "Nope"})
    assert response.status_code == 422


def test_create_title_is_trimmed(client):
    response = client.post("/tasks", json={"title": "  hello  "})
    assert response.status_code == 201
    assert response.json()["title"] == "hello"


def test_create_title_max_length_200_ok(client):
    response = client.post("/tasks", json={"title": "x" * 200})
    assert response.status_code == 201


def test_create_title_over_200_returns_422(client):
    response = client.post("/tasks", json={"title": "x" * 201})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Edge cases: status transitions (Done is now terminal)
# ---------------------------------------------------------------------------
def test_patch_valid_transition_inprogress_to_done_returns_200(client, created_task):
    task_id = created_task["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert response.status_code == 200
    assert response.json()["status"] == "Done"


def test_full_lifecycle_todo_to_done(client, created_task):
    task_id = created_task["id"]
    assert client.patch(f"/tasks/{task_id}", json={"status": "InProgress"}).status_code == 200
    assert client.patch(f"/tasks/{task_id}", json={"status": "Done"}).status_code == 200


def test_patch_done_to_inprogress_returns_422(client):
    # New rule: Done is terminal, reopening is not allowed.
    task_id = client.post("/tasks", json={"title": "d", "status": "Done"}).json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert response.status_code == 422


def test_patch_done_to_todo_returns_422(client):
    task_id = client.post("/tasks", json={"title": "d", "status": "Done"}).json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_patch_inprogress_to_todo_returns_422(client, created_task):
    task_id = created_task["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_invalid_transition_detail_mentions_reason(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Edge cases: partial updates
# ---------------------------------------------------------------------------
def test_patch_empty_body_returns_200_unchanged(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == "fixture task"


def test_patch_blank_title_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "   "})
    assert response.status_code == 422


def test_patch_title_is_trimmed(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "  spaced  "})
    assert response.status_code == 200
    assert response.json()["title"] == "spaced"


def test_patch_unknown_field_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"bogus": 1})
    assert response.status_code == 422


def test_patch_updates_assignee_and_priority(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"assignee": "sam", "priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert body["assignee"] == "sam"
    assert body["priority"] == "High"


def test_patch_preserves_created_at(client, created_task):
    task_id = created_task["id"]
    created_at = created_task["created_at"]
    body = client.patch(f"/tasks/{task_id}", json={"description": "x"}).json()
    assert body["created_at"] == created_at
    assert body["updated_at"] >= created_at


# ---------------------------------------------------------------------------
# Edge cases: listing & id generation
# ---------------------------------------------------------------------------
def test_list_filter_by_status_and_priority_combined(client):
    client.post("/tasks", json={"title": "a", "priority": "High"})                      # ToDo/High
    client.post("/tasks", json={"title": "b", "priority": "Low"})                       # ToDo/Low
    client.post("/tasks", json={"title": "c", "priority": "High", "status": "InProgress"})
    response = client.get("/tasks", params={"status": "ToDo", "priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "a"


def test_list_returns_creation_order(client):
    client.post("/tasks", json={"title": "first"})
    client.post("/tasks", json={"title": "second"})
    titles = [t["title"] for t in client.get("/tasks").json()]
    assert titles == ["first", "second"]


def test_ids_do_not_recycle_after_delete(client):
    ids = [client.post("/tasks", json={"title": f"t{i}"}).json()["id"] for i in range(3)]
    assert client.delete(f"/tasks/{ids[1]}").status_code == 204  # delete the middle one

    new_id = client.post("/tasks", json={"title": "new"}).json()["id"]
    assert new_id not in ids  # must not collide with an existing id

    # Surviving originals are intact (not overwritten by a recycled id).
    assert client.get(f"/tasks/{ids[0]}").json()["title"] == "t0"
    assert client.get(f"/tasks/{ids[2]}").json()["title"] == "t2"
    assert len(client.get("/tasks").json()) == 3


# ===========================================================================
# Feature 1: due dates + overdue
# ===========================================================================
def test_create_with_valid_due_date(client):
    response = client.post("/tasks", json={"title": "d", "due_date": FUTURE})
    assert response.status_code == 201
    assert response.json()["due_date"] == FUTURE


def test_create_with_invalid_due_date_format_returns_422(client):
    response = client.post("/tasks", json={"title": "d", "due_date": "31-12-2026"})
    assert response.status_code == 422


def test_create_with_impossible_calendar_date_returns_422(client):
    response = client.post("/tasks", json={"title": "d", "due_date": "2026-13-40"})
    assert response.status_code == 422


def test_due_date_defaults_to_null_and_not_overdue(client, created_task):
    assert created_task["due_date"] is None
    assert created_task["overdue"] is False


def test_past_due_date_is_overdue(client):
    body = client.post("/tasks", json={"title": "late", "due_date": PAST}).json()
    assert body["overdue"] is True


def test_future_due_date_is_not_overdue(client):
    body = client.post("/tasks", json={"title": "soon", "due_date": FUTURE}).json()
    assert body["overdue"] is False


def test_done_task_with_past_due_is_not_overdue(client):
    # A completed task is never "overdue" even if its due date has passed.
    body = client.post("/tasks", json={"title": "done", "status": "Done", "due_date": PAST}).json()
    assert body["overdue"] is False


def test_update_due_date(client, created_task):
    task_id = created_task["id"]
    body = client.patch(f"/tasks/{task_id}", json={"due_date": PAST}).json()
    assert body["due_date"] == PAST
    assert body["overdue"] is True


def test_clear_due_date_with_null(client):
    task_id = client.post("/tasks", json={"title": "x", "due_date": PAST}).json()["id"]
    body = client.patch(f"/tasks/{task_id}", json={"due_date": None}).json()
    assert body["due_date"] is None
    assert body["overdue"] is False


def test_overdue_filter_returns_only_overdue_tasks(client):
    client.post("/tasks", json={"title": "late", "due_date": PAST})
    client.post("/tasks", json={"title": "soon", "due_date": FUTURE})
    client.post("/tasks", json={"title": "no-date"})
    client.post("/tasks", json={"title": "done-late", "status": "Done", "due_date": PAST})

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["late"]


def test_overdue_false_filter_excludes_overdue(client):
    client.post("/tasks", json={"title": "late", "due_date": PAST})
    client.post("/tasks", json={"title": "soon", "due_date": FUTURE})
    titles = [t["title"] for t in client.get("/tasks", params={"overdue": "false"}).json()]
    assert "late" not in titles
    assert "soon" in titles


# ===========================================================================
# Feature 2: tags / labels
# ===========================================================================
def test_create_with_tags(client):
    body = client.post("/tasks", json={"title": "t", "tags": ["bug", "urgent"]}).json()
    assert body["tags"] == ["bug", "urgent"]


def test_tags_default_to_empty_list(client, created_task):
    assert created_task["tags"] == []


def test_create_with_blank_tag_returns_422(client):
    response = client.post("/tasks", json={"title": "t", "tags": ["ok", "   "]})
    assert response.status_code == 422


def test_tags_are_trimmed_and_deduped(client):
    body = client.post("/tasks", json={"title": "t", "tags": ["  bug ", "bug", "ux"]}).json()
    assert body["tags"] == ["bug", "ux"]


def test_too_many_tags_returns_422(client):
    response = client.post("/tasks", json={"title": "t", "tags": [f"t{i}" for i in range(11)]})
    assert response.status_code == 422


def test_too_long_tag_returns_422(client):
    response = client.post("/tasks", json={"title": "t", "tags": ["x" * 31]})
    assert response.status_code == 422


def test_update_tags(client, created_task):
    task_id = created_task["id"]
    body = client.patch(f"/tasks/{task_id}", json={"tags": ["new"]}).json()
    assert body["tags"] == ["new"]


def test_filter_by_tag_is_case_insensitive(client):
    client.post("/tasks", json={"title": "a", "tags": ["Backend"]})
    client.post("/tasks", json={"title": "b", "tags": ["frontend"]})
    titles = [t["title"] for t in client.get("/tasks", params={"tag": "backend"}).json()]
    assert titles == ["a"]


def test_filter_by_tag_no_match_returns_empty_list(client):
    client.post("/tasks", json={"title": "a", "tags": ["backend"]})
    response = client.get("/tasks", params={"tag": "nonexistent"})
    assert response.status_code == 200
    assert response.json() == []


def test_tags_preserved_after_unrelated_update(client):
    task_id = client.post("/tasks", json={"title": "a", "tags": ["keep"]}).json()["id"]
    body = client.patch(f"/tasks/{task_id}", json={"description": "changed"}).json()
    assert body["tags"] == ["keep"]
