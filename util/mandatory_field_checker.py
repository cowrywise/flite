def check_request_payload(payload, mandatory_field):
    try:
        obj_check = []
        for obj in payload:
            obj_check.append(obj)
        missing_fields = set(mandatory_field) - set(obj_check)
        if missing_fields:
            return missing_fields
        return True
    except Exception as e:
        print("Error at check_request_payload: ", str(e))
        return False


def check_empty_string(payload):
    try:
        obj_check = []
        # print(payload)
        for obj in payload:
            # print(str(obj))
            if len(payload[obj]) == 0:
                obj_check.append(str(obj))
        if obj_check:
            return obj_check
        return True

    except Exception as e:
        print("Error at check_empty_string: ", str(e))
        return False
