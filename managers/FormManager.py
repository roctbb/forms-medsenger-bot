import json
import time
from copy import copy
from datetime import datetime

from methods import log_action
from tasks import threader
from config import DYNAMIC_CACHE
from helpers import log, clear_categories, gts
from managers.ContractsManager import ContractManager
from managers.MedicineManager import MedicineManager
from managers.Manager import Manager
from models import Patient, Contract, Form, ActionRequest
from helpers import generate_timetable


class FormManager(Manager):
    def __init__(self, *args):
        super(FormManager, self).__init__()

    def get(self, form_id):
        return Form.query.filter_by(id=form_id).first()

    def get_templates(self):
        return Form.query.filter_by(is_template=True).all()

    def clear(self, contract):
        Form.query.filter_by(contract_id=contract.id).delete()
        self.__commit__()
        log_action("form", "clear", contract)
        return True

    def remove(self, id, contract):

        form = Form.query.filter_by(id=id).first_or_404()

        if form.contract_id != contract.id and not contract.is_admin:
            return None

        Form.query.filter_by(id=id).delete()

        self.__commit__()

        if not form.is_template:
            log_action("form", "remove", contract, form)

        return id

    def detach(self, template_id, contract):
        forms = list(filter(lambda x: x.template_id == template_id, contract.forms))

        for form in forms:
            log_action("form", "detach", contract, form)
            self.db.session.delete(form)

        self.__commit__()

    def attach(self, template_id, contract, custom_params=dict()):

        form = self.get(template_id)

        if form:
            new_form = form.clone()
            new_form.contract_id = contract.id
            new_form.patient_id = contract.patient.id

            if "times" in custom_params and custom_params.get('times', None) != None:
                try:
                    new_form.timetable = generate_timetable(9, 21, int(custom_params.get('times')))
                except Exception as e:
                    log(e, False)
            else:
                if "timetable" in custom_params and custom_params.get('timetable'):
                    try:
                        new_form.timetable = custom_params.get('timetable')
                    except Exception as e:
                        log(e, False)

            if "message" in custom_params and custom_params.get('message'):
                try:
                    new_form.custom_text = new_form.custom_text + "\n\n" + custom_params.get('message')
                except Exception as e:
                    log(e, False)


            if new_form.init_text:
                self.medsenger_api.send_message(new_form.contract_id, form.init_text, only_patient=True)

            self.db.session.add(new_form)
            self.__commit__()


            if new_form.timetable.get('send_on_init'):
                self.db.session.refresh(new_form)
                self.run(new_form)

            log_action("form", "attach", contract, new_form)

            return new_form
        else:
            return False

    def log_request(self, form, contract_id=None, description=None):
        if not contract_id:
            contract_id = form.contract_id
        if not description:
            description = "Заполнение опросника {}".format(form.title)

        super().log_request("form_{}".format(form.id), contract_id, description)

    def run(self, form, commit=True, contract_id=None):
        text = 'Пожалуйста, заполните опросник "{}".'.format(form.title)

        if form.custom_text:
            text = form.custom_text

        action = 'form/{}'.format(form.id)
        action_name = 'Заполнить опросник'

        if form.custom_title:
            action_name = form.custom_title

        if not contract_id:
            deadline = self.calculate_deadline(form)
            contract_id = form.contract_id
        else:
            deadline = None

        result = self.medsenger_api.send_message(contract_id, text, action, action_name, True, False, True, deadline)

        if result:
            form.last_sent = datetime.now()

            if not form.asked_timestamp:
                form.asked_timestamp = time.time()

            if commit:
                self.__commit__()

        return result

    def check_warning(self, form):
        if form.warning_days and form.warning_timestamp == 0 and form.asked_timestamp:
            if time.time() - form.asked_timestamp > 24 * 60 * 60 * form.warning_days:
                form.warning_timestamp = int(time.time())

                self.medsenger_api.send_message(form.contract_id,
                                                "Пациент не заполнял опросник {} уже {} дней.".format(form.title,
                                                                                                      form.warning_days),
                                                only_doctor=True, need_answer=False)
                self.__commit__()

    def __integral_result_report__(self, contract_id, form, integral_result):
        urgent = integral_result['params'].get('urgent', False)
        if not form.integral_evaluation.get('dont_send_to_doctor', False):
            text = '<strong>Результат интегральной оценки опросника "{}"</strong>:<br>{}'.format(form.title,
                                                                                                 integral_result[
                                                                                                     'result'])

            if form.integral_evaluation.get('groups_enabled'):
                text += '<br><br>Общая сумма баллов - {}<br><ul>'.format(integral_result['params']['score'])
                for group in integral_result['params']['group_scores'].keys():
                    text += '<li>{} - {}</li>'.format(group, integral_result['params']['group_scores'][group])
                text += '</ul>'
            elif integral_result['params'].get('group_scores'):
                text += '<br><ul>'
                for group in integral_result['params']['group_scores'].keys():
                    text += '<li>{} - {}</li>'.format(group, integral_result['params']['group_scores'][group])
                text += '</ul>'

            self.medsenger_api.send_message(contract_id, text, only_doctor=True, is_urgent=urgent)

        if integral_result['params'].get('message', None):
            self.medsenger_api.send_message(contract_id, integral_result['params'].get('message'), only_patient=True,
                                            is_urgent=urgent)
        elif urgent and form.integral_evaluation.get('warning_text'):
            self.medsenger_api.send_message(contract_id, form.integral_evaluation.get('warning_text'),
                                            only_patient=True, is_urgent=urgent)
        elif not urgent and form.integral_evaluation.get('ok_text'):
            self.medsenger_api.send_message(contract_id, form.integral_evaluation.get('ok_text'), only_patient=True,
                                            is_urgent=urgent)

    def __instant_report__(self, contract_id, form, report):
        text = 'Пациент заполнил опросник "{}" и дал следующие ответы.<br><br>'.format(form.title)
        text += '<ul>{}</ul>'.format(
            ''.join(list(map(lambda line: '<li><strong>{}</strong>: {};</li>'.format(*line), report))))

        deadline = time.time() + 1 * 60 * 60

        self.medsenger_api.send_message(contract_id, text, only_doctor=True)

        if not form.thanks_text:
            self.medsenger_api.send_message(contract_id,
                                            'Спасибо за заполнение опросника "{}". Ответы отправлены вашему лечащему врачу.'.format(
                                                form.title), only_patient=True, action_deadline=deadline)

    def _extract_packet_and_report_from_form(self, contract_id, form, answers):
        packet = []
        report = []

        medicine_manager = MedicineManager(self.medsenger_api, self.db)
        contract_manager = ContractManager(self.medsenger_api, self.db)
        contract = contract_manager.get(contract_id)

        for field in form.fields:
            if field['uid'] in answers.keys():
                if field['type'] == 'file':
                    category = field['category']
                    comment = field.get('category_value', answers[field['uid']].get('name'))

                    packet.append({"category_name": category, "value": comment, "files": [answers[field['uid']]]})

                    if field.get('params', {}).get('send_to_doctor'):
                        self.medsenger_api.send_message(contract_id, '', send_from='patient', need_answer=False,
                                                        attachments=[answers[field['uid']]])
                elif field['type'] == 'radio':
                    category = field['params']['variants'][answers[field['uid']]]['category']
                    answer = field['params']['variants'][answers[field['uid']]].get('text')
                    report.append((field.get('text'), answer))

                    if category == 'none':
                        continue

                    value = field['params']['variants'][answers[field['uid']]]['category_value']

                    params = {
                        "question_uid": field['uid'],
                        "question_text": field.get('text'),
                        "answer": answer,
                        "type": field['type']
                    }

                    if field['params']['variants'][answers[field['uid']]].get('custom_params'):
                        try:
                            params.update(
                                json.loads(field['params']['variants'][answers[field['uid']]].get('custom_params')))
                        except:
                            pass

                    packet.append((category, value, params))
                elif field['type'] == 'checkbox':

                    if not answers[field['uid']]:
                        continue

                    category = field['category']
                    value = field.get('category_value')
                    report.append((field.get('text'), 'Да'))

                    if category == 'none':
                        continue

                    if not value:
                        value = answers[field['uid']]

                    if category == 'none':
                        continue

                    params = {
                        "question_iud": field['uid'],
                        "question_text": field.get('text'),
                        "answer": value,
                        "type": field['type']
                    }

                    if field.get('params', {}).get('custom_params'):
                        try:
                            params.update(json.loads(field.get('params', {}).get('custom_params')))
                        except:
                            pass

                    packet.append((category, value, params))
                elif field['type'] == 'map':
                    category = field['category']
                    value = field.get('category_value', '') + ' ' + ', '.join(answers[field['uid']])
                    report.append((field.get('text'), value))

                    if category == 'none':
                        continue

                    params = {
                        "question_iud": field['uid'],
                        "question_text": field.get('text'),
                        "answer": answers[field['uid']],
                        "type": field['type'],
                        "map": field.get('params', {}).get('map')
                    }

                    if field.get('params', {}).get('custom_params'):
                        try:
                            params.update(json.loads(field.get('params', {}).get('custom_params')))
                        except:
                            pass

                    packet.append((category, value, params))
                elif field['type'] == 'medicine_list':
                    medicines = list(filter(lambda m: m['checked'] and m.get('title'), answers[field['uid']]))
                    answer = ', '.join([medicine['title'] + ' ({})'.format(medicine['dose']) if medicine['dose'] else ''
                                        for medicine in medicines])
                    report.append((field.get('text'), answer))

                    for medicine in medicines:
                        if not medicine.get('id'):
                            medicine_manager.create_or_edit(medicine, contract)
                        params = {
                            "question_iud": field['uid'],
                            "question_text": field.get('text'),
                            "answer": answer,
                            "type": field['type'],
                            "medicine_id": medicine.get('id'),
                            "dose": medicine.get('dose')
                        }
                        packet.append(('medicine', medicine['title'], params))
                else:
                    category = field['category']
                    report.append((field.get('text'), answers[field['uid']]))

                    if category == 'none':
                        continue

                    params = {
                        "question_uid": field['uid'],
                        "question_text": field.get('text'),
                        "answer": answers[field['uid']],
                        "type": field['type']
                    }

                    if field.get('params', {}).get('custom_params'):
                        try:
                            params.update(json.loads(field.get('params', {}).get('custom_params')))
                        except:
                            pass

                    if field['type'] == 'scale' and field.get('category_value'):
                        if not params.get('symptom_group'):
                            params.update({'symptom_group': field.get('category_value')})
                        max_value = max(
                            [(-1 if field['params'].get('reversed') else 1) * i + field['params']['start_from']
                             for i in range(len(field['params']['colors']))])
                        params.update({'color': abs(answers[field['uid']] - field['params']['start_from']) / max_value})
                        packet.append(
                            (category, "{} - {}".format(field.get('category_value'), answers[field['uid']]), params))
                    elif field['type'] in ['textarea', 'text'] and field.get('prefix'):
                        packet.append((category, "{}{}".format(field.get('prefix'), answers[field['uid']]), params))
                    else:
                        packet.append((category, answers[field['uid']], params))

        return packet, report

    def submit(self, answers, form, contract_id):
        form.warning_timestamp = 0
        form.asked_timestamp = 0
        form.filled_timestamp = int(time.time())

        self.__commit__()

        packet, report = self._extract_packet_and_report_from_form(contract_id, form, answers)

        action_name = 'Заполнение опросника ID {} "{}"'.format(form.template_id if form.template_id else form.id,
                                                               form.title)

        integral_result, integral_description, custom_params = self.get_integral_evaluation(contract_id, answers, form)
        action_name += integral_description

        custom_params['record_time'] = time.time()

        packet.append(('action', action_name, custom_params))

        params = {
            "form_id": form.id
        }

        timestamp = time.time()
        if 'timestamp' in answers:
            timestamp = answers['timestamp']

        if form.instant_report:
            self.__instant_report__(contract_id, form, report)

        if form.has_integral_evaluation and integral_result:
            integral_result = {'result': integral_result, 'params': custom_params}
            self.__integral_result_report__(contract_id, form, integral_result)

        result = bool(self.medsenger_api.add_records(contract_id, packet, params=params, record_time=timestamp))

        if result:
            self.log_done("form_{}".format(form.id), contract_id)

        return True

    def get_integral_evaluation(self, contract_id, answers, form):
        result = None
        action_name = ''
        custom_params = {}

        if not form.has_integral_evaluation:
            return result, action_name, custom_params

        score = 0
        group_scores = {}

        if form.integral_evaluation.get('groups_enabled'):
            for group in form.integral_evaluation['groups']:
                group_scores.update({group['description']: 0})

        questions = filter(lambda f: f['type'] != 'header', form.fields)

        for (i, question) in enumerate(questions, start=1):
            if question['uid'] in answers.keys() and not question.get('exclude_weight'):
                ans_score = 0

                if question['type'] == 'radio':
                    ans_score = question['params']['variants'][answers[question['uid']]]['weight']
                elif question['type'] == 'checkbox':
                    if answers[question['uid']]:
                        ans_score = question['weight']
                elif question['type'] == 'scale':
                    ans_score = answers[question['uid']]

                if form.integral_evaluation.get('script_enabled') and question.get('script_group'):
                    gr = question.get('script_group')
                    if gr in group_scores:
                        group_scores[gr] += ans_score
                    else:
                        group_scores.update({gr: ans_score})
                else:
                    score += ans_score

                if form.integral_evaluation.get('groups_enabled'):
                    for group in form.integral_evaluation['groups']:
                        if i in group['questions']:
                            group_scores[group['description']] += ans_score

        if form.integral_evaluation.get('script_enabled') and form.integral_evaluation.get('script'):
            try:
                results = {}
                exec(form.integral_evaluation.get('script'))
                result = results['result']
                action_name = results['action_name']
                return result, action_name, custom_params
            except Exception as e:
                log(e)

        score += form.integral_evaluation['offset']

        for res in form.integral_evaluation['results']:
            if res['value'] <= score:
                result = '{} (баллов: {})'.format(res['description'], score)
                custom_params['result'] = res['description']
                custom_params['message'] = res.get('message', None)
                custom_params['urgent'] = res.get('urgent', False)
                custom_params['score'] = score
                if contract_id is None:
                    custom_params['action'] = res.get('action', None)
                    custom_params['url'] = res.get('url', None)
                break

        if result is None:
            result = '{} балл(ов)'.format(score)

        action_name += ', результат интегральной оценки - {}'.format(result)

        category = form.integral_evaluation.get('category')
        if category != 'none' and contract_id:
            self.medsenger_api.add_record(contract_id, category, score, params={'form_id': form.id})

        if form.integral_evaluation.get('groups_enabled'):
            custom_params['group_scores'] = group_scores

            for group in form.integral_evaluation['groups']:
                category = group.get('category')
                if category != 'none' and contract_id:
                    self.medsenger_api.add_record(contract_id, category, group_scores[group['description']],
                                                  params={'form_id': form.id})
                if group_scores[group['description']] > group['value']:
                    action_name += ', сумма в группе превышает критическое значение'
                    custom_params['urgent'] = True
                    break

        return result, action_name, custom_params

    def create_or_edit(self, data, contract):
        try:
            old_names = []
            form_id = data.get('id')
            if not form_id:
                form = Form()
            else:
                form = Form.query.filter_by(id=form_id).first_or_404()

                if form.contract_id != contract.id and not contract.is_admin:
                    return None

                old_names = form.categories.split('|')

            form.title = data.get('title')
            form.doctor_description = data.get('doctor_description')
            form.patient_description = data.get('patient_description')
            form.init_text = data.get('init_text')
            form.thanks_text = data.get('thanks_text')
            form.show_button = bool(data.get('show_button'))
            form.button_title = data.get('button_title')
            form.custom_title = data.get('custom_title')
            form.custom_text = data.get('custom_text')
            form.timetable = data.get('timetable')
            form.fields = data.get('fields')
            form.has_integral_evaluation = bool(data.get('has_integral_evaluation'))
            form.integral_evaluation = data.get('integral_evaluation')
            form.template_id = data.get('template_id')
            form.warning_days = data.get('warning_days')
            form.instant_report = bool(data.get('instant_report'))
            form.categories = '|'.join(set(filter(lambda x: x, map(lambda f: f.get('category'), form.fields))))

            if data.get('is_template'):
                form.is_template = True
                form.template_category = data.get('template_category')
                if contract.is_admin:
                    form.clinics = data.get('clinics')
                    form.exclude_clinics = data.get('exclude_clinics')
                else:
                    form.doctor_id = data.get('doctor_id')
                    form.clinic_id = data.get('clinic_id')
            else:
                form.patient_id = contract.patient_id
                form.contract_id = contract.id

            if contract.is_admin:
                if data.get('algorithm_id'):
                    form.algorithm_id = data.get('algorithm_id')
                else:
                    form.algorithm_id = None

            if not form_id:
                self.db.session.add(form)
            self.__commit__()

            if not form_id and form.contract_id:
                self.db.session.refresh(form)

                if form.init_text:
                    self.medsenger_api.send_message(form.contract_id, form.init_text, only_patient=True)

                if form.timetable.get('send_on_init'):
                    self.run(form)

            if not form_id and not data.get('is_template'):
                log_action("form", "create", contract, form)

            if form_id:
                log_action("form", "edit", contract, form)

            return form
        except Exception as e:
            log(e)
            return None
