from tasks import threader


def log_action(object_type, action, contract, objects=None):
    text = None
    params = None

    if objects:
        if object_type == "algorithm":
            if action == "detach":
                params = {
                    'obj_id': list(map(lambda a: a.id, objects)),
                    'action': 'detach',
                    'object_type': 'algorithm',
                    'algorithm_title': objects[0].title
                }

                text = f'Отключен алгоритм "{objects[0].title}"'

            if action == "remove":
                params = {
                    'obj_id': objects.id,
                    'action': 'detach',
                    'object_type': 'algorithm'
                }

                text = 'Отключен алгоритм "{}".'.format(objects.title)

            if action == "attach":
                params = {
                    'obj_id': objects.id,
                    'action': 'attach',
                    'object_type': 'algorithm',
                    'params': objects.get_params()
                }

                text = 'Подключен алгоритм "{}"'.format(objects.title)

            if action == "clear":
                params = {
                    'action': 'clear',
                    'object_type': 'algorithm'
                }

                text = 'Отключены все алгоритмы.'

    if text and params:
        threader.async_record.delay(contract.id, 'doctor_action', text, params=params)
