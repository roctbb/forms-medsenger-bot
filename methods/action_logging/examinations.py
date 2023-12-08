def log_examination_action(action, contract, object=None):
    text = None
    params = None

    if action == "remove" or action == "detach":
        params = {
            'obj_id': object.id,
            'action': action,
            'object_type': 'examination',
            'description': object.doctor_description
        }

        text = 'Отмено исследование "{}".'.format(object.title)

    if action == "attach":
        params = {
            'obj_id': object.id,
            'action': 'attach',
            'object_type': 'examination',
            'description': object.doctor_description
        }

        text = 'Назначено исследование "{}"'.format(object.title)

    if action == "create":
        params = {
            'obj_id': object.id,
            'action': 'attach',
            'object_type': 'examination',
            'description': object.doctor_description
        }

        text = 'Назначено исследование "{}"'.format(object.title)

    if action == "edit":
        params = {
            'obj_id': object.id,
            'action': 'attach',
            'object_type': 'examination',
            'description': object.doctor_description
        }

        text = 'Изменены параметры обследования "{}"'.format(object.title)

    if action == "clear":
        params = {
            'action': 'clear',
            'object_type': 'examination'
        }

        text = 'Отменены все исследования.'

    return text, params
