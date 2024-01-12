

def get_signs():
    return {
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


def get_left_modes():
    return {
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


def get_right_modes():
    return {
        "sum": "сумме",
        "difference": "разности крайних значений",
        "delta": "разбросу",
        "count": "количеству значений",
        "average": "среднему значению",
        "max": "максимальному значению",
        "min": "минимальному значению"
    }


def dimensions():
    return {
        "times": "раз",
        "hours": "часов",
        "days": "дней"
    }


def generate_event_description(criteria, l_value, r_value, category_names, current_answer):
    try:
        if (criteria.get('left_mode') == 'value' and criteria.get('right_mode') == 'value'
                and criteria.get('sign') in ['equal', 'contains'] and current_answer):
            if not current_answer.get('params', {}).get('type'):
                return ""
            return current_answer['value'] + "."

        LEFT_MODE = get_left_modes().get(criteria.get('left_mode'))
        LEFT_CATEGORY = category_names.get(criteria.get('category'))
        SIGN = get_signs()[criteria.get('sign')]

        if criteria.get('sign') not in ['equal', 'contains'] or criteria.get('left_mode') != 'value':
            comment = "{} '{}' (<strong>{}</strong>) {} ".format(LEFT_MODE, LEFT_CATEGORY, l_value, SIGN)
        else:
            comment = "{} '{}' {} ".format(LEFT_MODE, LEFT_CATEGORY, SIGN)

        if criteria.get('right_mode') in ['value', 'category_value']:
            comment += "<strong>{}</strong>".format(criteria.get('value'))
        else:
            right_key = 'right_hours' if criteria.get('right_dimension') == "hours" else 'right_times'

            comment += "{} за {} {} (<strong>{}</strong>)".format(
                get_right_modes()[criteria.get('right_mode')], criteria.get(right_key),
                dimensions()[criteria.get('right_dimension')], r_value)

            if criteria.get('right_offset') and criteria.get('right_offset_dimension'):
                comment += "с отступом в {} {}".format(criteria.get('right_offset'),
                                                       dimensions()[criteria.get('right_offset_dimension')])

            if criteria.get('right_category'):
                comment += " '{}'".format(category_names.get(criteria.get('right_category')))

        return comment
    except Exception as e:
        from helpers import log
        log(e, False)
        return ""


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
