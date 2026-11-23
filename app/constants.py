class Category:
    today = "TODAY"
    in_plans = "IN PLANS"


class Status:
    in_process = "IN PROCESS"
    done = "DONE"
    blocked = "BLOCKED"


categories = Category()
statuses = Status()


DEFAULT_TITLE = "task title"
DEFAULT_DESCRIPTION = "task description"
DEFAULT_CATEGORY = categories.today
DEFAULT_STATUS = statuses.in_process
DEFAULT_DEADLINE = None
