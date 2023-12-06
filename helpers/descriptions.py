def generate_event_description(criteria, l_value, r_value, category_names, current_answer):
    if criteria.get('left_mode') == 'value' and criteria.get('right_mode') == 'value' and criteria.get('sign') in [
        'equal', 'contains'] and current_answer:
        if not current_answer.get('params', {}).get('type'):
            return ""

        return current_answer['value'] + "."

    signs = {
        "equal": "равно",
        "not_equal": "не равно",
        "greater": "больше",
        "less": "меньше",
        "greater_or_equal": "больше или равно",
        "less_or_equal": "меньше или равно",
        "contains": "содержит",
        "date_equal": "равно",
        "date_not_equal": "не равно",
        "date_greater": "больше",
        "date_less": "меньше",
        "date_greater_or_equal": "больше или равно",
        "date_less_or_equal": "меньше или равно",
    }

    left_modes = {
        "value": "Значение ",
        "category_value": "Значение ",
        "sum": "Сумма ",
        "difference": "Разность крайних значений ",
        "delta": "Разброс ",
        "average": "Среднее значение ",
        "count": "Количество значений ",
        "max": "Максимальному значение ",
        "min": "Минимальное значение "
    }

    right_modes = {
        "sum": "сумме",
        "difference": "разности крайних значений",
        "delta": "разбросу",
        "count": "количеству значений",
        "average": "среднему значению",
        "max": "максимальному значению",
        "min": "минимальному значению"
    }

    LEFT_MODE = left_modes.get(criteria.get('left_mode'))
    LEFT_CATEGORY = category_names.get(criteria.get('category'))
    SIGN = signs[criteria.get('sign')]

    if criteria.get('sign') not in ['equal', 'contains'] or criteria.get('left_mode') != 'value':
        comment = "{} '{}' (<strong>{}</strong>) {} ".format(LEFT_MODE, LEFT_CATEGORY, l_value, SIGN)
    else:
        comment = "{} '{}' {} ".format(LEFT_MODE, LEFT_CATEGORY, SIGN)

    if criteria.get('right_mode') in ['value', 'category_value']:
        comment += "<strong>{}</strong>".format(criteria.get('value'))
    else:
        comment += "{} за {} часа (ов) (<strong>{}</strong>)".format(right_modes[criteria.get('right_mode')],
                                                                     criteria.get('right_hours'), r_value)

        if criteria.get('right_category'):
            comment += " '{}'".format(category_names.get(criteria.get('right_category')))

    return comment


def generate_contract_description(contract):
    description = ""

    if contract.forms:
        description += 'Назначены опросники:<br> - '
        description += '<br> - '.join(map(lambda x: x.get_description(), contract.forms))

        description += '<br><br>'
    else:
        description += 'Опросников пока не назначено. <br>'

    if contract.medicines:
        description += 'Назначены лекарства:<br> - '
        description += '<br> - '.join(map(lambda x: x.get_description(), contract.medicines))

        description += '<br>'
    else:
        description += 'Лекарств пока не назначено. '

    return description
