def log_form_action(action, contract, form):
    text = None
    params = None

    if action == "remove" or action == "detach":
        params = {
            'obj_id': form.id,
            'action': 'delete',
            'object_type': 'form',
            'description': form.doctor_description
        }

        text = 'Отменен опросник "{}".'.format(form.title)

    if action == "attach":
        params = {
            'obj_id': form.id,
            'action': 'attach',
            'object_type': 'form',
            'description': form.doctor_description,
            'template_id': form.template_id
        }

        text = 'Назначен опросник "{}".'.format(form.title)

    if action == "clear":
        params = {
            'action': 'clear',
            'object_type': 'form'
        }

        text = 'Отключены все опросники.'

    if action == "create":
        params = {
            'obj_id': form.id,
            'action': 'create',
            'object_type': 'form',
            'description': form.doctor_description
        }

        text = 'Назначен опросник "{}".'.format(form.title)

    if action == "edit":
        params = {
            'obj_id': form.id,
            'action': 'create',
            'object_type': 'form',
            'description': form.doctor_description
        }

        text = 'Изменен опросник "{}".'.format(form.title)

    return text, params