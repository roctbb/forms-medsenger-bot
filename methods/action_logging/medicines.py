def log_medicine_action(action, contract, medicine):
    text = None
    params = None

    if action == "remove" or action == "detach":
        params = {
            'obj_id': medicine.id,
            'action': 'cancel',
            'object_type': 'medicine',
            'description': medicine.get_description(True, False)
        }

        text = 'Отменен препарат "{}".'.format(medicine.title)

    if action == "attach":
        params = {
            'obj_id': medicine.id,
            'action': 'attach',
            'object_type': 'medicine',
            'description': medicine.get_description(True, False)
        }

        text = 'Назначен препарат "{}".'.format(medicine.title)

    if action == "clear":
        params = {
            'action': 'clear',
            'object_type': 'medicine'
        }

        text = 'Отменены все лекарства.'

    if action == "resume":
        params = {
            'obj_id': medicine.id,
            'action': 'resume',
            'object_type': 'medicine',
            'description': medicine.get_description(True, False)
        }

        text = 'Возобновлен препарат "{}".'.format(medicine.title)

    if action == "create":
        params = {
            'obj_id': medicine.id,
            'action': 'create',
            'object_type': 'medicine',
            'description': medicine.get_description(True, False)
        }

        text = 'Назначен препарат "{}".'.format(medicine.title)

    if action == "edit":
        params = {
            'obj_id': medicine.id,
            'action': 'edit',
            'object_type': 'medicine',
            'description': medicine.get_description(True, False)
        }

        text = 'Изменены параметры приема препарата "{}".'.format(medicine.title)

    return text, params