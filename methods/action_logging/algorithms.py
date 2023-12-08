def log_algorithm_action(action, contract, object=None):
    text = None
    params = None

    if action == "detach" or action == "remove":
        params = {
            'obj_id': object.id,
            'action': 'detach',
            'object_type': 'algorithm',
            'algorithm_title': object.title
        }

        text = 'Отключен алгоритм "{}".'.format(object.title)

    if action == "attach" or action == 'create':
        params = {
            'obj_id': object.id,
            'action': 'attach',
            'object_type': 'algorithm',
            'params': object.get_params()
        }

        text = 'Подключен алгоритм "{}"'.format(object.title)

    if action == "edit":
        params = {
            'obj_id': object.id,
            'action': 'attach',
            'object_type': 'algorithm',
            'params': object.get_params()
        }

        text = 'Изменен алгоритм "{}"'.format(object.title)

    if action == "clear":
        params = {
            'action': 'clear',
            'object_type': 'algorithm'
        }

        text = 'Отключены все алгоритмы.'

    return text, params