import inspect


class ReviewerMixin:
    @classmethod
    def run_checks(cls, **kwarg):
        application = cls(**kwarg)
        functions = inspect.getmembers(cls, inspect.isfunction)
        checks = [
            func for func_name, func in functions if func_name.startswith("check")
        ]
        checks.reverse()
        for check in checks:
            application_check = check(application)
            if application_check.get("success") is False:
                return {"success": False, "message": application_check.get("message")}
        return {"success": True, "message": "checks successful"}
